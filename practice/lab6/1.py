# ==============================
# Regression Analysis
# California Housing Dataset
# ==============================

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


# ==============================
# 1. Load Dataset
# ==============================

housing = fetch_california_housing()

df = pd.DataFrame(housing.data, columns=housing.feature_names)
df["MedHouseVal"] = housing.target

print(df.head())


# ==============================
# 2. Exploratory Data Analysis
# ==============================

# Summary statistics
print(df.describe())

# Histograms
df.hist(figsize=(12, 10), bins=30)
plt.tight_layout()
plt.show()

# Correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()


# ==============================
# 3. Multiple Linear Regression
# ==============================

X = df.drop("MedHouseVal", axis=1)
y = df["MedHouseVal"]

# Add constant for statsmodels
X_const = sm.add_constant(X)

model = sm.OLS(y, X_const).fit()
print(model.summary())


# ==============================
# 4. VIF (Multicollinearity)
# ==============================

vif_data = pd.DataFrame()
vif_data["Feature"] = X_const.columns
vif_data["VIF"] = [
    variance_inflation_factor(X_const.values, i)
    for i in range(X_const.shape[1])
]

print("\nVIF values:")
print(vif_data)


# ==============================
# 5. Model Refinement
# ==============================

# Remove AveBedrms (high correlation with AveRooms)

X_refined = df.drop(["MedHouseVal", "AveBedrms"], axis=1)
X_refined_const = sm.add_constant(X_refined)

model_refined = sm.OLS(y, X_refined_const).fit()

print("\nRefined model:")
print(model_refined.summary())


# ==============================
# 6. Residual Analysis
# ==============================

residuals = model_refined.resid

plt.scatter(model_refined.fittedvalues, residuals)
plt.axhline(0)
plt.title("Residuals vs Fitted")
plt.show()

sns.histplot(residuals, kde=True)
plt.title("Residual Distribution")
plt.show()


# ==============================
# 7. Train/Test Prediction
# ==============================

X = df.drop("MedHouseVal", axis=1)
y = df["MedHouseVal"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\nTest R2:", r2)
print("Test RMSE:", rmse)
