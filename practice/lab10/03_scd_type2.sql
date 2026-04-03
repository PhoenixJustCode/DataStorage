-- ============================================================
-- LAB 10 – Task 3: Slowly Changing Dimension – Type 2
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- 3.1  New dim_customer table structure (Type 2)
--      Added columns:  effective_date, expiry_date,
--                      is_current, customer_version
-- ─────────────────────────────────────────────────────────────

CREATE TABLE dim_customer_v2 (
    customer_key      INT            PRIMARY KEY,   -- surrogate key (new row = new key)
    customer_id       VARCHAR(20)    NOT NULL,      -- natural/business key
    name              VARCHAR(100)   NOT NULL,
    email             VARCHAR(150)   NOT NULL,
    loyalty_tier      VARCHAR(20)    NOT NULL,
    registration_date DATE           NOT NULL,

    -- SCD Type 2 versioning columns ──────────────────────────
    effective_date    DATE           NOT NULL,      -- date this version became active
    expiry_date       DATE           NULL,          -- NULL means current row
    is_current        BOOLEAN        NOT NULL DEFAULT TRUE,
    customer_version  INT            NOT NULL DEFAULT 1
);

-- ─────────────────────────────────────────────────────────────
-- 3.2  Seed: original row for Alice Johnson (Gold tier)
-- ─────────────────────────────────────────────────────────────

INSERT INTO dim_customer_v2
    (customer_key, customer_id, name, email, loyalty_tier,
     registration_date, effective_date, expiry_date, is_current, customer_version)
VALUES
    (1, 'C1001', 'Alice Johnson', 'alice@email.com', 'Gold',
     '2022-03-15', '2022-03-15', NULL, TRUE, 1);

-- ─────────────────────────────────────────────────────────────
-- 3.3  Tier change: Gold → Platinum on 2024-04-01
--
--   Step A: Close the current (old) row
--   Step B: Insert a new row for the updated tier
--
--   fact_sales rows already written with customer_key = 1
--   (Gold era) automatically remain correct because they
--   point to the OLD surrogate key (customer_key = 1),
--   which now permanently represents the Gold period.
--   Future sales rows will use the NEW surrogate key (customer_key = 101).
-- ─────────────────────────────────────────────────────────────

-- Step A – expire the current Gold row
UPDATE dim_customer_v2
SET
    expiry_date      = '2024-03-31',   -- last day it was valid
    is_current       = FALSE
WHERE customer_id   = 'C1001'
  AND is_current    = TRUE;

-- Step B – insert new Platinum row with a new surrogate key
INSERT INTO dim_customer_v2
    (customer_key, customer_id, name, email, loyalty_tier,
     registration_date, effective_date, expiry_date, is_current, customer_version)
VALUES
    (101, 'C1001', 'Alice Johnson', 'alice@email.com', 'Platinum',
     '2022-03-15', '2024-04-01', NULL, TRUE, 2);

-- ─────────────────────────────────────────────────────────────
-- 3.4  Verify the two versions
-- ─────────────────────────────────────────────────────────────

SELECT
    customer_key,
    customer_id,
    name,
    loyalty_tier,
    effective_date,
    expiry_date,
    is_current,
    customer_version
FROM dim_customer_v2
WHERE customer_id = 'C1001'
ORDER BY customer_version;

/*
Expected result:
customer_key | customer_id | name          | loyalty_tier | effective_date | expiry_date | is_current | customer_version
-------------|-------------|---------------|--------------|----------------|-------------|------------|------------------
           1 | C1001       | Alice Johnson | Gold         | 2022-03-15     | 2024-03-31  | FALSE      | 1
         101 | C1001       | Alice Johnson | Platinum     | 2024-04-01     | NULL        | TRUE       | 2
*/

-- ─────────────────────────────────────────────────────────────
-- 3.5  Historical query: revenue per loyalty tier per PERIOD
--      (works correctly because old facts still point to key=1)
-- ─────────────────────────────────────────────────────────────

SELECT
    c.loyalty_tier,
    c.effective_date,
    c.expiry_date,
    SUM(f.revenue)             AS total_revenue,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_sales       f
JOIN dim_customer_v2  c ON c.customer_key = f.customer_key
GROUP BY c.loyalty_tier, c.customer_key, c.effective_date, c.expiry_date
ORDER BY c.customer_id, c.customer_version;

/*
Result shows Alice's Gold-era sales attributed to Gold,
and any future Platinum sales attributed to Platinum –
no historical data is lost or overwritten.
*/
