from flask import Blueprint, render_template, request, redirect, url_for, session
from .ikea_db.mongodb import get_all_items, insert_item, delete_item

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")

# Homepage


@main.route("/homepage")
def homepage():
    return render_template("homepage.html")


# View All Items
@main.route("/all_items")
def all_items():
    items = get_all_items()
    return render_template("all_items.html")

# Sign In


@main.route("/signin")
def signin():
    return render_template("signin.html")

# Sign Up


@main.route("/signup")
def signup():
    return render_template("signup.html")


# Order Product

@main.route("/order_product")
def order_product():
    return render_template("order_product.html")
