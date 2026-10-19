# Business Analysis — Swedish Telecom (Synthetic)

## Executive summary

This independent case study analyzes **8,000 fictional subscribers** in a Swedish-style mobile subscription business. The synthetic customer snapshot totals **SEK 1,725,975 in monthly subscription fees** (an average **SEK 215.75 per customer per month**). The 90-day churn label is positive for **12.72%** of the dataset. These are **not** performance claims about Telia, Tele2, Comviq, or any other real operator.

## Findings by subscription tier

| Subscription | Customers | Churn next 90 days | Monthly fees |
|---|---:|---:|---:|
| Premium Fri surf | 1,656 | 19.57% | 551,994 SEK |
| Plus 20 GB | 3,336 | 12.38% | 774,339 SEK |
| Bas 5 GB | 3,008 | 9.34% | 399,642 SEK |

The **Premium Fri surf** tier has the highest churn proportion in this synthetic sample, but its higher monthly fee also means it contributes substantial recurring subscription revenue. The observed differences are associations, not evidence that the plan itself causes churn.

## Machine-learning analysis

The project compares Logistic Regression with Random Forest using a held-out test set. **Logistic Regression** performs better by cross-validated ROC-AUC in this run. On the test sample: **ROC-AUC 0.7286**, **precision 0.3486**, **recall 0.2992**, **F1 0.3220** at a **0.25** classification threshold. Thus the model does **not** identify every leaving customer; intervention must be tested rather than assumed successful.

## Recommended business experiments

1. **Premium retention pilot:** test an opt-in service review for a randomized group of premium subscribers with high estimated churn risk. Compare actual 90-day retention with a control group.
2. **Customer-service triage:** offer proactive troubleshooting after repeated support contacts. Track post-contact churn, customer satisfaction, complaint resolution and cost.
3. **Contract and pricing review:** analyze customer sentiment and renewal reasons with additional real-world data before changing commercial terms.
4. **Decision quality:** calibrate churn probabilities, evaluate precision-recall tradeoffs, document fairness and privacy constraints, and measure **uplift** / incremental retention rather than relying only on prediction accuracy.

## KPI and financial caveats

- Monthly fees are an approximate **MRR proxy**, not audited recognized revenue or actual cash collections.
- The `churn_next_90d` label is a synthetic future outcome. Revenue associated with churn-labeled customers is **exposure**, not proven lost revenue.
- Data is cross-sectional, with no historical transactions or customer acquisition events. This project cannot establish true monthly churn trends, lifetime value, causal drivers or intervention ROI.
- A real telco implementation would need governance, customer consent/legal basis, security controls, and bias audits.

## How to reproduce

Run `python -m src.analysis` from repository root to regenerate core analytical outputs; open `dashboard/index.html` locally for an interactive stakeholder dashboard. The Power BI build recipe is in `powerbi/POWER_BI_GUIDE.md`.
