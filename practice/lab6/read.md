# Regression Analysis – California Housing

## Dataset

We used the California Housing dataset from sklearn.

Target variable:
MedHouseVal – median house value.

Predictors:
- MedInc
- HouseAge
- AveRooms
- AveBedrms
- Population
- AveOccup
- Latitude
- Longitude

---

# 1. Exploratory Data Analysis

First, we explored the dataset using summary statistics, histograms, and correlation matrix.

Key findings:

- Median income has the strongest correlation with house prices.
- Population and occupancy variables contain some outliers.
- Housing price distribution is slightly right-skewed.

---

# 2. Multiple Linear Regression

We built a multiple linear regression model using all predictors.

The model achieved:

R² ≈ 0.60 – 0.64

This means the model explains around 60% of the variation in housing prices.

---

# 3. Multicollinearity (VIF)

We checked Variance Inflation Factor (VIF).

Result:
AveRooms and AveBedrms showed high multicollinearity.

Reason:
Bedrooms are part of total rooms.

Therefore, AveBedrms was removed from the refined model.

---

# 4. Residual Analysis

Residual plots showed:

- Residuals are centered around zero
- Distribution is approximately normal
- No strong patterns

This suggests regression assumptions are reasonably satisfied.

---

# 5. Prediction

We used an 80/20 train-test split.

Evaluation metrics:

Test R² ≈ 0.60  
RMSE ≈ 0.7

This means the model predicts house prices with moderate accuracy.

---

# Conclusion

- Median income is the strongest predictor of house prices.
- Geographic location also plays an important role.
- Removing multicollinearity improved model stability.
- The model explains about 60% of housing price variation.