# Lab 10 – Star Schema Analysis: Online Bookstore

---

## Task 1 – Understand the Design

### 1.1 Grain of the Fact Table

> **Each row in `fact_sales` represents one line item within a customer order: a single product sold in a specific quantity at a specific price on a specific date.**

### 1.2 Dimensions and Grouping Attributes

| Dimension | Grouping Attribute 1 | Grouping Attribute 2 |
|-----------|---------------------|---------------------|
| `dim_product` | `genre` – group revenue by book category | `author` – rank authors by sales volume |
| `dim_customer` | `loyalty_tier` – compare spending by tier | `registration_date` (year) – cohort analysis |
| `dim_date` | `month` / `month_name` – monthly trends | `quarter` – quarterly performance reports |

### 1.3 Keys and Relationships

| Concept | Detail |
|---------|--------|
| **Primary key** of `fact_sales` | `sales_key` (surrogate integer, auto-generated) |
| **Foreign keys** | `product_key → dim_product.product_key` |
| | `customer_key → dim_customer.customer_key` |
| | `date_key → dim_date.date_key` |
| **Relationship type** | Many-to-one from fact to each dimension (classic star topology) |

---

## Task 2 – SQL Queries & Results

### Q1. Total Revenue by Genre

```sql
SELECT p.genre, SUM(f.revenue) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.genre
ORDER BY total_revenue DESC;
```

| genre | total_revenue |
|-------|--------------|
| Fiction | 239.97 |
| Science | 119.97 |
| Self-Help | 54.95 |
| Technology | 14.99 |
| History | 12.99 |

---

### Q2. Orders and Revenue per Loyalty Tier

```sql
SELECT c.loyalty_tier,
       COUNT(DISTINCT f.order_id) AS order_count,
       SUM(f.revenue)             AS total_revenue
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.loyalty_tier
ORDER BY total_revenue DESC;
```

| loyalty_tier | order_count | total_revenue |
|-------------|-------------|--------------|
| Gold | 2 | 206.95 |
| Silver | 2 | 94.97 |
| Bronze | 1 | 62.98 |
| Platinum | 1 | 77.97 |

---

### Q3. Monthly Revenue for 2024

```sql
SELECT d.month_name, d.month, SUM(f.revenue) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
WHERE d.year = 2024
GROUP BY d.month, d.month_name
ORDER BY d.month;
```

| month_name | month | monthly_revenue |
|-----------|-------|----------------|
| January | 1 | 139.97 |
| February | 2 | 14.99 |
| March | 3 | 140.95 |
| April | 4 | 79.98 |
| May | 5 | 66.98 |

---

### Q4. Top 3 Best-Selling Products (by Quantity)

```sql
SELECT p.title, SUM(f.quantity) AS total_quantity
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.product_key, p.title
ORDER BY total_quantity DESC
LIMIT 3;
```

| title | total_quantity |
|-------|---------------|
| Atomic Habits | 5 |
| The Great Gatsby | 3 |
| A Brief History of Time | 3 |

---

### Q5. Average Order Value

```sql
SELECT ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM fact_sales;
```

| avg_order_value |
|----------------|
| 73.81 |

*Calculation: total revenue $442.87 ÷ 6 distinct orders = $73.81*

---

### Q6. Customers Who Spent More Than $100

```sql
SELECT c.name, SUM(f.revenue) AS total_spent
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.customer_key, c.name
HAVING SUM(f.revenue) > 100
ORDER BY total_spent DESC;
```

| name | total_spent |
|------|------------|
| Alice Johnson | 206.95 |

*Only Alice Johnson exceeds the $100 threshold.*

---

## Task 3 – Slowly Changing Dimension (Type 2)

### 3.1 Problem with Type 1

With **Type 1** (overwrite), when Alice upgrades from *Gold* to *Platinum*, her row is simply updated:

```
customer_key=1, loyalty_tier='Platinum'   ← overwrites Gold
```

All historical `fact_sales` rows still point to `customer_key=1`, so any report grouping revenue by `loyalty_tier` will now attribute ALL of Alice's past purchases—including those made when she was *Gold*—to *Platinum*. This **destroys historical accuracy**: it becomes impossible to know how much Gold-tier customers actually spent versus how much Platinum-tier customers spent.

### 3.2 Type 2 Table Structure

```sql
CREATE TABLE dim_customer_v2 (
    customer_key      INT           PRIMARY KEY,  -- new key per version
    customer_id       VARCHAR(20)   NOT NULL,     -- natural business key
    name              VARCHAR(100)  NOT NULL,
    email             VARCHAR(150)  NOT NULL,
    loyalty_tier      VARCHAR(20)   NOT NULL,
    registration_date DATE          NOT NULL,

    -- SCD Type 2 versioning columns
    effective_date    DATE          NOT NULL,     -- version start date
    expiry_date       DATE          NULL,         -- NULL = currently active
    is_current        BOOLEAN       NOT NULL DEFAULT TRUE,
    customer_version  INT           NOT NULL DEFAULT 1
);
```

### 3.3 SQL: Close Old Row + Insert New Row

```sql
-- Step A: expire the current Gold row (last valid day = 2024-03-31)
UPDATE dim_customer_v2
SET  expiry_date = '2024-03-31',
     is_current  = FALSE
WHERE customer_id = 'C1001'
  AND is_current  = TRUE;

-- Step B: insert new Platinum row with a fresh surrogate key
INSERT INTO dim_customer_v2
    (customer_key, customer_id, name, email, loyalty_tier,
     registration_date, effective_date, expiry_date, is_current, customer_version)
VALUES
    (101, 'C1001', 'Alice Johnson', 'alice@email.com', 'Platinum',
     '2022-03-15', '2024-04-01', NULL, TRUE, 2);
```

**Result after the change:**

| customer_key | loyalty_tier | effective_date | expiry_date | is_current |
|-------------|-------------|---------------|------------|-----------|
| 1 | Gold | 2022-03-15 | 2024-03-31 | FALSE |
| 101 | Platinum | 2024-04-01 | NULL | TRUE |

### 3.4 Handling Existing Fact Rows

**No updates to `fact_sales` are required.** This is the key advantage of Type 2:

- Rows with `date_key ≤ 20240331` already reference `customer_key = 1` (Gold version) → correctly attributed to Gold.
- New sales rows after 2024-04-01 will use `customer_key = 101` (Platinum version) → correctly attributed to Platinum.
- Historical integrity is preserved automatically through the immutable surrogate key.

---

## Task 4 – Reflection

A star schema dramatically simplifies analytical queries compared to a normalized 3NF transactional schema. In a normalized schema, answering "monthly revenue by loyalty tier" might require joining five or more tables (orders, order_lines, products, customers, tiers), each requiring its own join condition; in a star schema the same question is a single two-table join between the fact table and two dimensions. Aggregations such as SUM and COUNT run faster because the dimensional attributes are pre-joined and stored redundantly in wide, flat tables, reducing the number of joins the query optimizer must resolve. Pre-computing the `revenue` column (denormalized as `quantity × unit_price`) further eliminates runtime arithmetic across millions of rows. The main trade-off of denormalization is **data redundancy**: if a product's genre name changes, every row in `dim_product` must be updated rather than a single lookup record. A second trade-off is **write complexity**—ETL pipelines must manage surrogate key generation, SCD logic, and consistency checks that a normalized schema handles naturally through referential integrity. Finally, the warehouse becomes **read-optimized at the cost of write performance**, which is acceptable for analytical workloads but unsuitable for high-throughput transactional systems where data freshness and update speed are critical.

---

## File Index

| File | Contents |
|------|----------|
| [01_schema_and_data.sql](01_schema_and_data.sql) | DDL for all tables + sample data inserts |
| [02_queries.sql](02_queries.sql) | All six business SQL queries with expected results |
| [03_scd_type2.sql](03_scd_type2.sql) | Type 2 dim_customer redesign + tier-change SQL |
| [lab10_report.md](lab10_report.md) | This report |
