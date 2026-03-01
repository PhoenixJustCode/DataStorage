import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["figure.autolayout"] = True


# 1. LOAD AND INSPECT DATASET
df = pd.read_csv("students.csv")

print("\n=== DATASET PREVIEW ===")
print(df.head())

print("\n=== DATASET INFO ===")
print(df.info())

print("\n=== DESCRIPTIVE STATISTICS ===")
print(df.describe())


# 2 DATA cleaning
print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("/", "_")
)

print("\n=== CLEANED COLUMNS ===")
print(df.columns)


# 3) RELATIONSHIP ANALYSIS
print("\n=== CORRELATION MATRIX ===")
scores = df[["math_score", "reading_score", "writing_score"]]
print(scores.corr())


# 4 Question
print("\n=== LAB QUESTIONS ANSWERS ===")

print("\n1) Average Math Score by Gender")
q1 = df.groupby("gender")["math_score"].mean().round(2).reset_index()
q1.columns = ["Gender", "Average Math Score"]
print(q1)

print("\n2) Correlation Between Reading and Writing Scores")
rw_corr = df["reading_score"].corr(df["writing_score"])
print(f"Correlation coefficient: {rw_corr:.3f}")

print("\n3) Effect of Test Preparation Course")
q3 = df.groupby("test_preparation_course")[
    ["math_score", "reading_score", "writing_score"]
].mean().round(2)
print(q3)

print("\n4) Performance by Parental Education Level")
q4 = df.groupby("parental_level_of_education")[
    ["math_score", "reading_score", "writing_score"]
].mean().round(2).sort_values("math_score", ascending=False)
print(q4)

print("\n5) Score Distribution by Lunch Type")
q5 = df.groupby("lunch")[
    ["math_score", "reading_score", "writing_score"]
].mean().round(2)
print(q5)

# --- Visualization 1: Math Score by Gender ---
plt.figure()
df.boxplot(column="math_score", by="gender")
plt.title("Math Score Distribution by Gender")
plt.suptitle("")
plt.xlabel("Gender")
plt.ylabel("Math Score")
plt.savefig("viz_1_math_by_gender.png")
plt.close()


# --- Visualization 2: Reading vs Writing ---

plt.figure()
plt.scatter(df["reading_score"], df["writing_score"])
plt.xlabel("Reading Score")
plt.ylabel("Writing Score")
plt.title("Reading vs Writing Scores")
plt.savefig("viz_2_reading_vs_writing.png")
plt.close()


# --- Visualization 3: Test Preparation Effect ---

plt.figure()
q3.plot(kind="bar")
plt.title("Average Scores by Test Preparation Course")
plt.xlabel("Test Preparation Course")
plt.ylabel("Average Score")
plt.xticks(rotation=0)
plt.savefig("viz_3_test_prep_effect.png")
plt.close()


# 6. KEY INSIGHTS
print("\n=== KEY INSIGHTS ===")
print("1. Test preparation improves student performance.")
print("2. Reading and writing scores are strongly correlated.")
print("3. Standard lunch students perform better on average.")
