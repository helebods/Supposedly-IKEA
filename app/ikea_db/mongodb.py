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
