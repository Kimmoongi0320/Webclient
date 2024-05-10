from flask import Flask, url_for, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///members.db"
db = SQLAlchemy(app)
app.secret_key = "kmg010320"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("login_page.html")


@app.route("/sign_up")
def sign_up():
    return render_template("sign_up_page.html")


# 회원가입 기능
@app.route("/add_user", methods=["POST"])
def add_user():
    new_name = request.form.get("user_name")
    new_id = request.form.get("user_id")
    new_password = request.form.get("user_password")
    existing_user = User.query.filter_by(name=new_name).first()
    if existing_user:
        flash("회원 정보가 이미 있습니다")
        return render_template("sign_up_page.html")
    else:
        with app.app_context():

            class Food(db.Model):
                __tablename__ = new_name
                id = db.Column(db.Integer, primary_key=True)
                type = db.Column(db.String, nullable=False)
                food_name = db.Column(db.String, nullable=False)

            db.create_all()
            # 기본 음식 데이터 계정 생성할떄 추가
            new_users_data = [
                {"type": "중식", "food_name": "짜장면"},
                {"type": "중식", "food_name": "짬뽕"},
                {"type": "중식", "food_name": "탕수육"},
                {"type": "일식", "food_name": "초밥"},
                {"type": "일식", "food_name": "텐동"},
                {"type": "한식", "food_name": "김치찌개"},
                {"type": "한식", "food_name": "된장찌개"},
                {"type": "한식", "food_name": "제육볶음"},
                {"type": "중식", "food_name": "탕수육"},
                {"type": "일식", "food_name": "돈카츠"},
                {"type": "양식", "food_name": "파스타"},
                {"type": "양식", "food_name": "리조또"},
                {"type": "양식", "food_name": "필라프"},
                {"type": "한식", "food_name": "김치찜"},
            ]
            for data in new_users_data:
                new_user = Food(type=data["type"], food_name=data["food_name"])
                db.session.add(new_user)
            db.session.commit()

            user_to_add = User(name=new_name, user_id=new_id, password=new_password)
            db.session.add(user_to_add)
            db.session.commit()
        return redirect(url_for("home"))


# 로그인 프로세스
@app.route("/login", methods=["POST"])
def login():
    userid = request.form.get("id")
    userpass = request.form.get("password")

    user = User.query.filter_by(user_id=userid).first()

    if user:
        if user.password == userpass:
            return render_template("recommand.html", name=user.name)
        else:
            flash("비밀번호가 틀렸습니다.")
            return redirect(url_for("home"))
    else:
        flash("회원정보가 존재하지 않습니다.")
        return redirect(url_for("home"))


# 메뉴 버튼 누를때 다시 리다이렉트
@app.route("/login/<username>")
def menu(username):
    return render_template("recommand.html", name=username)


# 개인정보 수정 페이지 로드
@app.route("/myinfo/<username>")
def my_info(username):
    return render_template("my_info.html", name=username)

#개인정보 수정 내용 반영
@app.route('/change/<username>',methods=['POST'])
def change(username):
    newid = request.form.get('newid')
    newpass = request.form.get('newpass')
    with app.app_context():
        db.session.query(User).filter_by(name =username).update({"user_id":newid,"password":newpass})
        db.session.commit()
    flash("개인정보가 변경되었습니다.") 
    return redirect(url_for('my_info',username = username))



if __name__ == "__main__":

    app.run(debug=True)
