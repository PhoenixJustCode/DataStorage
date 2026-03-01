import pandas as pd
import matplotlib.pyplot as plt

# 1) Load dataset
# Put StudentsPerformance.csv in the same folder as this notebook/script
df = pd.read_csv("student_data.csv")

# 2) Explore dataset
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\n--- First 5 rows ---")
print(df.head())

print("\n--- Info ---")
print(df.info())

print("\n--- Missing values ---")
print(df.isna().sum())

print("\n--- Numeric summary ---")
print(df.describe())

# 3) Find most correlated columns (numeric only)
num_cols = df.select_dtypes(include="number")
corr = num_cols.corr(numeric_only=True)

# Get the highest correlation pair (excluding diagonal)
corr_pairs = (
    corr.where(~(corr == 1.0))      # remove 1.0 diagonal
        .stack()
        .reset_index()
)
corr_pairs.columns = ["col1", "col2", "corr"]

# Because (A,B) and (B,A) both exist, keep only one ordering
corr_pairs["pair"] = corr_pairs.apply(
    lambda r: tuple(sorted([r["col1"], r["col2"]])), axis=1)
corr_pairs = corr_pairs.drop_duplicates("pair").drop(columns=["pair"])

top_pair = corr_pairs.sort_values("corr", ascending=False).iloc[0]
print("\n--- Most correlated numeric columns ---")
print(top_pair)

# 4) One meaningful visualization
x_col, y_col = top_pair["col1"], top_pair["col2"]

plt.figure(figsize=(7, 5))
plt.scatter(df[x_col], df[y_col])
plt.title(f"{x_col} vs {y_col} (corr={top_pair['corr']:.3f})")
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True, alpha=0.3)
plt.show()

# 5) One-paragraph insight (auto-generated)
insight = (
    f"In the StudentsPerformance dataset, the strongest linear relationship among numeric columns "
    f"is between '{x_col}' and '{y_col}' (correlation ≈ {top_pair['corr']:.3f}). "
    f"The scatter plot shows that students who score higher in '{x_col}' tend to also score higher "
    f"in '{y_col}', suggesting these skills/subjects are closely related or influenced by similar factors "
    f"(e.g., study habits, reading comprehension, or overall academic performance). "
    f"This insight can be useful for identifying which areas improve together and where targeted support might help."
)
print("\n--- One-paragraph insight ---")
print(insight)
