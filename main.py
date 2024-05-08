from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///members.db"
db = SQLAlchemy(app)


@app.route("/")
def home():
    return render_template("login_page.html")


if __name__ == "__main__":
    app.run(debug=True)
