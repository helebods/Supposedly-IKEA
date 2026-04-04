import uuid
import os
from flask import Blueprint, current_app, render_template, request, redirect, url_for, session
from . import mongo
from .ikea_db.mongodb import add_user, get_all_items, insert_product, delete_One_Item, update_One_Item, login_user, count_total_items, count_per_category, count_per_name, search_items
from werkzeug.utils import secure_filename
from bson import ObjectId


main = Blueprint("main", __name__)


@main.route("/")
def auth_home():
    return render_template("index.html")

# View All Items


@main.route("/all_items")
def all_items():

    if "user_id" not in session:
        return redirect(url_for("main.auth_home"))

    items = get_all_items()
    return render_template("all_items.html", items=items)

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

    return render_template("all_items.html")

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


# Order Product

@main.route("/order_product")
def order_product():
    return render_template("order_product.html")

# Insert Item


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

        data["image_url"] = filename
        if data["image_url"] is None:
            data["image_url"] = "quibolords.jpg"

        insert_product(data)

        return redirect(url_for("main.all_items"))

    return render_template("insert_item.html")


@main.route("/logout")
def logout():

    session.pop("user_id", None)
    return redirect(url_for("main.auth_home"))


@main.route("/update", methods=["GET", "POST"])
def update(product_id):
    if request.method == "POST":
        data = request.form.to_dict()

        file = request.files.get("Product_Image_URL")

        # get existing product directly
        product = current_app.db.products.find_one(
            {"_id": ObjectId(product_id)})

        filename = product.get("image_url") if product else None

        if file and file.filename != "":
            safe_name = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{safe_name}"

            upload_path = os.path.join(
                current_app.root_path,
                "static/uploads",
                filename
            )
            file.save(upload_path)

        data["image_url"] = filename

        # update directly in MongoDB
        current_app.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data}
        )

        return redirect(url_for("main.all_items"))

    # fetch product for initial form load
    product = current_app.db.products.find_one({"_id": ObjectId(product_id)})

    return render_template("update_item.html", product=product)


@main.route("/count_all_items")
def count_all_items():
    total_items = count_total_items()
    return render_template("all_items.html", total_items=total_items)


@main.route("/count_per_category")
def per_category_count():
    item_category_count = count_per_category()
    return render_template("all_items.html", item_category_count=item_category_count)

# seacrh


@main.route('/search')
def search():
    user_input = request.args.get('q')
    if not user_input:
        return redirect(url_for('main.all_items'))

    results = search_items(user_input)
    return render_template('all_items.html', items=results)
