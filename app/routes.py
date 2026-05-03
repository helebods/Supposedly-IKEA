from datetime import datetime
import uuid
import os
from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, session
from . import mongo
from .ikea_db.mongodb import add_user, build_stock, get_all_items, insert_product, delete_One_Item, update_One_Item, build_product, build_location, build_pricing
from .ikea_db.mongodb import login_user, count_total_items, get_manage_items, search_items, get_low_stock, average_selling_price, max_quantity, min_quantity
from werkzeug.utils import secure_filename
from bson import ObjectId


main = Blueprint("main", __name__)

# helper function for stats


def gets_stats():
    try:
        return {
            "total_items": count_total_items(),
            "avg_price": average_selling_price(),
            "min_qty": min_quantity(),
            "max_qty": max_quantity(),
        }
    except Exception as e:
        print("gets_stats() error:", e)
        return {
            "total_items": 0,
            "avg_price": 0,
            "min_qty": 0,
            "max_qty": 0,
        }


@main.route("/")
def auth_home():
    return render_template("index.html")

# View Al


@main.route("/all_items")
def all_items():
    if "user_id" not in session:
        return redirect(url_for("main.auth_home"))

    items = get_all_items()
    return render_template("all_items.html", items=items, stats=get_stats)

# Sign In


@main.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["signin-email"]
        password = request.form["signin-password"]

        user = login_user(email, password)

        if user:
            session["user_id"] = str(user["_id"])

            if user.get("email") == "secret@ikea.com":
                print("Admin user logged in:", email)
                session["is_admin"] = True
            else:
                session["is_admin"] = False

            if session.get("is_admin"):
                return redirect(url_for("main.insert"))

            return redirect(url_for("main.all_items"))
        else:
            return render_template("index.html")

# Sign Up


@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form["signup-firstname"]
        lastname = request.form["signup-lastname"]
        email = request.form["signup-email"]
        password = request.form["signup-password"]

        add_user(firstname, lastname, email, password)

    return render_template("index.html")


# Order Product i gues we can remove this or edit it for the viewing of orders


@main.route("/order_product", methods=["GET", "POST"])
def order_product():
    if "user_id" not in session:
        return redirect(url_for("main.auth_home"))

    if request.method == "POST":
        data = request.form

        items = [{
            "item_id": data.get("item_id"),
            "product_name": data.get("product_name"),
            "quantity": int(data.get("quantity")),
            "unit_cost": float(data.get("unit_cost"))
        }]

        total_cost = sum(i["quantity"] * i["unit_cost"] for i in items)
        user_id = session["user_id"]

        insert_order(user_id, items, total_cost)
        return redirect(url_for("main.order_product"))

    items = get_low_stock()
    return render_template("order_product.html", items=items)


@main.route("/insert", methods=["GET", "POST"])
def insert():
    if request.method == "POST":
        data = request.form.to_dict()

        file = request.files.get("Product_Image_URL")
        filename = None

        if file and file.filename != "":
            safe_name = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{safe_name}"
            upload_path = os.path.join(
                current_app.root_path, "static/uploads", filename)
            file.save(upload_path)

        data["image_url"] = filename if filename else "quibolords.jpg"

        # Insert to items collection (existing)
        insert_product(data)

        # Also insert to orders collection
        items = [{
            "item_id": str(mongo.db["items"].find_one(
                {"product.Product_Name": data.get("Product_Name")},
                sort=[("_id", -1)]  # get the one we just inserted
            )["_id"]),
            "product_name": data.get("Product_Name"),
            "quantity": int(data.get("quantity")),
            "unit_cost": float(data.get("cost"))
        }]

        total_cost = float(data.get("quantity")) * float(data.get("cost"))
        user_id = session.get("user_id", "admin")

        insert_order(user_id, items, total_cost)

        return redirect(url_for("main.insert"))

    return render_template("insert_item.html")


@main.route("/logout")
def logout():

    session.pop("user_id", None)
    return redirect(url_for("main.auth_home"))


@main.route("/update/<product_id>", methods=["POST"])
def update(product_id):
    data = request.form.to_dict()
    file = request.files.get("Product_Image_URL")

    item = mongo.db.items.find_one({"_id": ObjectId(product_id)})

    # keep old image if no new upload
    filename = item["product"].get("Product_image_url") if item else None

    if file and file.filename != "":
        safe_name = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{safe_name}"

        upload_path = os.path.join(
            current_app.root_path,
            "static/uploads",
            filename
        )
        file.save(upload_path)

    # USE YOUR BUILDERS HERE
    updated_data = {
        "product": build_product(
            data.get("Product_Name"),
            data.get("Product_Brand"),
            data.get("Product_Category"),
            data.get("Product_Description"),
            filename
        ),
        "location": build_location(
            data.get("warehouse"),
            data.get("aisle"),
            data.get("rack"),
            data.get("bin")
        ),
        "stock": build_stock(
            data.get("quantity"),
            data.get("unit"),
            data.get("reorder_level")
        ),
        "price": build_pricing(
            data.get("cost"),
            data.get("selling_price")
        ),
        "updated_at": datetime.now()
    }

    mongo.db.items.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": updated_data}
    )

    return redirect(url_for("main.manage_items"))


@main.route("/get_item/<id>")
def get_item(id):
    item = mongo.db.items.find_one({"_id": ObjectId(id)})

    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({
        "id": str(item["_id"]),

        "name": item["product"]["Product_Name"],
        "brand": item["product"]["Product_Brand"],
        "category": item["product"]["Product_Category"],
        "description": item["product"].get("Product_Description", ""),

        "quantity": item["stock"].get("quantity", ""),
        "unit": item["stock"].get("unit", ""),
        "reorder_level": item["stock"].get("reorder_level", ""),

        "warehouse": item["location"].get("warehouse", ""),
        "aisle": item["location"].get("aisle", ""),
        "rack": item["location"].get("rack", ""),
        "bin": item["location"].get("bin", ""),

        "cost": item["price"].get("cost", ""),
        "selling_price": item["price"].get("selling_price", "")
    })


@main.route("/delete/<product_id>")
def delete(product_id):
    delete_One_Item(product_id)
    return redirect(url_for("main.manage_items"))


@main.route('/manage_items')
def manage_items():
    print("user" + session.get("user_id", "None"))
    items = get_manage_items()
    return render_template("manage_items.html", items=items)


@main.route("/search")
def search():
    user_input = request.args.get('q')
    if not user_input:
        return redirect(url_for('main.all_items'))

    results = search_items(user_input)
    return render_template('all_items.html', items=results, stats=gets_stats())


@main.route("/item/<item_id>")
def item_detail(item_id):
    if "user_id" not in session:
        return redirect(url_for("main.auth_home"))
    item = get_item_by_id(item_id)
    if not item:
        return "Item not found"
    return render_template("item_des.html", item=item)
