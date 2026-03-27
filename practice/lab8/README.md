# Lab 8 — Online Bookstore Database

## Overview

This lab implements a relational database for an online bookstore using **SQLite** (via Python's built-in `sqlite3` module). It covers the full lifecycle: conceptual design, DDL, data insertion, and SQL queries.

---

## Part A — Conceptual Questions

### 1. Relational vs NoSQL

| Feature | Relational (SQL) | Non-relational (NoSQL) |
|---|---|---|
| Schema | Fixed, predefined | Flexible, schema-less |
| Data model | Tables with rows/columns | Documents, key-value, graphs, etc. |
| Relationships | Foreign keys, JOINs | Usually denormalized |
| Transactions | ACID guaranteed | Eventual consistency (often) |
| Scaling | Vertical (mostly) | Horizontal (designed for it) |

**SQL example:** a banking system where transactions must be atomic and consistent.
**NoSQL example:** a social media feed where schema varies per post type and scale is massive.

### 2. Why Relational for a Bookstore?

A bookstore has clear, structured relationships: books ↔ authors (many-to-many), orders ↔ customers (many-to-one), orders ↔ books (many-to-many via order items). ACID transactions are critical when placing orders (deduct stock + create order atomically). SQL is the right choice here.

### 3. ACID Properties

| Property | Meaning |
|---|---|
| **Atomicity** | A transaction is all-or-nothing (e.g., payment + order creation both succeed or both fail) |
| **Consistency** | The database moves from one valid state to another (constraints are never violated) |
| **Isolation** | Concurrent transactions don't interfere with each other |
| **Durability** | Committed transactions survive crashes |

For a bookstore, ACID ensures that an order is never created without a matching payment, and stock is never decremented without a committed order.

### 4. Primary Key vs Foreign Key

- **Primary key** — uniquely identifies each row in a table. Example: `customer_id` in `Customers`.
- **Foreign key** — references a primary key in another table to enforce referential integrity. Example: `Orders.customer_id` references `Customers.customer_id`.

### 5. Normalization and Data Redundancy

Redundancy wastes storage and causes update anomalies (changing an author's name in one place but not another). Normalization splits data into well-defined tables so each fact is stored once. For example, storing `publisher` data in a separate table means updating a publisher name requires changing only one row.

---

## Part B — Relational Schema

### ER Summary

- **Authors** `(author_id PK, name, birth_year)`
- **Books** `(isbn PK, title, publisher, publication_year, price, stock_qty)`
- **BookAuthors** `(isbn FK, author_id FK)` — junction table for M:N between Books and Authors
- **Customers** `(customer_id PK, name, email UNIQUE, address, registration_date)`
- **Orders** `(order_id PK, customer_id FK, order_date, total_amount, status)`
- **OrderItems** `(order_item_id PK, order_id FK, isbn FK, quantity, price_at_order)`

### Cardinalities

- Author — Book: **M:N** (via BookAuthors)
- Customer — Order: **1:N**
- Order — Book: **M:N** (via OrderItems)

---

## Part C — DDL (Create Tables)

```sql
CREATE TABLE Authors (
    author_id   INTEGER      PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL,
    birth_year  INTEGER
);

CREATE TABLE Books (
    isbn             VARCHAR(20)   PRIMARY KEY,
    title            VARCHAR(200)  NOT NULL,
    publisher        VARCHAR(100),
    publication_year INTEGER,
    price            DECIMAL(10,2) NOT NULL CHECK(price >= 0),
    stock_qty        INTEGER       NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
);

CREATE TABLE BookAuthors (
    isbn       VARCHAR(20) NOT NULL REFERENCES Books(isbn)       ON DELETE CASCADE ON UPDATE CASCADE,
    author_id  INTEGER     NOT NULL REFERENCES Authors(author_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (isbn, author_id)
);

CREATE TABLE Customers (
    customer_id       INTEGER      PRIMARY KEY AUTOINCREMENT,
    name              VARCHAR(100) NOT NULL,
    email             VARCHAR(150) NOT NULL UNIQUE,
    address           TEXT,
    registration_date DATE         NOT NULL
);

CREATE TABLE Orders (
    order_id     INTEGER      PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER      NOT NULL REFERENCES Customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    order_date   DATE         NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status       VARCHAR(20)  NOT NULL DEFAULT 'pending'
                 CHECK(status IN ('pending','shipped','delivered','cancelled'))
);

CREATE TABLE OrderItems (
    order_item_id  INTEGER      PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER      NOT NULL REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    isbn           VARCHAR(20)  NOT NULL REFERENCES Books(isbn)      ON DELETE RESTRICT ON UPDATE CASCADE,
    quantity       INTEGER      NOT NULL CHECK(quantity > 0),
    price_at_order DECIMAL(10,2) NOT NULL CHECK(price_at_order >= 0)
);
```

**ON DELETE / ON UPDATE choices:**

| Relationship | Action | Reason |
|---|---|---|
| BookAuthors → Books/Authors | CASCADE | Deleting a book/author removes the link |
| OrderItems → Orders | CASCADE | Deleting an order removes its line items |
| Orders → Customers | RESTRICT | Cannot delete a customer with existing orders |
| OrderItems → Books | RESTRICT | Cannot delete a book that was ordered |

---

## Part D — Sample Data

The script inserts:
- 5 authors (Orwell, Herbert, Rowling, Adams, Pratchett)
- 10 books (including *Good Omens* with two authors — Adams + Pratchett)
- 5 customers
- 8 orders (spanning Jan–Mar 2024, various statuses)
- 15 order items (1–3 per order)

---

## Part E — Queries

| # | Question |
|---|---|
| Q1 | All books with author(s) and price (JOIN + GROUP_CONCAT) |
| Q2 | Customers registered in 2023 |
| Q3 | Pending orders in the last 30 days (ref date: 2024-03-01) |
| Q4 | Number of books per author |
| Q5 | Total orders per customer (descending) |
| Q6 | Total revenue from OrderItems |
| Q7 | Top 3 best-selling books by quantity |
| Q8 | Customers who spent more than $100 total |
| Q9 | Monthly order count and sales for 2024 |

---

## How to Run

```bash
python main.py
```

No external dependencies — only Python's standard library (`sqlite3`).
The database is created in-memory by default. To persist it, change `DB_PATH` in `main.py`:

```python
DB_PATH = "bookstore.db"   # creates a file on disk
```
