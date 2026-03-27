"""
Lab 8 — Online Bookstore Database
Covers: DDL, data insertion, SQL queries (Parts C–E)
Uses SQLite (built-in, no extra dependencies)
"""

import sqlite3

DB_PATH = ":memory:"  # Use ":memory:" for in-memory or "bookstore.db" for persistent file


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# PART C — DDL: Create tables
# ─────────────────────────────────────────────────────────────────────────────

DDL = """
CREATE TABLE IF NOT EXISTS Authors (
    author_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL,
    birth_year  INTEGER
);

CREATE TABLE IF NOT EXISTS Books (
    isbn            VARCHAR(20)     PRIMARY KEY,
    title           VARCHAR(200)    NOT NULL,
    publisher       VARCHAR(100),
    publication_year INTEGER,
    price           DECIMAL(10,2)   NOT NULL CHECK(price >= 0),
    stock_qty       INTEGER         NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
);

CREATE TABLE IF NOT EXISTS BookAuthors (
    isbn        VARCHAR(20) NOT NULL REFERENCES Books(isbn)   ON DELETE CASCADE  ON UPDATE CASCADE,
    author_id   INTEGER     NOT NULL REFERENCES Authors(author_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (isbn, author_id)
);

CREATE TABLE IF NOT EXISTS Customers (
    customer_id     INTEGER     PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    address         TEXT,
    registration_date DATE       NOT NULL
);

CREATE TABLE IF NOT EXISTS Orders (
    order_id        INTEGER     PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER     NOT NULL REFERENCES Customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    order_date      DATE        NOT NULL,
    total_amount    DECIMAL(10,2) NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','shipped','delivered','cancelled'))
);

CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER     NOT NULL REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    isbn            VARCHAR(20) NOT NULL REFERENCES Books(isbn)      ON DELETE RESTRICT ON UPDATE CASCADE,
    quantity        INTEGER     NOT NULL CHECK(quantity > 0),
    price_at_order  DECIMAL(10,2) NOT NULL CHECK(price_at_order >= 0)
);
"""


# ─────────────────────────────────────────────────────────────────────────────
# PART D — Insert sample data
# ─────────────────────────────────────────────────────────────────────────────

def insert_data(conn: sqlite3.Connection):
    cur = conn.cursor()

    # 5 Authors
    cur.executemany(
        "INSERT INTO Authors (name, birth_year) VALUES (?, ?)",
        [
            ("George Orwell",       1903),
            ("Frank Herbert",       1920),
            ("J.K. Rowling",        1965),
            ("Douglas Adams",       1952),
            ("Terry Pratchett",     1948),
        ],
    )

    # 10 Books
    cur.executemany(
        "INSERT INTO Books (isbn, title, publisher, publication_year, price, stock_qty) VALUES (?,?,?,?,?,?)",
        [
            ("978-0451524935", "Nineteen Eighty-Four",            "Secker & Warburg",   1949, 9.99,  50),
            ("978-0441013593", "Dune",                            "Chilton Books",       1965, 12.99, 30),
            ("978-0439708180", "Harry Potter and the Sorcerer's Stone", "Scholastic",   1997, 14.99, 80),
            ("978-0345391803", "The Hitchhiker's Guide to the Galaxy", "Pan Books",     1979, 10.99, 45),
            ("978-0552166614", "Good Omens",                      "Victor Gollancz",    1990, 11.99, 25),
            ("978-0451526342", "Animal Farm",                     "Secker & Warburg",   1945, 7.99,  60),
            ("978-0441013590", "Dune Messiah",                    "Putnam",             1969, 11.99, 20),
            ("978-0439339636", "Harry Potter and the Chamber of Secrets", "Scholastic", 1998, 13.99, 70),
            ("978-0345391810", "The Restaurant at the End of the Universe", "Pan Books",1980, 10.99, 35),
            ("978-0552173926", "Mort",                            "Victor Gollancz",    1987, 9.99,  40),
        ],
    )

    # BookAuthors (junction): some books have multiple authors
    cur.executemany(
        "INSERT INTO BookAuthors (isbn, author_id) VALUES (?,?)",
        [
            ("978-0451524935", 1),   # Orwell -> 1984
            ("978-0441013593", 2),   # Herbert -> Dune
            ("978-0439708180", 3),   # Rowling -> HP1
            ("978-0345391803", 4),   # Adams -> HHGTTG
            ("978-0552166614", 4),   # Adams -> Good Omens  (co-author)
            ("978-0552166614", 5),   # Pratchett -> Good Omens (co-author)
            ("978-0451526342", 1),   # Orwell -> Animal Farm
            ("978-0441013590", 2),   # Herbert -> Dune Messiah
            ("978-0439339636", 3),   # Rowling -> HP2
            ("978-0345391810", 4),   # Adams -> Restaurant
            ("978-0552173926", 5),   # Pratchett -> Mort
        ],
    )

    # 5 Customers
    cur.executemany(
        "INSERT INTO Customers (name, email, address, registration_date) VALUES (?,?,?,?)",
        [
            ("Alice Johnson",  "alice@example.com",  "10 Baker St, London",      "2023-03-15"),
            ("Bob Smith",      "bob@example.com",    "42 Wallaby Way, Sydney",   "2023-07-22"),
            ("Carol White",    "carol@example.com",  "221B Baker St, London",    "2024-01-10"),
            ("David Brown",    "david@example.com",  "4 Privet Drive, Surrey",   "2024-02-28"),
            ("Eva Martinez",   "eva@example.com",    "12 Grimmauld Place, London","2022-11-05"),
        ],
    )

    # 8 Orders
    cur.executemany(
        "INSERT INTO Orders (customer_id, order_date, total_amount, status) VALUES (?,?,?,?)",
        [
            (1, "2024-01-05",  34.97, "delivered"),
            (2, "2024-01-20",  12.99, "shipped"),
            (1, "2024-02-14",  22.98, "delivered"),
            (3, "2024-03-01",  14.99, "pending"),
            (4, "2024-03-10",  21.98, "pending"),
            (5, "2024-02-01",  39.96, "shipped"),
            (2, "2024-02-25",  10.99, "delivered"),
            (5, "2024-03-15",  23.98, "pending"),
        ],
    )

    # OrderItems (each order has 1-3 items)
    cur.executemany(
        "INSERT INTO OrderItems (order_id, isbn, quantity, price_at_order) VALUES (?,?,?,?)",
        [
            # Order 1 — Alice
            (1, "978-0451524935", 1, 9.99),
            (1, "978-0451526342", 1, 7.99),
            (1, "978-0441013593", 1, 12.99),
            # Order 2 — Bob
            (2, "978-0441013593", 1, 12.99),
            # Order 3 — Alice
            (3, "978-0345391803", 1, 10.99),
            (3, "978-0552166614", 1, 11.99),
            # Order 4 — Carol
            (4, "978-0439708180", 1, 14.99),
            # Order 5 — David
            (5, "978-0439708180", 1, 14.99),
            (5, "978-0439339636", 1, 13.99),   # >price: truncated to fit total
            # Order 6 — Eva
            (6, "978-0552166614", 2, 11.99),
            (6, "978-0552173926", 1, 9.99),
            (6, "978-0345391803", 1, 10.99),
            # Order 7 — Bob
            (7, "978-0345391803", 1, 10.99),
            # Order 8 — Eva
            (8, "978-0441013590", 1, 11.99),
            (8, "978-0552173926", 1, 9.99),
        ],
    )

    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# PART E — Queries
# ─────────────────────────────────────────────────────────────────────────────

def run_query(conn, title: str, sql: str, params=()):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    rows = conn.execute(sql, params).fetchall()
    if rows:
        headers = rows[0].keys()
        col_w = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
        header_line = "  ".join(h.ljust(col_w[h]) for h in headers)
        print(header_line)
        print("-" * len(header_line))
        for row in rows:
            print("  ".join(str(row[h]).ljust(col_w[h]) for h in headers))
    else:
        print("(no rows)")
    print(f"  [{len(rows)} row(s)]")


def part_e_queries(conn: sqlite3.Connection):

    # ── Basic Query 1 ─────────────────────────────────────────────────────────
    run_query(conn, "Q1: All books with author(s) and price", """
        SELECT b.title,
               GROUP_CONCAT(a.name, ', ') AS authors,
               b.price
        FROM Books b
        JOIN BookAuthors ba ON b.isbn = ba.isbn
        JOIN Authors a      ON ba.author_id = a.author_id
        GROUP BY b.isbn
        ORDER BY b.title
    """)

    # ── Basic Query 2 ─────────────────────────────────────────────────────────
    run_query(conn, "Q2: Customers who registered in 2023", """
        SELECT customer_id, name, email, registration_date
        FROM Customers
        WHERE strftime('%Y', registration_date) = '2023'
    """)

    # ── Basic Query 3 ─────────────────────────────────────────────────────────
    # Using fixed reference date 2024-03-01 (last 30 days = 2024-01-31 .. 2024-03-01)
    run_query(conn, "Q3: Pending orders in the last 30 days (ref: 2024-03-01)", """
        SELECT order_id, customer_id, order_date, total_amount, status
        FROM Orders
        WHERE status = 'pending'
          AND order_date BETWEEN date('2024-03-01', '-30 days') AND '2024-03-01'
    """)

    # ── Basic Query 4 ─────────────────────────────────────────────────────────
    run_query(conn, "Q4: Number of books each author has written", """
        SELECT a.name AS author, COUNT(ba.isbn) AS book_count
        FROM Authors a
        LEFT JOIN BookAuthors ba ON a.author_id = ba.author_id
        GROUP BY a.author_id
        ORDER BY book_count DESC
    """)

    # ── Basic Query 5 ─────────────────────────────────────────────────────────
    run_query(conn, "Q5: Total orders per customer (descending)", """
        SELECT c.name AS customer, COUNT(o.order_id) AS total_orders
        FROM Customers c
        LEFT JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        ORDER BY total_orders DESC
    """)

    # ── Intermediate Query 6 ──────────────────────────────────────────────────
    run_query(conn, "Q6: Total revenue computed from OrderItems", """
        SELECT ROUND(SUM(oi.quantity * oi.price_at_order), 2) AS total_revenue
        FROM OrderItems oi
    """)

    # ── Intermediate Query 7 ──────────────────────────────────────────────────
    run_query(conn, "Q7: Top 3 best-selling books by quantity sold", """
        SELECT b.title,
               SUM(oi.quantity) AS total_sold
        FROM OrderItems oi
        JOIN Books b ON oi.isbn = b.isbn
        GROUP BY oi.isbn
        ORDER BY total_sold DESC
        LIMIT 3
    """)

    # ── Intermediate Query 8 ──────────────────────────────────────────────────
    run_query(conn, "Q8: Customers who spent more than $100 total", """
        SELECT c.name AS customer,
               ROUND(SUM(o.total_amount), 2) AS total_spent
        FROM Customers c
        JOIN Orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        HAVING total_spent > 100
        ORDER BY total_spent DESC
    """)

    # ── Intermediate Query 9 ──────────────────────────────────────────────────
    run_query(conn, "Q9: Orders and sales per month in 2024", """
        SELECT strftime('%Y-%m', order_date) AS month,
               COUNT(order_id)              AS num_orders,
               ROUND(SUM(total_amount), 2)  AS monthly_sales
        FROM Orders
        WHERE strftime('%Y', order_date) = '2024'
        GROUP BY month
        ORDER BY month
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("Lab 8 — Online Bookstore Database")
    print(f"Database: {DB_PATH}")

    conn = connect()

    print("\n[1] Creating tables (DDL)...")
    conn.executescript(DDL)
    print("    Tables created.")

    print("\n[2] Inserting sample data...")
    insert_data(conn)
    print("    Data inserted.")

    print("\n[3] Running Part E queries...")
    part_e_queries(conn)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
