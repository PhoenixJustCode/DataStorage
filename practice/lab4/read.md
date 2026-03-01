# Telco Customer Churn Analysis

## TASK 1: Exploratory Probability Analysis

- **Overall Churn Probability:** 26.6%
- **Conditional Probabilities:**
  - Month-to-month contract: 42.7%
  - Tenure < 12 months: 48.5%
  - Fiber optic internet: 41.9%
  - Electronic check payment: 45.3%
- **Joint Probability & Lift:**
  - Month-to-month + Fiber optic: 67.3%
  - Lift: 2.53 (risk 2.5× higher than average)
- **Feature Comparison:**
  - Lowest churn: Two year contract (2.85%)
  - Senior citizens (1) churn higher (41.7% vs 23.7%)
  - Paperless billing increases churn (33.6% vs 16.4%)
- **Visualizations:** Saved in `in png`

---

## TASK 2: Naive Bayes Classifier

- **Manual Naive Bayes:**
  - Accuracy: 71.6%
  - Precision: 48.0%
  - Recall: 78.9%
  - F1-score: 59.7%
- **Sklearn GaussianNB:**
  - Accuracy: 73.9%
  - Precision: 50.6%
  - Recall: 72.9%
  - F1-score: 59.8%
- ROC Curve: Saved in `roc_curve.png`

---

## TASK 3: Business Decision Analysis

- **Expected Value (EV):**
  - Max spend for P(Churn)=0.8: $340
- **Risk Segmentation Matrix:**

| Quadrant | #Customers | Expected Loss | Expected Gain |
|----------|------------|---------------|---------------|
| HV_HR    | 378        | $713,560      | $172,024      |
| HV_LR    | 340        | $69,480       | -$74,208      |
| LV_HR    | 209        | $377,886      | $88,454       |
| LV_LR    | 480        | $54,545       | -$122,182     |

- **Highest ROI:** HV_HR
- **Budget Optimization:**
  - Budget: $50,000 → Target 166 customers
  - Total Expected Profit: $82,651
  - High Risk Coverage: 28.3%
- **Sensitivity Analysis:**
  - Success 20% → EV drops
  - Cost $500 → fewer customers targeted
  - CLV $1,500 → EV drops → strategy adjusted
