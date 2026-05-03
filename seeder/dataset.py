import os
import random
import uuid
import shutil
from faker import Faker
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId   # ✅ FIX

fake = Faker()

# =====================================================
# ROOT PATH
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_IMAGE_PATH = os.path.join(BASE_DIR, "datasetss", "images")
FLASK_UPLOAD_PATH = os.path.join(BASE_DIR, "app", "static", "uploads")

os.makedirs(FLASK_UPLOAD_PATH, exist_ok=True)

# =====================================================
# MONGODB
# =====================================================
client = MongoClient("mongodb://localhost:27017/")
db = client["quibs_inventory"]

items_collection = db["items"]
# orders_collection = db["orders"]

# =====================================================
# CONFIG
# =====================================================
CATEGORIES = ["electronics", "office supplies", "furniture", "tools"]

PRODUCTS = {
    "electronics": ["wireless mouse", "keyboard", "usb hub", "monitor"],
    "office supplies": ["notebook", "stapler", "folder", "marker"],
    "furniture": ["office chair", "desk", "cabinet", "bookshelf"],
    "tools": ["hammer", "drill", "wrench", "pliers"]
}

BRANDS = {
    "electronics": ["Logitech", "Anker", "JBL", "Sony"],
    "office supplies": ["Pilot", "Deli", "Faber-Castell"],
    "furniture": ["Ikea", "Steelcase"],
    "tools": ["Bosch", "Makita", "DeWalt"]
}

# =====================================================
# IMAGE HANDLING
# =====================================================
def get_dataset_image(category, product):
    folder = os.path.join(DATASET_IMAGE_PATH, category, product)

    if not os.path.exists(folder):
        return None

    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    return random.choice(images) if images else None


def simulate_upload(file_path):
    if not file_path:
        return "image0.jpg"

    ext = os.path.splitext(file_path)[1]
    filename = f"{uuid.uuid4()}{ext}"

    dest = os.path.join(FLASK_UPLOAD_PATH, filename)
    shutil.copy(file_path, dest)

    return filename

# =====================================================
# GEO
# =====================================================
def get_random_point():
    return {
        "type": "Point",
        "coordinates": [
            random.uniform(120.90, 121.10),
            random.uniform(15.40, 15.60)
        ]
    }

# =====================================================
# PRODUCT
# =====================================================
def generate_product():
    category = random.choice(CATEGORIES)
    product_name = random.choice(PRODUCTS[category])

    img = get_dataset_image(category, product_name)
    uploaded_file = simulate_upload(img)

    return category, {
        "Product_Name": product_name.title(),
        "Product_Brand": random.choice(BRANDS[category]),
        "Product_Category": category,
        "Product_Description": fake.sentence(),
        "Product_image_url": uploaded_file
    }

# =====================================================
# RECORD
# =====================================================
def generate_record():
    category, product = generate_product()

    quantity = random.randint(5, 200)
    cost = round(random.uniform(5, 100), 2)

    return {
        "product": product,
        "location": {
            "warehouse": random.choice(["WH-A", "WH-B", "WH-C"]),
            "aisle": f"A{random.randint(1,5)}",
            "rack": f"R{random.randint(1,5)}",
            "bin": f"B{random.randint(1,20)}",
            "geo": get_random_point()
        },
        "stock": {
            "quantity": quantity,
            "unit": "pcs",
            "reorder_level": random.randint(5, 20)
        },
        "price": {
            "cost": cost,
            "selling_price": round(cost * random.uniform(1.2, 2.0), 2)
        },
        "stock_history": [
            {
                "type": "IN",
                "quantity": quantity,
                "date": datetime.utcnow(),
                "user_id": "admin"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# # =====================================================
# # ORDER SYSTEM (FIXED)
# # =====================================================
# def generate_order_number():
#     count = orders_collection.count_documents({})
#     return f"ORD-{count+1:04d}"


# def build_order(items, total_cost, ordered_by):
#     return {
#         "order_number": generate_order_number(),
#         "ordered_by": ObjectId(ordered_by),
#         "items": [
#             {
#                 "item_id": ObjectId(item["item_id"]),
#                 "product_name": item["product_name"],
#                 "quantity": int(item["quantity"]),
#                 "unit_cost": float(item["unit_cost"]),
#                 "total_cost": float(item["total_cost"])
#             }
#             for item in items
#         ],
#         "created_at": datetime.utcnow()
#     }


# def insert_order(user_id, items, total_cost):
#     order = build_order(items, total_cost, user_id)
#     orders_collection.insert_one(order)
#     print("Order inserted:", order["order_number"])

# =====================================================
# SEED
# =====================================================
def seed(n=50):
    data = [generate_record() for _ in range(n)]
    items_collection.insert_many(data)
    print(f"Inserted {n} records")


if __name__ == "__main__":
    seed()