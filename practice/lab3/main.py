import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import os

df = pd.read_csv("movies.csv")

os.makedirs("plots", exist_ok=True)

# task 1.1 Initial Exploration

print("Dataset shape:", df.shape)
print("\nMissing values:")
print(df.isna().sum())
print("\nData types:")
print(df.dtypes)

# task 1.2 Handling Missing Data

df['budget'] = df['budget'].fillna(df['budget'].median())
df['gross'] = df['gross'].fillna(df['gross'].median())
df['runtime'] = df['runtime'].fillna(df['runtime'].median())
df['score'] = df['score'].fillna(df['score'].median())
df['votes'] = df['votes'].fillna(df['votes'].median())

print("\nMissing values after filling:")
print(df[['budget','gross','runtime','score','votes']].isna().sum())

# task 1.3 Data Validation

df = df[(df['budget'] >= 0) & (df['gross'] >= 0) & (df['runtime'] >= 10)]

df['profit'] = df['gross'] - df['budget']
print("\nUnprofitable movies:", df[df['profit'] < 0].shape[0])

def iqr_outliers(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return series[(series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)]

# task 2.1 Numerical Summary

num_cols = ['budget','gross','runtime','score','votes']

summary = pd.DataFrame(index=num_cols)
summary['mean'] = df[num_cols].mean()
summary['median'] = df[num_cols].median()
summary['mode'] = df[num_cols].mode().iloc[0]
summary['range'] = df[num_cols].max() - df[num_cols].min()
summary['variance'] = df[num_cols].var()
summary['std_dev'] = df[num_cols].std()
summary['IQR'] = df[num_cols].quantile(0.75) - df[num_cols].quantile(0.25)

print("\nNumerical summary:")
print(summary)

print("\nFive-number summary:")
print(df[num_cols].describe().loc[['min','25%','50%','75%','max']])

# task 2.2 Categorical Summary

cat_cols = ['genre','director','star']

for col in cat_cols:
    print(f"\n{col.upper()}")
    print("Unique values:", df[col].nunique())
    print("Top 10:")
    print(df[col].value_counts().head(10))
    print("Percentages:")
    print(df[col].value_counts(normalize=True).head(10) * 100)

# task 2.3 Statistical Interpretation

cv = summary['std_dev'] / summary['mean']
print("\nCoefficient of variation:")
print(cv.sort_values(ascending=False))

skewness = 3 * (summary['mean'] - summary['median']) / summary['std_dev']
print("\nSkewness:")
print(skewness)

# task 3.1 Distribution Visualization

fig, axes = plt.subplots(2, 5, figsize=(25, 10))

for i, col in enumerate(num_cols):
    sns.histplot(df[col], kde=True, ax=axes[0, i])
    axes[0, i].axvline(df[col].mean(), color='red')
    axes[0, i].axvline(df[col].median(), color='green')
    axes[0, i].set_title(f"Histogram of {col}")

    sns.boxplot(x=df[col], ax=axes[1, i])
    axes[1, i].set_title(f"Boxplot of {col}")

plt.tight_layout()
plt.savefig("plots/numerical_distributions.png")
plt.close()

# task 3.2 Outlier Analysis

outliers_budget = iqr_outliers(df['budget'])
outliers_gross = iqr_outliers(df['gross'])
outliers_votes = iqr_outliers(df['votes'])

outlier_mask = (
    df['budget'].isin(outliers_budget) |
    df['gross'].isin(outliers_gross) |
    df['votes'].isin(outliers_votes)
)

outliers_df = df[outlier_mask]

print("\nOutlier movies count:", outliers_df.shape[0])
print("Revenue share from outliers (%):",
      outliers_df['gross'].sum() / df['gross'].sum() * 100)

print("\nExample outliers:")
print(outliers_df[['name','budget','gross','votes']].head())

# task 3.3 Normality Assessment

plt.figure(figsize=(6,6))
stats.probplot(df['score'], plot=plt)
plt.title("Q-Q Plot IMDb Score")
plt.savefig("plots/qqplot_imdb_score.png")
plt.close()

mean = df['score'].mean()
std = df['score'].std()

within_1 = df[(df['score'] >= mean-std) & (df['score'] <= mean+std)].shape[0] / len(df) * 100
within_2 = df[(df['score'] >= mean-2*std) & (df['score'] <= mean+2*std)].shape[0] / len(df) * 100
within_3 = df[(df['score'] >= mean-3*std) & (df['score'] <= mean+3*std)].shape[0] / len(df) * 100

print("\nNormality check (IMDb score):")
print("Within 1 SD:", within_1)
print("Within 2 SD:", within_2)
print("Within 3 SD:", within_3)

# task 4.1 Correlation Analysis

numerical_cols = ['budget', 'gross', 'runtime', 'score', 'votes', 'profit']

corr_matrix = df[numerical_cols].corr()
print("\nCorrelation matrix:")
print(corr_matrix)

strong_positive = corr_matrix[(corr_matrix > 0.7) & (corr_matrix < 1.0)]
strong_negative = corr_matrix[corr_matrix < -0.3]

print("\nStrong positive correlations (> 0.7):")
print(strong_positive.dropna(how='all').dropna(axis=1, how='all'))

print("\nStrong negative correlations (< -0.3):")
print(strong_negative.dropna(how='all').dropna(axis=1, how='all'))

print("\n note:")
print("Budget and gross have strong positive correlation — expected.")
print("Weak correlation between score and profit — rating does not guarantee profitability.")

# task 4.2 Scatter Plot Matrix

scatter_cols = ['budget', 'gross', 'score', 'votes']

sns.pairplot(
    df,
    vars=scatter_cols,
    hue='genre',
    diag_kind='kde',
    plot_kws={'alpha': 0.5}
)

plt.gcf().set_size_inches(12, 10)
plt.savefig("plots/scatter_matrix_budget_gross_score_votes.png")
plt.close()

# task 4.3 Advanced Relationship Analysis

df['profit_margin'] = np.where(
    df['budget'] == 0,
    np.nan,
    (df['gross'] - df['budget']) / df['budget']
)

print("\nInfinite profit margin explanation:")
print("If budget is zero, profit margin is undefined (division by zero).")
print("Such cases are excluded from profit margin analysis.")

pm_corr = df[['profit_margin', 'score']].corr().iloc[0,1]
print("\nCorrelation between profit margin and IMDb score:", pm_corr)

plt.figure(figsize=(8,6))
sns.scatterplot(
    data=df,
    x='score',
    y='profit_margin',
    alpha=0.5
)
plt.yscale('symlog')
plt.title("Profit Margin vs IMDb Score")
plt.savefig("plots/profit_margin_vs_score.png")
plt.close()

# task 5.1 Genre Comparison

plt.figure(figsize=(10,6))
sns.boxplot(data=df, x='genre', y='budget')
plt.xticks(rotation=45)
plt.title("Budget by Genre")
plt.savefig("plots/budget_by_genre.png")
plt.close()

plt.figure(figsize=(10,6))
sns.boxplot(data=df, x='genre', y='gross')
plt.xticks(rotation=45)
plt.title("Revenue by Genre")
plt.savefig("plots/revenue_by_genre.png")
plt.close()

plt.figure(figsize=(10,6))
sns.violinplot(data=df, x='genre', y='score')
plt.xticks(rotation=45)
plt.title("IMDb Rating Distribution by Genre")
plt.savefig("plots/imdb_by_genre_violin.png")
plt.close()

genre_profit = df.groupby('genre')['profit_margin'].mean()
print("\nAverage profit margin by genre:")
print(genre_profit)

print("\nGenre with highest median budget:")
print(df.groupby('genre')['budget'].median().idxmax())

print("\nMost consistent ratings (lowest SD):")
print(df.groupby('genre')['score'].std().idxmin())

print("\nGenre overperformance insight:")
print("Genres with lower budgets but high profit margins indicate strong overperformance.")

# task 5.2 Time Trend Analysis

budget_year = df.groupby('year')['budget'].mean().rolling(3).mean()
score_year = df.groupby('year')['score'].mean()

plt.figure(figsize=(10,6))
plt.plot(budget_year)
plt.title("Average Budget Over Time (3-year MA)")
plt.xlabel("Year")
plt.ylabel("Budget")
plt.savefig("plots/budget_trend.png")
plt.close()

plt.figure(figsize=(10,6))
plt.plot(score_year)
plt.title("Average IMDb Score Over Time")
plt.xlabel("Year")
plt.ylabel("IMDb Score")
plt.savefig("plots/imdb_trend.png")
plt.close()

print("\nMovie quality over time:")
print("IMDb scores remain relatively stable with slight decline in recent years.")

# task 5.3 Director Analysis

top_directors = df['director'].value_counts().head(10).index

director_stats = df[df['director'].isin(top_directors)].groupby('director').agg(
    movies_count=('name', 'count'),
    avg_score=('score', 'mean'),
    avg_profit_margin=('profit_margin', 'mean')
)

print("\nTop 10 directors analysis:")
print(director_stats)
