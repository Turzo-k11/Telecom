from src.analysis import generate,build_model

def test_generation():
    df=generate(120,42)
    assert len(df)==120
    assert df.customer_id.is_unique
    assert df.churn_next_90d.isin([0,1]).all()
    assert (df.monthly_fee_sek>0).all()

def test_reproducible():
    assert generate(20,42).equals(generate(20,42))

def test_model():
    df=generate(400,42)
    _,m,_,_=build_model(df)
    assert 0<=m['roc_auc']<=1
    assert m['train_rows']+m['test_rows']==400
