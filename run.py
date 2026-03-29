from flask import Flask, Request, redirect, url_for, render_template
from flask_pymongo import PyMongo
import os


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
