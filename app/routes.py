from flask import Blueprint, render_template, request, redirect, url_for, session
from . import mongo
from .ikea_db.mongodb import add_user, get_all_items, insert_item, delete_item, login_user

main = Blueprint("main", __name__)


@main.route("/")
def auth_home():
    return render_template("index.html")

# View All Items
@main.route("/all_items")
def all_items():
    items = get_all_items()
    return render_template("all_items.html", items=items)

# Sign In
@main.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        email = request.form["signin-email"]
        password = request.form["signin-password"]

        user = login_user(email, password)

        if user:
            session["user_id"] = str(user["_id"])
            return redirect(url_for("main.all_items"))

    return render_template("all_items.html")

# Sign Up
@main.route("/signup", methods=["GET","POST"])
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
@main.route("/insert_item", methods=["POST"])
def insert():
    Product_Name = request.form["Product_Name"]
    Product_Brand = request.form["Product_Brand"]
    Product_Category = request.form["Product_Category"]
    Product_Description = request.form["Product_Description"]
    Product_image_url = request.form["Product_image_url"]

    insert_item(Product_Name, Product_Brand, Product_Category, Product_Description, Product_image_url)

    return redirect(url_for("main.all_items"))

@main.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("main.auth_home"))