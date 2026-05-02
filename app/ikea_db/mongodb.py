from flask import current_app

from app import mongo
from bson.objectid import ObjectId
from datetime import datetime
import os

# View All Items
def get_all_items(query=None, projection=None, sort=None, limit=None):
    if query is None:
        query = {}

    cursor = mongo.db["items"].find(query, projection)

    if sort:
        cursor = cursor.sort(sort)

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)


def find_by_product_name(name):
    return list(mongo.db["items"].find({"product.Product_Name": name}))


def find_with_include_projection(include_fields):
    projection = {field: 1 for field in include_fields}
    projection["_id"] = 1
    projection["product.Product_image_url"] = 1
    projection["stock.quantity"] = 1
    projection["stock.unit"] = 1
    projection["price.cost"] = 1
    return list(mongo.db["items"].find({}, projection))


def find_with_exclude_projection(exclude_fields):
    projection = {field: 0 for field in exclude_fields}
    return list(mongo.db["items"].find({}, projection))


def find_by_category_with_include(category, include_fields):
    projection = {field: 1 for field in include_fields}
    projection["_id"] = 1
    projection["product.Product_image_url"] = 1
    projection["stock.quantity"] = 1
    projection["stock.unit"] = 1
    projection["price.cost"] = 1
    return list(mongo.db["items"].find({"product.Product_Category": category}, projection))


def find_by_category_with_exclude(category, exclude_fields):
    projection = {field: 0 for field in exclude_fields}
    return list(mongo.db["items"].find({"product.Product_Category": category}, projection))

def get_manage_items():
    projection = {
        "product.Product_Name": 1,
        "product.Product_Brand": 1,
        "product.Product_Category": 1,
        "product.Product_image_url": 1,
        "_id": 1
    }
    return list(mongo.db["items"].find({}, projection))

def get_recent_items(limit=3):
    return list(
        mongo.db["items"]
        .find()
        .sort("_id", -1)
        .limit(limit)
    )


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
        "quantity": int(quantity),
        "unit": unit,
        "reorder_level": int(reorder_level)
    }


def build_pricing(cost, selling_price):
    return {
        "cost": float(cost),
        "selling_price": float(selling_price)
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
            datetime.now(),
            data.get("user_id", "admin")
        ),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
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
        "updated_at": datetime.now()
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
        item = mongo.db["items"].find_one({"_id": ObjectId(product_Id)})

        if item:
            filename = item.get("product", {}).get("Product_image_url")

        # delete file if exists and not default image
        try:
            if filename and filename != "quibolords.jpg":
                file_path = os.path.join(
                    current_app.root_path,
                    "static/uploads",
                    filename
                )

                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print("Error occurred while deleting file:", e)

        result = mongo.db["items"].delete_one(
            {"_id": ObjectId(product_Id)})
        return result.deleted_count > 0

    except Exception as e:
        print("Error occurred while deleting item:", e)
        return False


def add_user(first_name, last_name, email, password):
    if mongo.db["users"].find_one({"credentials.email": email}):
        print("User already exists:", email)
        return False

    user = {
        "first_name": first_name,
        "last_name": last_name,
        "credentials": {
            "email": email,
            "password": password
        }
    }

    mongo.db["users"].insert_one(user)

    return True


def login_user(email, password):
    user = mongo.db["users"].find_one({"credentials.email": email})

    if not user:
        print("User not found:", email)
        return None

    if user["credentials"]["password"] == password:
        print("Login successful:", user["credentials"]["email"])
        return user
    else:
        print("Password mismatch:", email)
        return None


# aggregate functions for all items page
def count_total_items():
    return mongo.db["items"].count_documents({})

def average_selling_price():
    pipeline = [
        {"$group": {"_id": None, "avgSellingPrice": {"$avg": "$price.selling_price"}}}
    ]
    result = list(mongo.db["items"].aggregate(pipeline))
    return result[0]["avgSellingPrice"] if result else 0


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


def build_keyword_pattern(user_input):
    keyword = [k.strip() for k in user_input.replace(",", " ").split()]
    return keyword


def build_or_clause(keywords):
    return {
        "$or": [
            {"product.Product_Name": {"$regex": keywords, "$options": "i"}}
            # {"product.Product_Brand": {"$regex": keywords, "$options": "i"}},
            # {"product.Product_Category": {"$regex": keywords, "$options": "i"}}
        ]
    }


def build_search_query(user_input):
    if not user_input:
        return {}
    keywords = build_keyword_pattern(user_input)
    return {"$and": [build_or_clause(kw) for kw in keywords]}


def search_items(user_input):
    # add the aggregate=None to parameters, and also add a user_input=None
    # pipeline = []
    query = build_search_query(user_input)
    # if query:
    #     pipeline.append({"$match": query})
    # if aggregate:
    #     pipeline.append(aggregate)
    return list(mongo.db["items"].find(query, {"_id": 0}))


# other find function this is so useless fr

# dis kinda useful for low stock view
# this is for  db.<collection>.find({“parameter”},{attribute:1})
# for low stock view can be used for dashboard or ordering function to help user to orde the rightprod

def get_low_stock():
    prediction = {
        "product.Product_Name": 1,
        "stock.quantity": 1,
        "stock.unit": 1,
        "stock.reorder_level": 1,
        "location": 1,
        "_id": 1
    }
    return list(mongo.db["items"].find(
        {"$expr": {"$lt": ["$stock.quantity", "$stock.reorder_level"]}},
        prediction
    ))


# db.<collection>.find({ },{attribute:1})
# for manage items back end


# find({"parameter"}, {attribute: 0})
# for insert page to check if item already exists, if it does then we can just update the stock and price instead of creating a new entry


def check_existing_item(name):
    return mongo.db["items"].find_one(
        {"product.Product_Name": {"$regex": name, "$options": "i"}},
        {"price": 0, "stock_history": 0, "location": 0, "_id": 0}
    )


def format_aggregate_result(result, toggle):
    grouped = ["count_per_category", "count_per_name", "count_per_brand"]
    single = ["average_selling_price", "min_quantity", "max_quantity"]

    if toggle in grouped:
        return [{"label": r["_id"], "value": r["count"]} for r in result]

    if toggle in single and result:
        r = result[0]
        value = next(v for k, v in r.items() if k != "_id")
        return [{"label": toggle, "value": round(value, 2) if isinstance(value, float) else value}]
    return result

def get_item_by_id(item_id):
    return mongo.db["items"].find_one({"_id": ObjectId(item_id)})


# def aggregate_items_by_brand():
#     pipeline = [
#         {
#             "$group": {
#                 "_id": "$product.Product_Brand",
#                 "count": {"$sum": 1}
#             }
#         },
#         {
#             "$sort": {"_id": 1}
#         }
#     ]
#     return list(mongo.db["items"].aggregate(pipeline))


def generate_order_number():
    count = mongo.db["orders"].count_documents({})
    return f"ORD-{count+1:04d}"

def build_order(items, total_cost, ordered_by):
    return {
        "order_number": generate_order_number(),
        "ordered_by": ObjectId(ordered_by),
        "items":[
            {
            "item_id": ObjectId(item["item_id"]),
            "product_name": item["product_name"],
            "quantity": int(item["quantity"]),
            "unit_cost": float(item["unit_cost"]),
            "total_cost": float(total_cost)
            }
            for item in items
        ],
        "created_at": datetime.now()
    }

def insert_order(user_id, items, total_cost):
    print(">>> insert_order called", user_id, items, total_cost)
    order = build_order(items, total_cost, user_id)
    print(">>> order built:", order)  # ← and this
    mongo.db["orders"].insert_one(order)
    return True 

def get_orders_by_user(user_id):
    return list(mongo.db["orders"].find({"ordered_by": ObjectId(user_id)}))
