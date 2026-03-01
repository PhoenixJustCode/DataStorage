import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, RocCurveDisplay, precision_score, recall_score, f1_score, accuracy_score
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
import os

os.makedirs("plots", exist_ok=True)

# === Load Data ===
df = pd.read_csv('dataset.xls', sep=',')
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df = df.dropna(subset=['TotalCharges'])

# === TASK 1.1 Overall Churn Probability ===
p_churn = df['Churn'].value_counts(normalize=True)['Yes']
print("P(Churn):", p_churn)

# === TASK 1.2 Conditional Probabilities ===
p_churn_month2month = df[df['Contract'] ==
                         'Month-to-month']['Churn'].value_counts(normalize=True)['Yes']
p_churn_tenure_lt12 = df[df['tenure'] < 12]['Churn'].value_counts(normalize=True)[
    'Yes']
p_churn_fiber = df[df['InternetService'] ==
                   'Fiber optic']['Churn'].value_counts(normalize=True)['Yes']
p_churn_echeck = df[df['PaymentMethod'] ==
                    'Electronic check']['Churn'].value_counts(normalize=True)['Yes']
print("P(Churn | Month-to-month):", p_churn_month2month)
print("P(Churn | tenure < 12):", p_churn_tenure_lt12)
print("P(Churn | Fiber optic):", p_churn_fiber)
print("P(Churn | Electronic check):", p_churn_echeck)

# === TASK 1.3 Joint Probability & Lift ===
p_joint = (p_churn_month2month * p_churn_fiber) / p_churn
lift = p_joint / p_churn
print("P(Churn | Month-to-month & Fiber optic):", p_joint)
print("Lift:", lift)

# === TASK 1.4 Feature Comparison ===
contract_churn = df.groupby('Contract')['Churn'].apply(
    lambda x: (x == 'Yes').mean())
senior_churn = df.groupby('SeniorCitizen')['Churn'].apply(
    lambda x: (x == 'Yes').mean())
paperless_churn = df.groupby('PaperlessBilling')[
    'Churn'].apply(lambda x: (x == 'Yes').mean())
print("Churn by Contract:\n", contract_churn)
print("Churn by SeniorCitizen:\n", senior_churn)
print("Churn by PaperlessBilling:\n", paperless_churn)

# === TASK 1.5 Visualization ===
features = ['Contract', 'InternetService',
            'PaymentMethod', 'SeniorCitizen', 'PaperlessBilling']
for f in features:
    probs = df.groupby(f)['Churn'].apply(lambda x: (x == 'Yes').mean())
    ax = probs.plot(
        kind='bar', title=f'Churn Probability by {f}', figsize=(6, 4))
    plt.ylabel('Churn Probability')
    plt.tight_layout()
    plt.savefig(f'plots/churn_by_{f}.png')
    plt.close()

# === TASK 2.1 Data Preparation ===
X = df.drop(columns=['customerID', 'Churn'])
y = df['Churn'].map({'Yes': 1, 'No': 0})
for c in X.select_dtypes(include='object').columns:
    X[c] = X[c].astype('category').cat.codes

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
categorical_cols = [c for c in X_train.columns if str(
    X_train[c].dtype) in ['int8', 'int16', 'int32']]
numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']

# === TASK 2.2 Probability Calculations ===
priors = {1: y_train.mean(), 0: 1-y_train.mean()}
feature_probs = {}
for col in categorical_cols:
    feature_probs[col] = {}
    for val in X_train[col].unique():
        feature_probs[col][val] = {}
        for cls in [0, 1]:
            feature_probs[col][val][cls] = ((X_train[col] == val) & (
                y_train == cls)).sum() / (y_train == cls).sum()

numerical_stats = {}
for col in numerical_cols:
    numerical_stats[col] = {}
    for cls in [0, 1]:
        vals = X_train[y_train == cls][col]
        numerical_stats[col][cls] = (vals.mean(), vals.std())


def gaussian_prob(x, mean, std):
    return (1/(np.sqrt(2*np.pi)*std)) * np.exp(-(x-mean)**2/(2*std**2))


def nb_predict_proba(X):
    probs = []
    for idx, row in X.iterrows():
        p = {}
        for cls in [0, 1]:
            likelihood = priors[cls]
            for col in categorical_cols:
                likelihood *= feature_probs[col].get(
                    row[col], {0: 1e-6, 1: 1e-6})[cls]
            for col in numerical_cols:
                mean, std = numerical_stats[col][cls]
                likelihood *= gaussian_prob(row[col], mean, std)
            p[cls] = likelihood
        total = p[0]+p[1]
        probs.append(p[1]/total)
    return np.array(probs)


# === TASK 2.3 Prediction & Evaluation ===
y_pred_prob = nb_predict_proba(X_test)
y_pred = (y_pred_prob > 0.5).astype(int)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1-score:", f1_score(y_test, y_pred))
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:\n", cm)

plt.figure(figsize=(6, 4))
RocCurveDisplay.from_predictions(y_test, y_pred_prob)
plt.title('ROC Curve')
plt.tight_layout()
plt.savefig('plots/roc_curve.png')
plt.close()

# === TASK 2.5 Sklearn Naive Bayes Comparison ===
gnb = GaussianNB()
gnb.fit(X_train, y_train)
y_pred_gnb = gnb.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred_gnb))
print("Precision:", precision_score(y_test, y_pred_gnb))
print("Recall:", recall_score(y_test, y_pred_gnb))
print("F1-score:", f1_score(y_test, y_pred_gnb))

# === TASK 3.1 Expected Value of Targeting ===
CLV = 2000
cost = 300
success = 0.4
ev_test = y_pred_prob * CLV * success - cost
print("Example EV for all test customers calculated.")

# === TASK 3.2 Risk Segmentation Matrix ===
high_value = X_test['MonthlyCharges'] > 70
high_risk = pd.Series(y_pred_prob > 0.6, index=X_test.index)

quadrants = {
    'HV_HR': high_value & high_risk,
    'HV_LR': high_value & ~high_risk,
    'LV_HR': ~high_value & high_risk,
    'LV_LR': ~high_value & ~high_risk
}

for k, v in quadrants.items():
    n = v.sum()
    expected_loss = (y_pred_prob[v] * CLV).sum()
    expected_gain = (y_pred_prob[v] * CLV * success - cost).sum()
    print(k, "Num Customers:", n, "Expected Loss:",
          expected_loss, "Expected Gain:", expected_gain)

# === TASK 3.3 Budget Optimization ===
ev_sorted = pd.Series(ev_test, index=X_test.index).sort_values(ascending=False)
ev_sorted = ev_sorted[ev_sorted > 0]
budget = 50000
num_targeted = min(budget//cost, len(ev_sorted))
target_indices = ev_sorted.index[:num_targeted]
expected_profit = ev_sorted.iloc[:num_targeted].sum()
high_risk_covered = high_risk[target_indices].sum()/high_risk.sum()
print("Num Targeted:", num_targeted, "Expected Profit:",
      expected_profit, "High Risk Coverage:", high_risk_covered)

# === TASK 3.4 Sensitivity Analysis ===
success_scenarios = [0.2, 0.4]
cost_scenarios = [300, 500]
CLV_scenarios = [1500, 2000]
for s in success_scenarios:
    for cst in cost_scenarios:
        for clv_val in CLV_scenarios:
            ev_alt = y_pred_prob * clv_val * s - cst
            ev_alt_sorted = pd.Series(
                ev_alt, index=X_test.index).sort_values(ascending=False)
            ev_alt_sorted = ev_alt_sorted[ev_alt_sorted > 0]
            num_target = min(budget//cst, len(ev_alt_sorted))
            total_ev = ev_alt_sorted.iloc[:num_target].sum()
            print("Success:", s, "Cost:", cst, "CLV:", clv_val,
                  "Num Targeted:", num_target, "Total EV:", total_ev)
