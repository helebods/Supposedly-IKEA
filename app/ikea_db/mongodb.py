from app import mongo
from bson.objectid import ObjectId

# View All Items


def get_all_items():
    return list(mongo.db.ikeaunderscoreitems.find())

# Insert Item


def insert_item(Product_Name, Product_Brand, Product_Category,
                Product_Description, Product_image_url):
    Items = {
        "Product_Name": Product_Name,
        "Product_Brand": Product_Brand,
        "Product_Category": Product_Category,
        "Product_Description": Product_Description,
        "Product_image_url": Product_image_url
    }

    mongo.db.ikeaunderscoreitems.insert_one(Items)

    return True

# Update Item


def update_Item(item_id, Product_Name, Product_Brand, Product_Category,
                Product_Description, Product_image_url):
    updated_Item = {
        "Product_Name": Product_Name,
        "Product_Brand": Product_Brand,
        "Product_Category": Product_Category,
        "Product_Description": Product_Description,
        "Product_image_url": Product_image_url}

    mongo.db.ikeaunderscoreitems.update_one(
        {"_id": ObjectId(item_id)}, {"$set": updated_Item})

    return True

# Delete Item


def delete_item(item_id):
    mongo.db.ikeaunderscoreitems.delete_one({"_id": ObjectId(item_id)})
    return True
