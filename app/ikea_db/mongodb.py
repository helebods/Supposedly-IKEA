from app import mongo
from bson.objectid import ObjectId

# View All Items


def get_all_items():
    return list(mongo.db.ikeaunderscoreitems.find())

# Insert Item


def insert_item(Product_Name, Product_Brand, Product_Category,
                Product_Description, File_Name):
    Items = {
        "Product_Name": Product_Name,
        "Product_Brand": Product_Brand,
        "Product_Category": Product_Category,
        "Product_Description": Product_Description,
        "Product_image_url": File_Name
    }

    mongo.db.ikeaunderscoreitems.insert_one(Items)

    return True

# Update Item


def update_Item(item_id, Product_Name, Product_Brand, Product_Category,
                Product_Description, File_Name):
    updated_Item = {
        "Product_Name": Product_Name,
        "Product_Brand": Product_Brand,
        "Product_Category": Product_Category,
        "Product_Description": Product_Description,
        "Product_image_url": File_Name
    }

    mongo.db.ikeaunderscoreitems.update_one(
        {"_id": ObjectId(item_id)}, {"$set": updated_Item})

    return True

# Delete Item


def delete_item(item_id):
    mongo.db.ikeaunderscoreitems.delete_one({"_id": ObjectId(item_id)})
    return True

def add_user(first_name, last_name, email, password):
    if mongo.db.users.find_one({"email": email}):
        print("User already exists:", email)
        return False
    
    user = { 
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

    mongo.db.users.insert_one(user)

    return True

def login_user(email, password):
    user = mongo.db.users.find_one({"email": email})
    
    if not user:
        print("User not found:", email)
        return None
    
    if user["password"] == password:
        print("Login successful:", user["email"])
        return user
    else:
        print("Password mismatch:", email)
        return None