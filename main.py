from flask import Flask, url_for, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, select, delete, insert
import random
import configparser
import os
import sys
import urllib.request
import json

properties = configparser.ConfigParser()
properties.read('static\config.ini')
resource = properties['ETC']
Naver_id = resource["Client_id"]
Naver_password = resource["Client_password"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///members.db"
db = SQLAlchemy(app)
app.secret_key = "kmg010320"
meta = MetaData()


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
        return render_template("login_page.html")
    else:
        with app.app_context():

            food_table = Table(
                new_name,
                meta,
                Column("id", Integer, primary_key=True),
                Column("type", String, nullable=False),
                Column("food_name", String, nullable=False),
            )
            meta.create_all(bind=db.engine)
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
                db.session.execute(
                    food_table.insert().values(
                        type=data["type"], food_name=data["food_name"]
                    )
                )

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


# 개인정보 수정 내용 반영
@app.route("/change/<username>", methods=["POST"])
def change(username):
    newid = request.form.get("newid")
    newpass = request.form.get("newpass")
    with app.app_context():
        db.session.query(User).filter_by(name=username).update(
            {"user_id": newid, "password": newpass}
        )
        db.session.commit()
    flash("개인정보가 변경되었습니다.")
    return redirect(url_for("my_info", username=username))


# 음식추가 페이지
@app.route("/add/<username>")
def add(username):
    table_name = username
    food_table = Table(table_name, meta, autoload_with=db.engine)
    query = select(food_table)
    result = db.session.execute(query)
    result_list = [row for row in result]
    # 음식 종류 별로 정렬 하기
    sorted_result = sorted(result_list, key=lambda x: x[1])
    return render_template("add.html", foods=sorted_result, name=username)


# 음식 삭제
@app.route("/delete/<username>/<id>")
def delete_food(username, id):
    with app.app_context():
        table_name = username
        food_table = Table(table_name, meta, autoload_with=db.engine)
        condition = food_table.c.id == id
        delete_query = delete(food_table).where(condition)
        db.session.execute(delete_query)
        db.session.commit()
        return redirect(url_for("add", username=username))


# 음식 추가
@app.route("/add_food/<username>", methods=["POST"])
def add_food(username):
    new_food_type = request.form.get("foodType")
    new_food_name = request.form.get("food_name")
    with app.app_context():
        table_name = username
        food_table = Table(table_name, meta, autoload_with=db.engine)
        new_food_data = {"type": new_food_type, "food_name": new_food_name}
        insert_stmt = insert(food_table).values(new_food_data)

        # 실행
        db.session.execute(insert_stmt)
        db.session.commit()

        return redirect(url_for("add", username=username))


@app.route("/store/<username>", methods=["POST"])
def store(username):
    foodtype = request.form.get("foodType")
    table_name = username
    food_table = Table(table_name, meta, autoload_with=db.engine)
    if foodtype == "전체":
        query = select(food_table.c.food_name)
    else:
        query = select(food_table.c.food_name).where(food_table.c.type == foodtype)
    result = db.session.execute(query)
    food_names = [row[0] for row in result]
    try:
        random_food = random.choice(food_names)
    except IndexError:
        random_food = "데이터 없음"
    return render_template("food.html", food=random_food, name=username)

@app.route('/store_recommand/<food>/<username>',methods=["POST"])
def store_recommand(food,username):
    #지역 이름
    place = request.form.get('place')
    #네이버 api 구현
    encText = urllib.parse.quote(place+" "+food+" 맛집")
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText # JSON 결과
    request_ = urllib.request.Request(url)
    request_.add_header("X-Naver-Client-Id",Naver_id)
    request_.add_header("X-Naver-Client-Secret",Naver_password)
    response = urllib.request.urlopen(request_)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read().decode('utf-8')
        data = json.loads(response_body)
        return render_template('store.html',name=username)
    else:
        print("Error Code:" + rescode)
        return render_template('recommand.html')


if __name__ == "__main__":
    app.run(debug=True)
