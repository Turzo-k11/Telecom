"""Reproducible telecom portfolio analysis on synthetic Swedish mobile subscribers."""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, confusion_matrix, RocCurveDisplay
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]

def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-30,30)))

def generate(n=8000, seed=42):
    rng=np.random.default_rng(seed)
    plans=np.array(['Bas 5 GB','Plus 20 GB','Premium Fri surf'])
    plan=rng.choice(plans,n,p=[.37,.42,.21])
    base=pd.Series(plan).map({'Bas 5 GB':149,'Plus 20 GB':249,'Premium Fri surf':349}).to_numpy()
    tenure=rng.integers(1,73,n)
    region=rng.choice(['Stockholm','Göteborg','Malmö','Övriga Sverige'],n,p=[.31,.17,.12,.40])
    age=rng.integers(18,76,n)
    discount=rng.choice([0,25,50,75],n,p=[.63,.16,.14,.07])
    monthly=(base-discount).astype(int)
    data_use=np.maximum(0,rng.normal(np.select([plan==plans[0],plan==plans[1]],[4,15],default=36),[3 if a==plans[0] else 8 if a==plans[1] else 18 for a in plan])).round(1)
    support=rng.poisson(.38,n)+rng.binomial(1,.10,n)
    complaints=rng.binomial(1,sigmoid(-2.8+.48*support),n)
    network=rng.choice(['Mycket nöjd','Nöjd','Missnöjd'],n,p=[.25,.58,.17])
    autopay=rng.binomial(1,.67,n)
    competitor_offer=rng.binomial(1,.25,n)
    binding=rng.choice(['Ingen bindning','12 månader','24 månader'],n,p=[.55,.30,.15])
    # Synthetic behavioral assumptions: NOT estimates of actual Swedish operators.
    logit=(-1.85 + .95*(network=='Missnöjd')-.40*(network=='Mycket nöjd')
           +.55*complaints+.23*support+.8*competitor_offer-.43*autopay
           -.018*tenure+.42*(binding=='Ingen bindning')-.36*(binding=='24 månader')
           +.003*(monthly-230)+.22*(data_use>38))
    churn=rng.binomial(1,sigmoid(logit))
    df=pd.DataFrame({'customer_id':[f'MOB{i:06d}' for i in range(1,n+1)],'age':age,
         'region':region,'plan':plan,'tenure_months':tenure,'monthly_fee_sek':monthly,
         'data_usage_gb':data_use,'support_tickets_90d':support,'complaint_90d':complaints,
         'network_satisfaction':network,'autopay':autopay,'competitor_offer_seen':competitor_offer,
         'contract_type':binding,'churn_next_90d':churn})
    return df

def build_model(df, seed=42):
    target='churn_next_90d'; exclude=['customer_id',target]
    X=df.drop(columns=exclude); y=df[target]
    cat=X.select_dtypes(include='object').columns.tolist()
    nums=X.columns.difference(cat).tolist()
    preprocessing=ColumnTransformer([
        ('numeric',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),
        ('categorical',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cat)])
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,stratify=y,random_state=seed)
    options={'Logistic Regression':LogisticRegression(max_iter=1500,random_state=seed),
             'Random Forest':RandomForestClassifier(n_estimators=180,min_samples_leaf=12,random_state=seed,n_jobs=-1)}
    cv=StratifiedKFold(n_splits=3,shuffle=True,random_state=seed)
    comparison={}; pipelines={}
    for name,model in options.items():
        pipe=Pipeline([('preprocessor',preprocessing),('model',model)])
        scores=cross_validate(pipe,Xtr,ytr,cv=cv,scoring={'roc_auc':'roc_auc','average_precision':'average_precision'},n_jobs=1)
        comparison[name]={'cv_roc_auc_mean':round(float(scores['test_roc_auc'].mean()),4),
                          'cv_average_precision_mean':round(float(scores['test_average_precision'].mean()),4)}
        pipelines[name]=pipe
    best=max(comparison,key=lambda k:comparison[k]['cv_roc_auc_mean'])
    pipe=pipelines[best].fit(Xtr,ytr)
    proba=pipe.predict_proba(Xte)[:,1]
    pred=(proba>=.25).astype(int)
    metrics={'best_model':best,'train_rows':len(Xtr),'test_rows':len(Xte),'threshold':.25,
             'roc_auc':round(float(roc_auc_score(yte,proba)),4),
             'average_precision':round(float(average_precision_score(yte,proba)),4),
             'precision':round(float(precision_score(yte,pred,zero_division=0)),4),
             'recall':round(float(recall_score(yte,pred,zero_division=0)),4),
             'f1':round(float(f1_score(yte,pred,zero_division=0)),4),
             'confusion_matrix':confusion_matrix(yte,pred).tolist(), 'cross_validation':comparison}
    return pipe,metrics,yte,proba

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rows',type=int,default=8000);args=parser.parse_args()
    for part in ['data','figures','reports']:(ROOT/part).mkdir(exist_ok=True)
    df=generate(n=args.rows);df.to_csv(ROOT/'data/synthetic_mobile_subscribers.csv',index=False)
    summary={'customers':len(df),'churn_rate_pct':round(100*df.churn_next_90d.mean(),2),
             'monthly_recurring_revenue_sek':int(df.monthly_fee_sek.sum()),
             'annualized_revenue_sek':int(12*df.monthly_fee_sek.sum()),
             'average_revenue_per_customer_sek':round(float(df.monthly_fee_sek.mean()),2),
             'potential_monthly_revenue_at_risk_sek':int(df.loc[df.churn_next_90d==1,'monthly_fee_sek'].sum())}
    (ROOT/'reports/kpis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    segments=df.groupby('plan').agg(customers=('customer_id','count'),churn_rate=('churn_next_90d','mean'),monthly_revenue_sek=('monthly_fee_sek','sum')).reset_index()
    segments['churn_rate_pct']=(segments.pop('churn_rate')*100).round(2)
    segments.to_csv(ROOT/'reports/plan_segments.csv',index=False)
    pipe,metrics,yte,proba=build_model(df)
    (ROOT/'reports/model_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.style.use('ggplot')
    fig,ax=plt.subplots(figsize=(8,5));ax.bar(segments['plan'],segments['churn_rate_pct']);ax.set_ylabel('Churn nästa 90 dagar (%)');ax.set_title('Simulerad churn per abonnemang');fig.tight_layout();fig.savefig(ROOT/'figures/churn_by_plan.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5));region=df.groupby('region')['monthly_fee_sek'].sum().sort_values();ax.barh(region.index,region.values);ax.set_xlabel('Månadsintäkt (SEK)');ax.set_title('Simulerad omsättning per region');fig.tight_layout();fig.savefig(ROOT/'figures/revenue_by_region.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,5));RocCurveDisplay.from_predictions(yte,proba,ax=ax);ax.set_title(f'ROC-kurva – {metrics["best_model"]}');fig.tight_layout();fig.savefig(ROOT/'figures/roc_curve.png',dpi=160);plt.close(fig)
    print('KPI:',summary);print('MODEL:',metrics)

if __name__=='__main__':main()
