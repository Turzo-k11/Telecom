# Build the Power BI dashboard (Desktop)

> This project provides data, a theme, measures and an interactive standalone HTML dashboard; **it does not contain an edited `.pbix` file**. Power BI Desktop is needed to create a `.pbix`.

1. Open Power BI Desktop → **Get data → Text/CSV**. Import `../data/synthetic_mobile_subscribers.csv`, using UTF-8 and comma delimiter. Rename the table to `Subscribers`.
2. **Transform Data** and set `monthly_fee_sek` / `tenure_months` / `support_tickets_90d` / `churn_next_90d` to Whole number, `data_usage_gb` to Decimal number, and the categorical columns to Text. Click **Close & Apply**.
3. Go to **View → Themes → Browse for themes** and select `theme.json`.
4. Go to **Modeling → New measure** and create the measures one by one from `DAX_measures.dax` (each line is a separate measure definition). Format churn rates as Percentage, revenue as Currency (SEK), and customers as whole numbers.
5. Page 1 **Executive overview**: four card visuals with `Customers`, `Monthly Revenue (SEK)`, `Churn Rate 90d`, `Average Revenue per User (SEK)`. Add slicers for `plan`, `region`, `contract_type`.
6. Add a clustered column chart: `region` axis, `Monthly Revenue (SEK)` value. Add another bar chart: `plan` axis, `Churn Rate 90d` value. Add a bar chart: `network_satisfaction` axis, `Churn Rate 90d` value.
7. Page 2 **Retention & service**: chart of `support_tickets_90d` vs `Churn Rate 90d`; matrix rows = `plan`, columns = `contract_type`, values = `Customers`, `Churn Rate 90d`.
8. Page 3 **Model**: add explanatory text and static model metrics from `../reports/model_metrics.json`: ROC-AUC 0.7286; precision 0.3486; recall 0.2992; F1 0.3220. Do not portray these as filter-sensitive measures.
9. Save as `Swedish_Telecom_Analytics.pbix`. Export screenshots for your GitHub README if desired.

**Interpretation:** churn represents a modeled 90-day outcome in synthetic data. Subscription revenue is a cross-sectional monthly amount. Do not multiply churn by 4 and call it a forecast without modeling timing, cohorts, acquisitions, and changes. `MRR Associated with Churn` is not realized loss.
