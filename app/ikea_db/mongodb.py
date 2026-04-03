from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

# View All Items


def get_all_items():
    return list(mongo.db["items"].find())

# Insert Item


def build_product(Product_Name, Product_Brand, Product_Category, Product_Description, File_Name):
    return {
        "Product_Name": Product_Name,
        "Product_Brand": Product_Brand,
        "Product_Category": Product_Category,
        "Product_Description": Product_Description,
        "Product_image_url": File_Name
    }


def build_location(warehouse, aisle, rack, bin):
    return {
        "warehouse": warehouse,
        "aisle": aisle,
        "rack": rack,
        "bin": bin
    }


def build_stock(quantity, unit, reorder_level):
    return {
        "quantity": quantity,
        "unit": unit,
        "reorder_level": reorder_level
    }


def build_pricing(cost, selling_price):
    return {
        "cost": cost,
        "selling_price": selling_price
    }


def build_stock_history(type, quantity, date, handled_by):
    return {
        "type": type,
        "quantity": quantity,
        "date": date,
        "handled_by": handled_by
    }


def insert_product(data):

    item = {
        "product": build_product(
            data.get("Product_Name"),
            data.get("Product_Brand"),
            data.get("Product_Category"),
            data.get("Product_Description"),
            data.get("image_url")
        ),
        "location": build_location(
            data.get("warehouse"),
            data.get("aisle"),
            data.get("rack"),
            data.get("bin")
        ),
        "stock": build_stock(
            int(data.get("quantity")),
            data.get("unit"),
            int(data.get("reorder_level"))
        ),
        "price": build_pricing(
            float(data.get("cost")),
            float(data.get("selling_price"))
        ),
        "stock_history": build_stock_history(
            "IN",
            int(data.get("quantity")),
            datetime.utcnow(),
            data.get("user_id", "admin")
        ),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    mongo.db["items"].insert_one(item)
    return True

# Update Item


def update_One_Item(product_Id, data):
    updated_Item = {
        "stock": build_stock(
            int(data.get("quantity")),
            data.get("unit"),
            int(data.get("reorder_level"))
        ),
        "price": build_pricing(
            float(data.get("cost")),
            float(data.get("selling_price"))
        ),
        "updated_at": datetime.utcnow()
    }

    result = mongo.db["items"].update_one(
        {
            "_id": ObjectId(product_Id)
        },
        {
            "$set": updated_Item
        }
    )

    return result.modified_count > 0

# Delete Item


def delete_One_Item(product_Id):
    try:
        result = mongo.db["items"].delete_one(
            {"_id": ObjectId(product_Id)})
        return result.deleted_count > 0

    except Exception as e:
        print("Error occurred while deleting item:", e)
        return False


def add_user(first_name, last_name, email, password):
    if mongo.db["users"].find_one({"email": email}):
        print("User already exists:", email)
        return False

    user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

    mongo.db["users"].insert_one(user)

    return True


def login_user(email, password):
    user = mongo.db["users"].find_one({"email": email})

    if not user:
        print("User not found:", email)
        return None

    if user["password"] == password:
        print("Login successful:", user["email"])
        return user
    else:
        print("Password mismatch:", email)
        return None


# aggregate functions for all items page
def count_total_items():
    return mongo.db["items"].count_documents({})


def count_per_category():
    pipeline = [
        {"$group": {"_id": "$product.Product_Category", "count": {"$sum": 1}}}
    ]
    return list(mongo.db["items"].aggregate(pipeline))


def count_per_name():
    pipeline = [
        {"$group": {"_id": "$product.Product_Name", "count": {"$sum": 1}}}
    ]
    return list(mongo.db["items"].aggregate(pipeline))


def count_per_brand():
    pipeline = [
        {"$group": {"_id": "$product.Product_Brand", "count": {"$sum": 1}}}
    ]
    return list(mongo.db["items"].aggregate(pipeline))


def average_selling_price():
    pipeline = [
        {"$group": {"_id": None, "avgPrice": {"$avg": "$price.selling_price"}}}
    ]
    result = list(mongo.db["items"].aggregate(pipeline))
    return round(result[0]["avgPrice"], 2) if result else 0


def min_quantity():
    pipeline = [
        {"$group": {"_id": None, "minQty": {"$min": "$stock.quantity"}}}
    ]
    result = list(mongo.db["items"].aggregate(pipeline))
    return result[0]["minQty"] if result else 0


def max_quantity():
    pipeline = [
        {"$group": {"_id": None, "maxQty": {"$max": "$stock.quantity"}}}
    ]
    result = list(mongo.db["items"].aggregate(pipeline))
    return result[0]["maxQty"] if result else 0


def find_and_sort_by_price(item_name):
    return list(mongo.db["items"].find({"product.Product_Name": item_name}).sort("price.selling_price", 1))


def find_and_sort_by_quantity(item_name):
    return list(mongo.db["items"].find({"product.Product_Name": item_name}).sort("stock.quantity", 1))


def find_by_category(item_name, category):
    try:
        if category is None:
            return list(mongo.db["items"].find({"product.Product_Name": item_name}))
        elif category == category.get("Product_Category"):
            return list(mongo.db["items"].find({"product.Product_Name": item_name, "product.Product_Category": category}))
    except Exception as e:
        return False


def find_by_brand(item_name, brand):
    try:
        if brand is None:
            return list(mongo.db["items"].find({"product.Product_Name": item_name}))
        elif brand == brand.get("Product_Brand"):
            return list(mongo.db["items"].find({"product.Product_Name": item_name, "product.Product_Brand": brand}))
    except Exception as e:
        return False
