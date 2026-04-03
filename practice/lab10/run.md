# Запуск Lab 10 – Star Schema Analysis

## Требования

- PostgreSQL 14+ (или любая совместимая СУБД: MySQL, SQLite)
- Клиент: `psql`, DBeaver, pgAdmin или любой SQL-редактор

---

## Вариант 1 — через psql (командная строка)

```bash
# 1. Создать базу данных
psql -U postgres -c "CREATE DATABASE bookstore_dw;"

# 2. Подключиться к БД
psql -U postgres -d bookstore_dw

# 3. Создать схему и загрузить данные
\i 01_schema_and_data.sql

# 4. Запустить бизнес-запросы
\i 02_queries.sql

# 5. Запустить SCD Type 2
\i 03_scd_type2.sql
```

---

## Вариант 2 — через DBeaver / pgAdmin

1. Открыть DBeaver → создать новое подключение к PostgreSQL
2. Создать новую базу данных `bookstore_dw`
3. Открыть файл `01_schema_and_data.sql` → выполнить (Ctrl+Enter или F5)
4. Открыть файл `02_queries.sql` → выполнить каждый запрос отдельно
5. Открыть файл `03_scd_type2.sql` → выполнить

---

## Вариант 3 — SQLite (без установки сервера)

```bash
# Установить sqlite3 если нет
# Windows: скачать с https://sqlite.org/download.html

sqlite3 bookstore_dw.db < 01_schema_and_data.sql
sqlite3 bookstore_dw.db < 02_queries.sql
sqlite3 bookstore_dw.db < 03_scd_type2.sql
```

> Примечание: в SQLite `BOOLEAN` хранится как `INTEGER` (0/1), `LIMIT` работает так же.  
> Замените `DECIMAL(10,2)` на `REAL` если возникают ошибки.

---

## Порядок выполнения файлов

| Порядок | Файл | Что делает |
|---------|------|-----------|
| 1 | `01_schema_and_data.sql` | Создаёт таблицы, вставляет данные |
| 2 | `02_queries.sql` | Запускает 6 аналитических запросов |
| 3 | `03_scd_type2.sql` | Создаёт dim_customer_v2, меняет тир Alice Gold→Platinum |

---

## Ожидаемый вывод Q1 (проверка что всё работает)

```
   genre    | total_revenue
------------+--------------
 Fiction    |        239.97
 Science    |        119.97
 Self-Help  |         54.95
 Technology |         14.99
 History    |         12.99
```

Если видите эту таблицу — всё загрузилось корректно.
