from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///members.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String,nullable = False)
    user_id = db.Column(db.String,nullable = False)
    password = db.Column(db.String,nullable = False)

@app.route("/")
def home():
    return render_template("login_page.html")


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up_page.html')


if __name__ == "__main__":

    app.run(debug=True)
