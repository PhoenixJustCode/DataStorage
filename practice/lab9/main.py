"""
Лабораторная работа 9: MongoDB — CRUD, Aggregation, Indexing
Использует pymongo для подключения к MongoDB Atlas / локальному серверу.
"""

from pymongo import MongoClient
from datetime import datetime

# ── Подключение ──────────────────────────────────────────────────────────────
# Замени <connection_string> на свою строку подключения MongoDB Atlas
# Пример: "mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/"
CONNECTION_STRING = "mongodb://localhost:27017/"
DB_NAME = "lab9"

client = MongoClient(CONNECTION_STRING)
db = client[DB_NAME]

products = db["products"]
orders = db["orders"]


#  
# Part 2: Sample Dataset
#  

def seed_data():
    """Очистка и заполнение коллекций начальными данными."""
    products.drop()
    orders.drop()

    # 2.1 — products
    products.insert_many([
        {"_id": 1, "name": "Laptop",       "price": 999.99, "category": "Electronics",
         "tags": ["computer", "portable"], "stock": 25},
        {"_id": 2, "name": "Smart Watch",  "price": 199.99, "category": "Electronics",
         "tags": ["wearable", "wireless"], "stock": 50},
        {"_id": 3, "name": "Desk Lamp",    "price": 34.99,  "category": "Home",
         "tags": ["lighting", "office"],   "stock": 100},
        {"_id": 4, "name": "Running Shoes","price": 89.99,  "category": "Sports",
         "tags": ["footwear", "running"],  "stock": 40},
        {"_id": 5, "name": "Headphones",   "price": 59.99,  "category": "Electronics",
         "tags": ["audio", "wireless"],    "stock": 75},
    ])

    # 2.2 — orders
    orders.insert_many([
        {"_id": 1, "customer": "Alice", "date": datetime(2025, 1, 15),
         "items": [{"productId": 1, "quantity": 1}, {"productId": 5, "quantity": 2}],
         "total": 1119.97, "status": "delivered"},
        {"_id": 2, "customer": "Bob",   "date": datetime(2025, 2, 3),
         "items": [{"productId": 2, "quantity": 1}],
         "total": 199.99,  "status": "shipped"},
        {"_id": 3, "customer": "Alice", "date": datetime(2025, 2, 20),
         "items": [{"productId": 3, "quantity": 3}, {"productId": 4, "quantity": 1}],
         "total": 194.96,  "status": "pending"},
        {"_id": 4, "customer": "Charlie", "date": datetime(2025, 3, 10),
         "items": [{"productId": 1, "quantity": 1}, {"productId": 2, "quantity": 1}],
         "total": 1199.98, "status": "pending"},
    ])
    print("=== Данные загружены ===\n")


#  
# Part 3: Basic CRUD Operations
#  

def part3_crud():
    print("─── Part 3: CRUD ───\n")

    # 3.1 Find
    # 1) Все продукты
    print("1) Все продукты:")
    for p in products.find():
        print("  ", p)

    # 2) Электроника — только name и price
    print("\n2) Электроника (name, price):")
    for p in products.find({"category": "Electronics"}, {"name": 1, "price": 1, "_id": 0}):
        print("  ", p)

    # 3) Цена > 50, сортировка по убыванию
    print("\n3) Цена > 50, сортировка desc:")
    for p in products.find({"price": {"$gt": 50}}).sort("price", -1):
        print("  ", p)

    # 3.2 Insert
    # 4) Вставка нового продукта
    products.insert_one({
        "_id": 6, "name": "Bluetooth Speaker", "price": 49.99,
        "category": "Electronics", "tags": ["speaker", "audio"], "stock": 60
    })
    print("\n4) Вставлен Bluetooth Speaker:")
    print("  ", products.find_one({"_id": 6}))

    # 3.3 Update
    # 5) Увеличить цену электроники на 10%
    result = products.update_many(
        {"category": "Electronics"},
        {"$mul": {"price": 1.1}}
    )
    print(f"\n5) Цена электроники +10%: обновлено {result.modified_count} документов")
    for p in products.find({"category": "Electronics"}, {"name": 1, "price": 1, "_id": 0}):
        print("  ", p)

    # 6) Добавить тег "best seller" к Smart Watch
    products.update_one(
        {"name": "Smart Watch"},
        {"$push": {"tags": "best seller"}}
    )
    print("\n6) Smart Watch после добавления тега:")
    print("  ", products.find_one({"name": "Smart Watch"}))

    # 3.4 Delete
    # 7) Удалить продукт с _id: 6
    products.delete_one({"_id": 6})
    print("\n7) Bluetooth Speaker удалён:", products.find_one({"_id": 6}) is None)

    # 8) Вставим продукт с малым stock и удалим все с stock < 10
    products.insert_one({"_id": 7, "name": "Old Cable", "price": 2.99,
                         "category": "Accessories", "tags": ["cable"], "stock": 3})
    result = products.delete_many({"stock": {"$lt": 10}})
    print(f"8) Удалено продуктов со stock < 10: {result.deleted_count}")


#  
# Part 4: Querying with Operators
#  

def part4_operators():
    print("\n─── Part 4: Operators ───\n")

    # 1) Цена от 20 до 100 включительно
    print("1) Цена 20..100:")
    for p in products.find({"price": {"$gte": 20, "$lte": 100}}):
        print("  ", p["name"], "—", round(p["price"], 2))

    # 2) Заказы со статусом pending или shipped
    print("\n2) Заказы pending/shipped:")
    for o in orders.find({"status": {"$in": ["pending", "shipped"]}}):
        print(f"  Order #{o['_id']}: {o['customer']} — {o['status']}")

    # 3) Продукты с тегом "wireless"
    print("\n3) Продукты с тегом 'wireless':")
    for p in products.find({"tags": "wireless"}):
        print("  ", p["name"])

    # 4) Заказы, где customer != Alice
    print("\n4) Заказы (customer ≠ Alice):")
    for o in orders.find({"customer": {"$ne": "Alice"}}):
        print(f"  Order #{o['_id']}: {o['customer']}")


#  
# Part 5: Aggregation Pipeline
#  

def part5_aggregation():
    print("\n─── Part 5: Aggregation ───\n")

    # 1) Общая выручка
    pipeline = [{"$group": {"_id": None, "totalRevenue": {"$sum": "$total"}}}]
    result = list(orders.aggregate(pipeline))
    print(f"1) Общая выручка: {result[0]['totalRevenue']:.2f}")

    # 2) Средний чек по клиенту
    pipeline = [
        {"$group": {"_id": "$customer",
                     "avgOrder": {"$avg": "$total"},
                     "count": {"$sum": 1}}},
        {"$sort": {"avgOrder": -1}}
    ]
    print("\n2) Средний чек по клиенту:")
    for r in orders.aggregate(pipeline):
        print(f"  {r['_id']}: avg={r['avgOrder']:.2f}, orders={r['count']}")

    # 3) Топ продуктов по количеству заказов (с $lookup)
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.productId", "totalQty": {"$sum": "$items.quantity"}}},
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$project": {"productName": "$product.name", "totalQty": 1}},
        {"$sort": {"totalQty": -1}}
    ]
    print("\n3) Топ продуктов:")
    for r in orders.aggregate(pipeline):
        print(f"  {r['productName']}: {r['totalQty']} шт.")

    # 4) Количество заказов по месяцам
    pipeline = [
        {"$group": {
            "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    print("\n4) Заказы по месяцам:")
    for r in orders.aggregate(pipeline):
        print(f"  {r['_id']['year']}-{r['_id']['month']:02d}: {r['count']} заказов")


#  
# Main
#  

if __name__ == "__main__":
    seed_data()
    part3_crud()
    part4_operators()
    part5_aggregation()

    client.close()
    print("\n=== Готово ===")
