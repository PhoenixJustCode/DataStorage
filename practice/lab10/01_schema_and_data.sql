-- ============================================================
-- LAB 10: Star Schema Analysis – Online Bookstore Data Warehouse
-- File 1: Schema creation and sample data loading
-- ============================================================

-- ─────────────────────────────────────────────
-- 1. DIMENSION TABLES
-- ─────────────────────────────────────────────

CREATE TABLE dim_product (
    product_key  INT            PRIMARY KEY,
    product_id   VARCHAR(20)    NOT NULL,
    title        VARCHAR(200)   NOT NULL,
    author       VARCHAR(100)   NOT NULL,
    genre        VARCHAR(50)    NOT NULL,
    price        DECIMAL(10,2)  NOT NULL
);

CREATE TABLE dim_customer (
    customer_key       INT           PRIMARY KEY,
    customer_id        VARCHAR(20)   NOT NULL,
    name               VARCHAR(100)  NOT NULL,
    email              VARCHAR(150)  NOT NULL,
    loyalty_tier       VARCHAR(20)   NOT NULL,   -- 'Bronze','Silver','Gold','Platinum'
    registration_date  DATE          NOT NULL
);

CREATE TABLE dim_date (
    date_key    INT          PRIMARY KEY,   -- format YYYYMMDD
    date        DATE         NOT NULL,
    year        INT          NOT NULL,
    quarter     INT          NOT NULL,
    month       INT          NOT NULL,
    month_name  VARCHAR(15)  NOT NULL,
    day_of_week VARCHAR(10)  NOT NULL
);

-- ─────────────────────────────────────────────
-- 2. FACT TABLE
-- ─────────────────────────────────────────────

CREATE TABLE fact_sales (
    sales_key    INT            PRIMARY KEY,
    order_id     INT            NOT NULL,
    product_key  INT            NOT NULL  REFERENCES dim_product(product_key),
    customer_key INT            NOT NULL  REFERENCES dim_customer(customer_key),
    date_key     INT            NOT NULL  REFERENCES dim_date(date_key),
    quantity     INT            NOT NULL,
    unit_price   DECIMAL(10,2)  NOT NULL,
    revenue      DECIMAL(10,2)  NOT NULL   -- denormalized: quantity * unit_price
);

-- ─────────────────────────────────────────────
-- 3. SAMPLE DATA – dim_product
-- ─────────────────────────────────────────────

INSERT INTO dim_product VALUES
(1, 'P001', 'The Great Gatsby',          'F. Scott Fitzgerald', 'Fiction',    49.99),
(2, 'P002', 'A Brief History of Time',   'Stephen Hawking',     'Science',    39.99),
(3, 'P003', 'To Kill a Mockingbird',     'Harper Lee',          'Fiction',    45.00),
(4, 'P004', 'The Pragmatic Programmer',  'David Thomas',        'Technology', 14.99),
(5, 'P005', 'Atomic Habits',             'James Clear',         'Self-Help',  10.99),
(6, 'P006', 'Sapiens',                   'Yuval Noah Harari',   'History',    12.99);

-- ─────────────────────────────────────────────
-- 4. SAMPLE DATA – dim_customer
-- ─────────────────────────────────────────────

INSERT INTO dim_customer VALUES
(1, 'C1001', 'Alice Johnson', 'alice@email.com',   'Gold',     '2022-03-15'),
(2, 'C1002', 'Bob Smith',     'bob@email.com',     'Silver',   '2021-07-20'),
(3, 'C1003', 'Carol White',   'carol@email.com',   'Platinum', '2020-01-10'),
(4, 'C1004', 'David Brown',   'david@email.com',   'Bronze',   '2023-11-05');

-- ─────────────────────────────────────────────
-- 5. SAMPLE DATA – dim_date
-- ─────────────────────────────────────────────

INSERT INTO dim_date VALUES
(20240115, '2024-01-15', 2024, 1, 1,  'January',  'Monday'),
(20240210, '2024-02-10', 2024, 1, 2,  'February', 'Saturday'),
(20240305, '2024-03-05', 2024, 1, 3,  'March',    'Tuesday'),
(20240401, '2024-04-01', 2024, 2, 4,  'April',    'Monday'),
(20240520, '2024-05-20', 2024, 2, 5,  'May',      'Monday');

-- ─────────────────────────────────────────────
-- 6. SAMPLE DATA – fact_sales  (matches screenshot)
-- ─────────────────────────────────────────────

INSERT INTO fact_sales VALUES
( 1, 1001, 1, 1, 20240115, 2, 49.99,  99.98),
( 2, 1001, 2, 1, 20240115, 1, 39.99,  39.99),
( 3, 1002, 4, 2, 20240210, 1, 14.99,  14.99),
( 4, 1003, 3, 3, 20240305, 1, 45.00,  45.00),
( 5, 1003, 5, 3, 20240305, 3, 10.99,  32.97),
( 6, 1004, 6, 4, 20240305, 1, 12.99,  12.99),
( 7, 1004, 1, 4, 20240305, 1, 49.99,  49.99),
( 8, 1005, 2, 2, 20240401, 2, 39.99,  79.98),
( 9, 1006, 3, 1, 20240520, 1, 45.00,  45.00),
(10, 1006, 5, 1, 20240520, 2, 10.99,  21.98);
