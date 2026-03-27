# Data Storage & Analysis — Конспект для Midterm

> Предмет охватывает: EDA, статистику, теорию вероятностей, Naive Bayes, A/B тестирование, линейную регрессию.

---

## Содержание

1. [Lab 1 — Введение в Pandas и базовый EDA](#lab-1)
2. [Lab 2 — Углублённый EDA, groupby, визуализации](#lab-2)
3. [Lab 3 — Статистический анализ, выбросы, корреляции](#lab-3)
4. [Lab 4 — Теория вероятностей и Naive Bayes](#lab-4)
5. [Lab 5 — A/B Тестирование](#lab-5)
6. [Lab 6 — Линейная регрессия](#lab-6)
7. [Шпаргалка по функциям](#shpargalka)

---

## Lab 1 — Введение в Pandas и базовый EDA {#lab-1}

**Датасет:** StudentsPerformance (`student_data.csv`) — 1000 студентов, оценки по математике, чтению, письму.

### Цель
Загрузить датасет, исследовать его структуру, найти корреляции, построить график.

### Основные шаги

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("student_data.csv")
```

### Ключевые функции

| Функция | Что делает |
|---|---|
| `df.shape` | Возвращает кортеж `(строки, столбцы)` |
| `df.columns.tolist()` | Список названий столбцов |
| `df.head(n)` | Первые n строк (по умолчанию 5) |
| `df.info()` | Типы данных и количество непустых значений |
| `df.isna().sum()` | Количество пропущенных значений по каждому столбцу |
| `df.describe()` | Описательная статистика: mean, std, min, max, квартили |
| `df.select_dtypes(include="number")` | Выбрать только числовые столбцы |
| `num_cols.corr()` | Матрица корреляций (Пирсона) |

### Нахождение самой коррелированной пары столбцов

```python
corr = num_cols.corr()

# Убираем диагональ (корреляция столбца с самим собой = 1.0)
corr_pairs = (
    corr.where(~(corr == 1.0))
        .stack()
        .reset_index()
)
corr_pairs.columns = ["col1", "col2", "corr"]

# Убираем дублирующиеся пары (A,B) и (B,A)
corr_pairs["pair"] = corr_pairs.apply(
    lambda r: tuple(sorted([r["col1"], r["col2"]])), axis=1
)
corr_pairs = corr_pairs.drop_duplicates("pair").drop(columns=["pair"])

top_pair = corr_pairs.sort_values("corr", ascending=False).iloc[0]
```

**Что такое корреляция Пирсона?**
- Число от -1 до +1
- +1 = идеальная прямая зависимость
- -1 = идеальная обратная зависимость
- 0 = нет линейной зависимости
- Сильная корреляция: |r| > 0.7

### Scatter plot (диаграмма рассеяния)

```python
plt.figure(figsize=(7, 5))
plt.scatter(df[x_col], df[y_col])
plt.title(f"{x_col} vs {y_col}")
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True, alpha=0.3)
plt.show()
```

**Вывод Lab 1:** Чтение и письмо имеют самую высокую корреляцию (~0.95), что значит эти навыки развиваются вместе.

---

## Lab 2 — Углублённый EDA, groupby, визуализации {#lab-2}

**Датасет:** `students.csv` — тот же датасет StudentPerformance, 8 признаков.

### Очистка и нормализация названий столбцов

```python
df.columns = (
    df.columns
    .str.lower()           # все в нижний регистр
    .str.replace(" ", "_") # пробелы -> подчёркивание
    .str.replace("/", "_") # слэши -> подчёркивание
)
```

**Зачем?** Нормализованные имена проще использовать в коде: `df.math_score` вместо `df["math score"]`.

### groupby — группировка и агрегация

```python
# Средний балл по математике по полу
q1 = df.groupby("gender")["math_score"].mean().round(2).reset_index()
```

| Метод | Описание |
|---|---|
| `groupby("col")` | Группировать по значениям столбца |
| `.mean()` | Среднее по группе |
| `.sum()` | Сумма по группе |
| `.count()` | Количество строк в группе |
| `.round(2)` | Округлить до 2 знаков |
| `.reset_index()` | Превратить индексы в столбцы |
| `.sort_values("col", ascending=False)` | Сортировка по убыванию |

### Анализ нескольких столбцов одновременно

```python
q3 = df.groupby("test_preparation_course")[
    ["math_score", "reading_score", "writing_score"]
].mean().round(2)
```

### Корреляция двух конкретных столбцов

```python
rw_corr = df["reading_score"].corr(df["writing_score"])
# rw_corr ≈ 0.95 → очень сильная корреляция
```

### Матрица корреляций для нескольких столбцов

```python
scores = df[["math_score", "reading_score", "writing_score"]]
print(scores.corr())
```

### Визуализации

**Boxplot (ящик с усами):**
```python
df.boxplot(column="math_score", by="gender")
plt.title("Math Score Distribution by Gender")
plt.savefig("viz_1_math_by_gender.png")
plt.close()
```
- Показывает медиану, квартили, выбросы
- Удобен для сравнения распределений по группам

**Bar chart (столбчатая диаграмма):**
```python
q3.plot(kind="bar")
plt.xticks(rotation=0)
plt.savefig("viz_3_test_prep_effect.png")
plt.close()
```

### Структура EDA-отчёта

1. **Executive Summary** — краткий вывод (сколько записей, ключевые находки)
2. **Data Quality** — пропуски, типы данных, выбросы
3. **Key Insights** — 3 главных вывода с доказательствами
4. **Visualization Summary** — что показывает каждый график
5. **Recommendations** — рекомендации и следующие шаги

### Выводы Lab 2

- Студенты, прошедшие курс подготовки к тестам, получают более высокие оценки по всем предметам
- Чтение и письмо имеют коэффициент корреляции ≈ 0.95
- Студенты со стандартным питанием (не льготным) учатся лучше

---

## Lab 3 — Статистический анализ, выбросы, корреляции {#lab-3}

**Датасет:** `movies.csv` — фильмы с бюджетом, кассовыми сборами, рейтингом IMDb.

### Импорт библиотек

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
```

### Обработка пропущенных значений

```python
# Заполняем медианой (устойчива к выбросам)
df['budget'] = df['budget'].fillna(df['budget'].median())
df['gross'] = df['gross'].fillna(df['gross'].median())
```

**Почему медиана, а не среднее?**
- Среднее чувствительно к выбросам (один блокбастер с $500M может сильно исказить)
- Медиана стабильна — это середина отсортированного ряда

### Валидация данных

```python
# Убираем некорректные строки
df = df[(df['budget'] >= 0) & (df['gross'] >= 0) & (df['runtime'] >= 10)]

# Добавляем вычисляемый столбец
df['profit'] = df['gross'] - df['budget']
```

### Описательная статистика — полная сводка

```python
num_cols = ['budget', 'gross', 'runtime', 'score', 'votes']
summary = pd.DataFrame(index=num_cols)

summary['mean']     = df[num_cols].mean()
summary['median']   = df[num_cols].median()
summary['mode']     = df[num_cols].mode().iloc[0]
summary['range']    = df[num_cols].max() - df[num_cols].min()
summary['variance'] = df[num_cols].var()
summary['std_dev']  = df[num_cols].std()
summary['IQR']      = df[num_cols].quantile(0.75) - df[num_cols].quantile(0.25)
```

### Ключевые статистические термины

| Термин | Формула / Описание |
|---|---|
| **Mean (среднее)** | Сумма / количество |
| **Median (медиана)** | Середина отсортированного ряда |
| **Mode (мода)** | Наиболее частое значение |
| **Range (размах)** | max - min |
| **Variance (дисперсия)** | Среднее квадратов отклонений от среднего |
| **Std Dev (ст. отклонение)** | sqrt(variance) — в тех же единицах, что данные |
| **IQR (межквартильный размах)** | Q3 - Q1, содержит 50% данных |

### Коэффициент вариации (CV)

```python
cv = summary['std_dev'] / summary['mean']
```
- Показывает относительный разброс (в долях от среднего)
- CV > 1 означает очень высокую изменчивость
- Позволяет сравнивать разброс величин с разными единицами измерения

### Скошенность (Skewness)

```python
# Приближённая формула Пирсона
skewness = 3 * (mean - median) / std_dev
```
- **> 0** = правосторонний хвост (right-skewed), большинство значений слева
- **< 0** = левосторонний хвост (left-skewed), большинство значений справа
- **= 0** = симметричное распределение

### Выбросы — метод IQR

```python
def iqr_outliers(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    # Границы: Q1 - 1.5*IQR  и  Q3 + 1.5*IQR
    return series[(series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)]
```

**Правило Тьюки (IQR rule):** всё, что выходит за пределы `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`, считается выбросом.

### Проверка нормальности — Q-Q Plot

```python
stats.probplot(df['score'], plot=plt)
plt.title("Q-Q Plot IMDb Score")
plt.show()
```
- Если точки лежат на прямой → распределение нормальное
- Отклонение в хвостах → тяжёлые хвосты или скошенность

### Правило 68-95-99.7 (эмпирическое правило)

```python
within_1 = df[(df['score'] >= mean-std) & (df['score'] <= mean+std)].shape[0] / len(df) * 100
within_2 = df[(df['score'] >= mean-2*std) & (df['score'] <= mean+2*std)].shape[0] / len(df) * 100
```
- В нормальном распределении: ±1σ → 68%, ±2σ → 95%, ±3σ → 99.7%

### Анализ корреляций

```python
corr_matrix = df[numerical_cols].corr()

# Сильные положительные (> 0.7)
strong_positive = corr_matrix[(corr_matrix > 0.7) & (corr_matrix < 1.0)]

# Сильные отрицательные (< -0.3)
strong_negative = corr_matrix[corr_matrix < -0.3]
```

### Scatter Matrix (Pair Plot)

```python
sns.pairplot(
    df,
    vars=['budget', 'gross', 'score', 'votes'],
    hue='genre',        # цветовое разделение по жанру
    diag_kind='kde',    # на диагонали — KDE (сглаженная гистограмма)
    plot_kws={'alpha': 0.5}
)
```

### Profit Margin (маржа прибыли)

```python
df['profit_margin'] = np.where(
    df['budget'] == 0,
    np.nan,                                         # деление на 0 → NaN
    (df['gross'] - df['budget']) / df['budget']     # (сборы - бюджет) / бюджет
)
```

### Анализ по категориям (жанрам)

```python
# Boxplot бюджета по жанрам
sns.boxplot(data=df, x='genre', y='budget')
plt.xticks(rotation=45)

# Violin plot рейтинга по жанрам
sns.violinplot(data=df, x='genre', y='score')

# Средняя маржа по жанрам
genre_profit = df.groupby('genre')['profit_margin'].mean()

# Жанр с наибольшим медианным бюджетом
df.groupby('genre')['budget'].median().idxmax()
```

### Анализ временных трендов

```python
# Скользящее среднее (3-летнее)
budget_year = df.groupby('year')['budget'].mean().rolling(3).mean()
```
- `rolling(3).mean()` сглаживает шумы, показывая долгосрочный тренд

### Выводы Lab 3

- Budget и gross имеют сильную положительную корреляцию (ожидаемо)
- Рейтинг IMDb слабо коррелирует с прибылью — высокий рейтинг не гарантирует кассовый успех
- Часть жанров с низким бюджетом показывает высокую маржу

---

## Lab 4 — Теория вероятностей и Naive Bayes {#lab-4}

**Датасет:** Telco Customer Churn — данные телекоммуникационной компании о клиентах.

**Задача:** Предсказать, уйдёт ли клиент (Churn = Yes/No).

### Часть 1: Теория вероятностей

#### Безусловная вероятность

```python
p_churn = df['Churn'].value_counts(normalize=True)['Yes']
# Результат: P(Churn) = 0.266 (26.6%)
```

`normalize=True` — возвращает доли вместо абсолютных чисел.

#### Условная вероятность P(A|B)

**P(Churn | условие)** = вероятность ухода при выполнении условия

```python
# P(Churn | Month-to-month contract)
p_churn_month = df[df['Contract'] == 'Month-to-month']['Churn'].value_counts(normalize=True)['Yes']
# Результат: 42.7%

# P(Churn | tenure < 12)
p_churn_new = df[df['tenure'] < 12]['Churn'].value_counts(normalize=True)['Yes']
# Результат: 48.5%
```

**Формула условной вероятности:**
```
P(A|B) = P(A ∩ B) / P(B)
```

#### Лифт (Lift)

```python
p_joint = (p_churn_month * p_churn_fiber) / p_churn
lift = p_joint / p_churn
# Lift = 2.53 → риск ухода в 2.5 раза выше среднего
```

**Лифт > 1** → комбинация факторов увеличивает риск выше базового уровня.

#### Churn по группам

```python
contract_churn = df.groupby('Contract')['Churn'].apply(
    lambda x: (x == 'Yes').mean()
)
```

**Результаты:**
- Two-year contract: 2.85% (самый низкий churn)
- Month-to-month: 42.7% (самый высокий)
- Старшие граждане (SeniorCitizen=1): 41.7% vs 23.7%
- Paperless Billing: 33.6% vs 16.4%

### Часть 2: Naive Bayes Classifier

#### Идея алгоритма

Naive Bayes применяет теорему Байеса и делает **"наивное" предположение** — все признаки независимы друг от друга:

```
P(класс | признаки) ∝ P(класс) × P(признак1|класс) × P(признак2|класс) × ...
```

#### Подготовка данных

```python
# Кодирование категориальных признаков числами
for c in X.select_dtypes(include='object').columns:
    X[c] = X[c].astype('category').cat.codes

# Разделение на train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

| Шаг | Описание |
|---|---|
| `astype('category').cat.codes` | Заменяет строки числами: "Yes"→1, "No"→0 |
| `train_test_split(..., test_size=0.2)` | 80% данных на обучение, 20% на тест |
| `random_state=42` | Фиксирует случайность для воспроизводимости |

#### Априорные вероятности (Priors)

```python
priors = {
    1: y_train.mean(),         # P(Churn=1)
    0: 1 - y_train.mean()      # P(Churn=0)
}
```

#### Гауссовская (нормальная) вероятность для числовых признаков

```python
def gaussian_prob(x, mean, std):
    return (1 / (np.sqrt(2 * np.pi) * std)) * np.exp(-(x - mean)**2 / (2 * std**2))
```

**Формула нормального распределения:**
```
f(x) = (1 / (σ√(2π))) × e^(-(x-μ)²/(2σ²))
```
- μ (mu) = среднее
- σ (sigma) = стандартное отклонение

#### Предсказание вручную

```python
def nb_predict_proba(X):
    probs = []
    for idx, row in X.iterrows():
        p = {}
        for cls in [0, 1]:
            likelihood = priors[cls]
            # Categorical features
            for col in categorical_cols:
                likelihood *= feature_probs[col].get(row[col], {0: 1e-6, 1: 1e-6})[cls]
            # Numerical features
            for col in numerical_cols:
                mean, std = numerical_stats[col][cls]
                likelihood *= gaussian_prob(row[col], mean, std)
            p[cls] = likelihood
        total = p[0] + p[1]
        probs.append(p[1] / total)   # нормализация → вероятность класса 1
    return np.array(probs)
```

#### Sklearn GaussianNB

```python
from sklearn.naive_bayes import GaussianNB

gnb = GaussianNB()
gnb.fit(X_train, y_train)
y_pred_gnb = gnb.predict(X_test)
```

#### Метрики качества классификации

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
```

| Метрика | Формула | Интерпретация |
|---|---|---|
| **Accuracy** | (TP+TN)/(TP+TN+FP+FN) | Доля правильных ответов |
| **Precision** | TP/(TP+FP) | Из тех, кого предсказали "ушёл", сколько реально ушло |
| **Recall** | TP/(TP+FN) | Из тех, кто реально ушёл, сколько мы поймали |
| **F1-score** | 2×(P×R)/(P+R) | Гармоническое среднее Precision и Recall |

**Матрица ошибок (Confusion Matrix):**
```
              Predicted No  Predicted Yes
Actual No  |     TN         |    FP       |
Actual Yes |     FN         |    TP       |
```

**Результаты Lab 4:**
- Manual NB: Accuracy 71.6%, Recall 78.9%, F1 59.7%
- Sklearn GaussianNB: Accuracy 73.9%, F1 59.8%

#### ROC-кривая

```python
from sklearn.metrics import RocCurveDisplay
RocCurveDisplay.from_predictions(y_test, y_pred_prob)
```
- Показывает компромисс между TPR (recall) и FPR
- AUC (площадь под кривой): 1.0 = идеал, 0.5 = случайный классификатор

### Часть 3: Бизнес-анализ решений

#### Expected Value (ожидаемая ценность)

```python
CLV = 2000    # Customer Lifetime Value
cost = 300    # стоимость удержания клиента
success = 0.4 # вероятность успешного удержания

EV = P(Churn) × CLV × success - cost
```

**Пример:** при P(Churn)=0.8: EV = 0.8 × 2000 × 0.4 - 300 = 340 USD

#### Матрица сегментации рисков

```python
high_value = X_test['MonthlyCharges'] > 70     # высокая ценность
high_risk = pd.Series(y_pred_prob > 0.6, ...)   # высокий риск

# 4 квадранта:
# HV_HR — приоритет №1 для retention
# HV_LR — важные клиенты, но риск низкий
# LV_HR — дешёвые клиенты, но готовы уйти
# LV_LR — нет необходимости действовать
```

| Квадрант | Клиентов | Ожидаемые потери | Ожидаемая прибыль |
|---|---|---|---|
| HV_HR | 378 | $713,560 | $172,024 |
| HV_LR | 340 | $69,480 | -$74,208 |
| LV_HR | 209 | $377,886 | $88,454 |
| LV_LR | 480 | $54,545 | -$122,182 |

**Вывод:** Фокусироваться на HV_HR — наибольший ROI.

---

## Lab 5 — A/B Тестирование {#lab-5}

**Сценарий:** Тестируем новый дизайн сайта (B) против старого (A) на 10,000 посетителях.

### Переменные

| Переменная | Тип | Описание |
|---|---|---|
| `visitor_id` | int | Уникальный ID посетителя |
| `group` | str | "A" (контроль) или "B" (лечение) |
| `converted` | int | 1 = купил, 0 = не купил |
| `time_on_site` | float | Время на сайте (секунды) |
| `pages_viewed` | int | Количество просмотренных страниц |

### Генерация датасета

```python
np.random.seed(42)  # воспроизводимость
n = 10000

group = np.random.choice(['A', 'B'], size=n, p=[0.5, 0.5])

# Конверсия (бинарная — да/нет)
converted = np.where(
    group == 'A',
    np.random.binomial(1, 0.05, n),   # 5% конверсия
    np.random.binomial(1, 0.065, n)   # 6.5% конверсия
)

# Время (нормальное распределение)
time_on_site = np.where(
    group == 'A',
    np.random.normal(120, 30, n),
    np.random.normal(130, 35, n)
)
time_on_site = np.clip(time_on_site, 0, None)  # нет отрицательного времени

# Страницы (распределение Пуассона — целые числа)
pages_viewed = np.where(
    group == 'A',
    np.random.poisson(4, n),
    np.random.poisson(4.3, n)
)
```

### Формулировка гипотез

Для каждой метрики:

**H₀ (нулевая гипотеза):** B не лучше A (нет улучшения)
**H₁ (альтернативная гипотеза):** B лучше A (есть улучшение)

Пример для конверсии:
- H₀: p_B ≤ p_A
- H₁: p_B > p_A (one-tailed, нас интересует только улучшение)

### Тест 1: Z-тест для двух пропорций (конверсия)

```python
from statsmodels.stats.proportion import proportions_ztest

successes = df.groupby('group')['converted'].sum().values   # кол-во конверсий
nobs = df.groupby('group')['converted'].count().values       # кол-во посетителей

z_stat, p_val = proportions_ztest(count=successes, nobs=nobs, alternative='larger')
```

**Формула:**
```
z = (p_B - p_A) / sqrt(p * (1-p) * (1/n_B + 1/n_A))

где p = (successes_A + successes_B) / (n_A + n_B)  — pooled proportion
```

**Условия применения:**
- Независимые наблюдения (случайное распределение)
- n × p ≥ 10 и n × (1-p) ≥ 10 в каждой группе

### Тест 2: T-тест для независимых выборок (time_on_site, pages_viewed)

```python
from scipy import stats

t_stat, p_val = stats.ttest_ind(time_B, time_A, alternative='greater')
```

**Формула:**
```
t = (mean_B - mean_A) / sqrt(s_B²/n_B + s_A²/n_A)
```

**Условия применения:**
- Независимые наблюдения
- Данные примерно нормально распределены (для больших n работает по ЦПТ)
- При неравных дисперсиях используется тест Уэлча (по умолчанию в scipy)

### Интерпретация результатов

| p-value | Решение |
|---|---|
| p < 0.05 | Отвергаем H₀ → результат статистически значимый |
| p ≥ 0.05 | Не отвергаем H₀ → нет доказательств улучшения |

### Ключевые термины

| Термин | Объяснение |
|---|---|
| **p-value** | Вероятность получить такой или более экстремальный результат при условии H₀ |
| **z-stat / t-stat** | Количество стандартных ошибок между наблюдаемой разницей и нулём |
| **Significance level α** | Порог отклонения H₀, обычно 0.05 |
| **One-tailed test** | Проверяем только одно направление (B > A) |
| **Two-tailed test** | Проверяем любое отличие (B ≠ A) |
| **Type I Error** | Отвергли H₀, когда она верна (ложная тревога) |
| **Type II Error** | Не отвергли H₀, когда она ложна (пропустили эффект) |

### Выводы Lab 5

- Конверсия группы B (6.5%) статистически значимо выше A (5.0%)
- Время на сайте B (130s) > A (120s) — значимо
- Страниц просмотрено B (4.3) > A (4.0) — значимо

---

## Lab 6 — Линейная регрессия {#lab-6}

**Датасет:** California Housing (sklearn) — данные о ценах на жильё в Калифорнии.

**Цель:** Предсказать медианную стоимость дома (`MedHouseVal`).

### Загрузка данных

```python
from sklearn.datasets import fetch_california_housing

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df["MedHouseVal"] = housing.target
```

### Признаки (Features)

| Признак | Описание |
|---|---|
| `MedInc` | Медианный доход в районе |
| `HouseAge` | Медианный возраст домов |
| `AveRooms` | Среднее число комнат |
| `AveBedrms` | Среднее число спален |
| `Population` | Население района |
| `AveOccup` | Среднее число жителей на дом |
| `Latitude` | Широта |
| `Longitude` | Долгота |

### Корреляционная матрица — тепловая карта

```python
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
```

**Вывод:** `MedInc` имеет наибольшую корреляцию с ценой дома.

### Множественная линейная регрессия (statsmodels)

```python
import statsmodels.api as sm

X = df.drop("MedHouseVal", axis=1)
y = df["MedHouseVal"]

X_const = sm.add_constant(X)  # добавляем константу (intercept)
model = sm.OLS(y, X_const).fit()
print(model.summary())
```

**Уравнение регрессии:**
```
y = β₀ + β₁×MedInc + β₂×HouseAge + ... + βₙ×Longitude + ε
```

- β₀ = intercept (свободный член)
- βᵢ = коэффициент регрессии для признака i
- ε = ошибка (остаток)

**Из `model.summary()` смотрим:**
- `coef` — коэффициент βᵢ (на сколько изменяется Y при увеличении Xᵢ на 1)
- `P>|t|` — p-value коэффициента (< 0.05 → значимый признак)
- `R-squared` — коэффициент детерминации (0.6 = модель объясняет 60% вариации)

### Мультиколлинеарность — VIF

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
vif_data["Feature"] = X_const.columns
vif_data["VIF"] = [
    variance_inflation_factor(X_const.values, i)
    for i in range(X_const.shape[1])
]
```

**VIF (Variance Inflation Factor):**
- VIF = 1 → нет мультиколлинеарности
- VIF = 5–10 → умеренная мультиколлинеарность
- VIF > 10 → серьёзная мультиколлинеарность, признак нужно удалить

**Проблема:** `AveRooms` и `AveBedrms` имеют высокий VIF (спальни — часть всех комнат).

**Решение:** Удалить `AveBedrms` из модели.

```python
X_refined = df.drop(["MedHouseVal", "AveBedrms"], axis=1)
X_refined_const = sm.add_constant(X_refined)
model_refined = sm.OLS(y, X_refined_const).fit()
```

### Анализ остатков (Residual Analysis)

```python
residuals = model_refined.resid

# График остатков vs предсказанные значения
plt.scatter(model_refined.fittedvalues, residuals)
plt.axhline(0)
plt.title("Residuals vs Fitted")

# Распределение остатков
sns.histplot(residuals, kde=True)
```

**Условия нормальной регрессии (проверяем по остаткам):**
1. Остатки центрированы вокруг нуля
2. Остатки нормально распределены
3. Нет паттернов (гомоскедастичность — равномерная дисперсия)
4. Независимость остатков

### Оценка модели (sklearn)

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
```

| Метрика | Формула | Интерпретация |
|---|---|---|
| **R² (R-squared)** | 1 - SS_res/SS_tot | Доля объяснённой дисперсии (0–1, выше лучше) |
| **RMSE** | sqrt(mean((y - ŷ)²)) | Средняя ошибка в единицах целевой переменной |
| **MSE** | mean((y - ŷ)²) | Среднеквадратичная ошибка |

**Результат Lab 6:**
- R² ≈ 0.60 — модель объясняет 60% вариации цен
- RMSE ≈ 0.7 (в единицах $100k)

### Выводы Lab 6

- Медианный доход (`MedInc`) — сильнейший предиктор цены дома
- Географическое положение (Latitude, Longitude) тоже значимо
- Удаление `AveBedrms` улучшило стабильность модели
- Оценка R² ~0.60 — умеренная точность, модель работает

---

## Шпаргалка по функциям {#shpargalka}

### Pandas

```python
pd.read_csv("file.csv")              # загрузка CSV
df.shape                              # (строки, столбцы)
df.head(n)                            # первые n строк
df.tail(n)                            # последние n строк
df.info()                             # типы данных, non-null count
df.describe()                         # описательная статистика
df.isna().sum()                       # кол-во NaN по столбцам
df.isnull().sum()                     # то же самое
df.fillna(value)                      # заполнить NaN значением
df.fillna(df.col.median())            # заполнить медианой
df.dropna(subset=['col'])             # удалить строки с NaN в col
df.dtypes                             # типы данных столбцов

df.columns.str.lower()                # нижний регистр
df.columns.str.replace(" ", "_")      # замена символов

df.select_dtypes(include="number")    # только числовые столбцы
df["col"].value_counts()              # частота значений
df["col"].value_counts(normalize=True) # относительные частоты
df["col"].nunique()                   # кол-во уникальных значений
df["col"].unique()                    # массив уникальных значений

df.groupby("col").mean()              # группировка + среднее
df.groupby("col").agg({...})          # группировка + несколько агрегаций
df.sort_values("col", ascending=False) # сортировка

df["col"].corr(df["col2"])            # корреляция двух столбцов
df.corr()                             # матрица корреляций
df.corr().stack()                     # матрица в длинный формат

df.quantile(0.25)                     # 1-й квартиль (Q1)
df.quantile(0.75)                     # 3-й квартиль (Q3)

pd.to_numeric(df["col"], errors='coerce')  # конвертация в число, ошибки → NaN
df["col"].astype("category").cat.codes     # категории → числа
``` 

### NumPy

```python
np.random.seed(42)                    # фиксирует случайность
np.random.choice(['A','B'], n, p=[.5,.5])  # случайный выбор
np.random.normal(mean, std, n)        # нормальное распределение
np.random.binomial(1, p, n)           # биномиальное (Бернулли)
np.random.poisson(lam, n)             # Пуассона

np.where(condition, val_true, val_false)   # условная замена
np.clip(arr, min, max)                # обрезать значения
np.sqrt(x)                            # квадратный корень
np.exp(x)                             # экспонента
np.pi                                 # число π
np.nan                                # Not a Number
np.inf                                # бесконечность
```

### Matplotlib / Seaborn

```python
# Matplotlib
plt.figure(figsize=(w, h))            # создать фигуру
plt.scatter(x, y)                     # диаграмма рассеяния
plt.plot(x, y)                        # линейный график
plt.bar(x, height)                    # столбчатая диаграмма
plt.hist(data, bins=30)               # гистограмма
plt.boxplot(data)                     # ящик с усами
plt.title("title")                    # заголовок
plt.xlabel("x"), plt.ylabel("y")      # подписи осей
plt.xticks(rotation=45)               # поворот подписей
plt.axhline(y=0)                      # горизонтальная линия
plt.axvline(x=val, color='red')       # вертикальная линия
plt.grid(True, alpha=0.3)             # сетка
plt.tight_layout()                    # автоотступы
plt.savefig("name.png")               # сохранить
plt.show()                            # показать
plt.close()                           # закрыть

# Seaborn
sns.histplot(df[col], kde=True)       # гистограмма + KDE
sns.boxplot(data=df, x=cat, y=num)    # боксплот
sns.violinplot(data=df, x=cat, y=num) # скрипичная диаграмма
sns.scatterplot(data=df, x=x, y=y)   # scatter с доп. опциями
sns.heatmap(corr, annot=True)         # тепловая карта корреляций
sns.pairplot(df, vars=[...], hue=cat) # матрица scatter plots
```

### Scipy / Statsmodels

```python
from scipy import stats

stats.ttest_ind(a, b, alternative='greater')    # t-тест независимых
stats.probplot(data, plot=plt)                  # Q-Q plot

from statsmodels.stats.proportion import proportions_ztest
proportions_ztest(count=[s_a, s_b], nobs=[n_a, n_b], alternative='larger')

import statsmodels.api as sm
sm.add_constant(X)            # добавить intercept
sm.OLS(y, X).fit()            # обычный МНК (OLS)
model.summary()               # подробная сводка
model.resid                   # остатки
model.fittedvalues            # предсказанные значения

from statsmodels.stats.outliers_influence import variance_inflation_factor
variance_inflation_factor(X.values, i)   # VIF для i-го признака
```

### Sklearn

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()
gnb.fit(X_train, y_train)

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score, r2_score, mean_squared_error
)
```

---

## Быстрый справочник по формулам

| Формула | Название |
|---|---|
| `corr = Σ(xi-x̄)(yi-ȳ) / (n×σx×σy)` | Корреляция Пирсона |
| `IQR = Q3 - Q1` | Межквартильный размах |
| `Выброс если: x < Q1-1.5×IQR или x > Q3+1.5×IQR` | Правило Тьюки |
| `CV = σ / μ` | Коэффициент вариации |
| `Skewness ≈ 3×(μ - median) / σ` | Скошенность (Пирсон) |
| `P(A\|B) = P(A∩B) / P(B)`  | Условная вероятность |
| `Lift = P(A\|B) / P(A)` | Лифт |
| `EV = P × CLV × success - cost` | Ожидаемая ценность |
| `z = (p_B - p_A) / SE` | Z-статистика (пропорции) |
| `t = (μ_B - μ_A) / SE` | T-статистика (средние) |
| `f(x) = (1/σ√2π)×e^(-(x-μ)²/2σ²)` | Гауссова плотность |
| `R² = 1 - SS_res/SS_tot` | R-squared |
| `RMSE = sqrt(mean((y-ŷ)²))` | Root Mean Squared Error |
| `F1 = 2×P×R/(P+R)` | F1-score |

---

*Автор: Alexandr Demchenko | Предмет: Data Storage & Analysis*
