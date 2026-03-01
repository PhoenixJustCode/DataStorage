import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
from scipy import stats

# --------------------------
# 1. Генерация датасета
# --------------------------
np.random.seed(42)
n = 10000

# Группы
group = np.random.choice(['A', 'B'], size=n, p=[0.5, 0.5])

# Конверсии
conv_rate_A = 0.05
conv_rate_B = 0.065  # +1.5% absolute

converted = np.where(
    group == 'A',
    np.random.binomial(1, conv_rate_A, n),
    np.random.binomial(1, conv_rate_B, n)
)

# Время на сайте
time_A = np.random.normal(120, 30, n)
time_B = np.random.normal(130, 35, n)
time_on_site = np.where(group == 'A', time_A, time_B)
time_on_site = np.clip(time_on_site, 0, None)  # не может быть отрицательным

# Кол-во просмотренных страниц
pages_A = np.random.poisson(4, n)
pages_B = np.random.poisson(4.3, n)
pages_viewed = np.where(group == 'A', pages_A, pages_B)

# DataFrame
df = pd.DataFrame({
    'visitor_id': range(1, n+1),
    'group': group,
    'converted': converted,
    'time_on_site': time_on_site,
    'pages_viewed': pages_viewed
})

# --------------------------
# 2. A/B анализ
# --------------------------

# --- Conversion Rate (двухпропорционный z-тест) ---
successes = df.groupby('group')['converted'].sum().values
nobs = df.groupby('group')['converted'].count().values

# H0: p_B <= p_A, H1: p_B > p_A (one-tailed)
z_stat, p_val = proportions_ztest(
    count=successes, nobs=nobs, alternative='larger')
print("Conversion Rate Test:")
print(f"  Control A: {successes[0]}/{nobs[0]} = {successes[0]/nobs[0]:.3f}")
print(f"  Treatment B: {successes[1]}/{nobs[1]} = {successes[1]/nobs[1]:.3f}")
print(f"  z-stat: {z_stat:.3f}, p-value (one-tailed): {p_val:.3f}\n")

# --- Time on Site (t-тест для независимых выборок) ---
time_A = df[df['group'] == 'A']['time_on_site']
time_B = df[df['group'] == 'B']['time_on_site']

# Проверим нормальность (Shapiro) - можно для больших n пропустить
# stats.shapiro(time_A.sample(500))  # пример

# H0: mean_B <= mean_A, H1: mean_B > mean_A
t_stat, p_val = stats.ttest_ind(time_B, time_A, alternative='greater')
print("Time on Site Test:")
print(f"  Mean A: {time_A.mean():.2f}, Mean B: {time_B.mean():.2f}")
print(f"  t-stat: {t_stat:.3f}, p-value (one-tailed): {p_val:.3f}\n")

# --- Pages Viewed (t-тест для независимых выборок) ---
pages_A = df[df['group'] == 'A']['pages_viewed']
pages_B = df[df['group'] == 'B']['pages_viewed']

t_stat, p_val = stats.ttest_ind(pages_B, pages_A, alternative='greater')
print("Pages Viewed Test:")
print(f"  Mean A: {pages_A.mean():.2f}, Mean B: {pages_B.mean():.2f}")
print(f"  t-stat: {t_stat:.3f}, p-value (one-tailed): {p_val:.3f}\n")
