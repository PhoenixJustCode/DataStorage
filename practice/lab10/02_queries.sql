-- ============================================================
-- LAB 10 – Task 2: Business SQL Queries
-- ============================================================

--  
-- Q1. Total revenue by genre
--     (highest to lowest)
--  

SELECT
    p.genre,
    SUM(f.revenue)  AS total_revenue
FROM fact_sales  f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.genre
ORDER BY total_revenue DESC;

/*
Expected result:
genre        | total_revenue
-------------|-------------
Fiction      |     239.96    (99.98 + 39.99 + 45.00 + 49.99 + 45.00 = 279.96) -- recalc below
Science      |     119.97
Self-Help    |      54.95
Technology   |      14.99
History      |      12.99

Detailed check:
  Fiction:     sales 1(99.98) + 4(45.00) + 7(49.99) + 9(45.00) = 239.97
  Science:     sales 2(39.99) + 8(79.98)                        = 119.97
  Self-Help:   sales 5(32.97) + 10(21.98)                       =  54.95
  Technology:  sales 3(14.99)                                   =  14.99
  History:     sales 6(12.99)                                   =  12.99
*/

--  
-- Q2. Number of orders and total revenue per loyalty tier
--  

SELECT
    c.loyalty_tier,
    COUNT(DISTINCT f.order_id)  AS order_count,
    SUM(f.revenue)              AS total_revenue
FROM fact_sales  f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.loyalty_tier
ORDER BY total_revenue DESC;

/*
Expected result:
loyalty_tier | order_count | total_revenue
-------------|-------------|-------------
Gold         |      3      |    206.95    (orders 1001+1006 by customer 1, plus order 1006 row 10)
Platinum     |      2      |     77.99    (orders 1003 by customer 3 = 45+32.97; wait – customer 3 is Carol=Platinum)
Silver       |      2      |     94.97    (orders 1002+1005 by customer 2 = 14.99+79.98)
Bronze       |      1      |     62.98    (order 1004 by customer 4 = 12.99+49.99)

Breakdown by customer_key:
  customer 1 (Gold):     sales 1,2,9,10  → orders 1001,1006  revenue=99.98+39.99+45.00+21.98=206.95
  customer 2 (Silver):   sales 3,8       → orders 1002,1005  revenue=14.99+79.98=94.97
  customer 3 (Platinum): sales 4,5       → order  1003       revenue=45.00+32.97=77.97
  customer 4 (Bronze):   sales 6,7       → order  1004       revenue=12.99+49.99=62.98
*/

--  
-- Q3. Monthly total revenue for 2024
--     (ordered by month number)
--  

SELECT
    d.month_name,
    d.month,
    SUM(f.revenue)  AS monthly_revenue
FROM fact_sales f
JOIN dim_date   d ON d.date_key = f.date_key
WHERE d.year = 2024
GROUP BY d.month, d.month_name
ORDER BY d.month;

/*
Expected result:
month_name | month | monthly_revenue
-----------|-------|----------------
January    |   1   |   139.97
February   |   2   |    14.99
March      |   3   |   140.95
April      |   4   |    79.98
May        |   5   |    66.98
*/

--  
-- Q4. Top 3 best-selling products by total quantity sold
--  

SELECT
    p.title,
    SUM(f.quantity)  AS total_quantity
FROM fact_sales  f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.product_key, p.title
ORDER BY total_quantity DESC
LIMIT 3;

/*
Expected result:
title                      | total_quantity
---------------------------|---------------
Atomic Habits              |       5        (3 + 2)
The Great Gatsby           |       3        (2 + 1)
A Brief History of Time    |       3        (1 + 2)
*/

--  
-- Q5. Average order value  (total revenue / distinct orders)
--  

SELECT
    ROUND(
        SUM(revenue) / COUNT(DISTINCT order_id),
        2
    )  AS avg_order_value
FROM fact_sales;

/*
Expected result:
  Total revenue   = 442.87
  Distinct orders = 6  (1001, 1002, 1003, 1004, 1005, 1006)
  avg_order_value = 73.81
*/

--  
-- Q6. Customers who have spent more than $100
--  

SELECT
    c.name,
    SUM(f.revenue)  AS total_spent
FROM fact_sales  f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.customer_key, c.name
HAVING SUM(f.revenue) > 100
ORDER BY total_spent DESC;

/*
Expected result:
name          | total_spent
--------------|------------
Alice Johnson |    206.95
Bob Smith     |     94.97  -- excluded (< 100)  wait: 94.97 < 100 → excluded
Carol White   |     77.97  -- excluded
David Brown   |     62.98  -- excluded

Only Alice Johnson qualifies with 206.95.
*/
