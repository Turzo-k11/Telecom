# Model card — Mobile subscriber churn (demo)

**Purpose:** Illustrate a predictive retention workflow for a fictional Swedish telecom company.

**Training data:** 8,000 synthetic rows generated from assumed statistical relationships; no actual subscribers or information from Telia, Tele2, or Comviq.

**Target:** `churn_next_90d` is a simulated binary outcome.

**Features:** Age, region, subscription tier, customer tenure, monthly price, usage, support tickets, complaint, network satisfaction, autopay, competitor offer and contract terms. The customer ID is excluded.

**Selection:** Compare Logistic Regression and Random Forest using stratified three-fold CV on the 75% train set, select by ROC-AUC, then score the untouched 25% test set.

**Classification threshold:** 0.25 (illustration, not business-calibrated). Model performance in `reports/model_metrics.json`.

**Risks and limitations:** Synthetic labels, assumed churn process, no external validation, potential privacy and fairness issues, possible false-positive contact, and no validated cost-benefit analysis. Do not use to make real customer decisions.
