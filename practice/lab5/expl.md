# A/B Testing Analysis Explanation

This document explains the Python A/B testing code, dataset, and all statistical terms used.

---

## 1. Dataset / Variables

| Column         | Meaning                                                  |
| -------------- | -------------------------------------------------------- |
| `visitor_id`   | Unique identifier for each visitor.                      |
| `group`        | Indicates if visitor is in Control (A) or Treatment (B). |
| `converted`    | 1 if visitor purchased, 0 otherwise (binary variable).   |
| `time_on_site` | Seconds spent on website (continuous numeric variable).  |
| `pages_viewed` | Number of pages viewed (integer numeric variable).       |

---

## 2. Hypotheses

In A/B testing, we test if the new version (B) is better than the old version (A).

**Conversion Rate**

* H₀: p_B ≤ p_A (Treatment B is not better than A)
* H₁: p_B > p_A (Treatment B increases conversion)

**Time on Site**

* H₀: mean_B ≤ mean_A (B does not increase time spent)
* H₁: mean_B > mean_A (B increases time spent)

**Pages Viewed**

* Same as Time on Site: test if B increases pages viewed.

---

## 3. Statistical Tests

### a) Two-Proportion z-test (for `converted`)

* Used for binary variables.

* Tests whether the proportion of successes (conversions) is higher in B than A.

* **Formula:**

  z = (p_B - p_A) / sqrt(p*(1-p)*(1/n_B + 1/n_A))

  where p = (total successes in A + B) / (total visitors in A + B)

* **Assumptions:**

  1. Independent observations.
  2. Sample size large enough: n*p ≥ 10 and n*(1-p) ≥ 10.

* **Output:**

  * `z-stat`: number of standard deviations difference.
  * `p-value`: probability of seeing the effect by chance under H₀.

### b) t-test for independent samples (for `time_on_site` and `pages_viewed`)

* Used for continuous variables.

* Compares the average value between two independent groups.

* **Formula:**

  t = (mean_B - mean_A) / sqrt((s_B^2/n_B) + (s_A^2/n_A))

* **Assumptions:**

  1. Independent observations.
  2. Data in each group is approximately normally distributed.
  3. Variances are similar (use Welch's t-test if not).

* **Output:**

  * `t-stat`: how many standard errors the difference is from zero.
  * `p-value`: probability of observing the difference under H₀.

---

## 4. One-tailed vs Two-tailed Tests

* One-tailed: test if B is **better** than A.
* Two-tailed: test if B is **different** from A (better or worse).
* Here, we use **one-tailed** because we care only if B improves metrics.

---

## 5. Interpreting Results

* **p-value < 0.05** → reject H₀ → B is statistically significantly better.
* **p-value ≥ 0.05** → do not reject H₀ → cannot claim improvement.

**Other Terms:**

| Term                     | Meaning                                                          |
| ------------------------ | ---------------------------------------------------------------- |
| Mean                     | Average value of variable.                                       |
| Standard deviation       | How spread out values are around the mean.                       |
| Variance                 | Standard deviation squared.                                      |
| Proportion               | Fraction of successes: successes / total.                        |
| Independent observations | Each visitor behaves independently.                              |
| p-value                  | Probability that observed difference happens by chance under H₀. |
| Significance level (α)   | Threshold for rejecting H₀ (commonly 0.05).                      |

---

## 6. Random Assignment & Control

* Randomly assigning visitors ensures **independence** and avoids bias.
* Control group (A) = baseline.
* Treatment group (B) = new design to test.
