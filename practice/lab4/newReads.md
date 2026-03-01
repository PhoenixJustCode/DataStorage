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
  - Lift: 2.53 → 2.5× higher risk than average
- **Feature Comparison:**
  - Lowest churn: Two year contract (2.85%)
  - Senior citizens churn higher: 41.7% vs 23.7%
  - Paperless billing increases churn: 33.6% vs 16.4% (~17% difference)
- **Visualizations:** Saved in `....png`

---

## TASK 2: Naive Bayes Classifier

- **Data Preparation:**
  - `TotalCharges` converted to numeric, NaNs removed
  - Categorical features encoded numerically; numeric features assumed normally distributed
  - Train/Test split: 80%/20%
- **Probability Calculations:**
  - Priors: P(Churn)=0.266, P(NoChurn)=0.734
  - Conditional probabilities calculated for categorical and numerical features
- **Prediction & Evaluation (Manual NB):**
  - Accuracy: 71.6%
  - Precision: 48.0%
  - Recall: 78.9%
  - F1-score: 59.7%
  - Confusion Matrix: [[713 320], [79 295]]
  - ROC Curve saved: `plots/roc_curve.png`
- **Sklearn GaussianNB Comparison:**
  - Accuracy: 73.9%
  - Precision: 50.6%
  - Recall: 72.9%
  - F1-score: 59.8%
  - Comment: Sklearn slightly higher accuracy, F1 similar

---

## TASK 3: Business Decision Analysis

- **Expected Value of Targeting:**
  - EV = P(Churn) × CLV × success – cost
  - Max spend for P(Churn)=0.8: 0.8 × 2000 × 0.4 – 300 = 340 USD
  - Example EV for all test customers calculated

- **Risk Segmentation Matrix:**
  - High Value: MonthlyCharges > 70
  - High Risk: P(Churn) > 0.6

| Quadrant | #Customers | Expected Loss | Expected Gain |
|----------|------------|---------------|---------------|
| HV_HR    | 378        | 713,560       | 172,024       |
| HV_LR    | 340        | 69,480        | -74,208       |
| LV_HR    | 209        | 377,886       | 88,454        |
| LV_LR    | 480        | 54,545        | -122,182      |

- **Highest ROI:** HV_HR

- **Budget Optimization:**
  - Budget = 50,000 USD, cost = 300 USD → 166 customers targeted
  - Total Expected Profit = 82,651 USD
  - High Risk Coverage = 28.3%

- **Sensitivity Analysis:**
  - Success 20% → fewer expected profits, EV still positive for 166 customers
  - Cost 500 → target fewer customers
  - CLV 1,500 → EV decreases → targeting strategy shrinks
