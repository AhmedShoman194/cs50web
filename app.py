import datetime
import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from helpers import login_required
import datetime

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANeNT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['UPLOAD_FOLDER'] = "/static"
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

def apology(message):
    return render_template("apology.html", message=message)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not name or not email or not phone or not password or not confirm or password != confirm:
            message = "Check the name and password again!"
            return apology(message)
        con = sqlite3.connect("market.db")
        db = con.cursor()
        check = db.execute("SELECT email FROM users WHERE email = (?);", (email,))
        ch = check.fetchall()
        if len(ch) == 1:
            message = "E-mail is already in use!"
            return apology(message)
        h = generate_password_hash(password)
        db.execute("INSERT INTO users ('name', 'email','phone', 'hash') VALUES (?, ?, ?, ?);", (name, email, phone, h))
        con.commit()
        con.close()
        return render_template("login.html")


@app.route("/login", methods=['GET','POST'])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            message = "Check E-mail and password again!"
            return apology(message)
        con = sqlite3.connect("market.db")
        db = con.cursor()
        data = db.execute("SELECT id, email, hash FROM users WHERE email = (?);", (email,))
        check = data.fetchall()
        if len(check) != 1 or not check_password_hash(check[0][2], password):
            message = "Password or E-Mail is wrong!"
            return apology(message)
        session["user_id"] = check[0][0]
        con.commit()
        con.close()
        if check[0][0] == 1:
            return redirect("/admin")
        return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/admin", methods=['GET','POST'])
@login_required
def admin():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        item_category = request.form.get("item_category")
        item_price = request.form.get("item_price")
        description = request.form.get("description")
        image = request.files["file"]
        if not item_name or not item_category or not item_price or not description or not image:
            message = "Check data again!"
            return apology(message)
        image.save(secure_filename(image.filename))
        con = sqlite3.connect("market.db")
        db = con.cursor()
        db.execute("insert into items ('item_name', 'item_category', 'item_price', 'description', 'image') values (?, ?, ?, ?, ?);", (item_name, item_category, item_price, description, image.filename))
        cursor = db.execute("select distinct item_category from items;")
        category = cursor.fetchall()
        curser2 = db.execute("select * from orders;")
        orders = curser2.fetchall()
        con.commit()
        con.close()
        return render_template("admin.html", item_category=category, orders=orders)
    else:
        con = sqlite3.connect("market.db")
        db = con.cursor()
        cursor = db.execute("select distinct item_category from items;")
        category = cursor.fetchall()
        curser2 = db.execute("select * from orders;")
        orders = curser2.fetchall()
        con.commit()
        con.close()
        return render_template("admin.html", item_category=category, orders=orders)


@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    if request.method == "GET":
        con = sqlite3.connect("market.db")
        db = con.cursor()
        cursor = db.execute("select * from items;")
        items = cursor.fetchall()
        item_name = []
        item_category = []
        item_price = []
        description = []
        image = []
        ca = []
        code = []
        for i in items:
            code.append(i[0])
            item_name.append(i[1])
            ca.append(i[2])
            item_price.append(i[3])
            description.append(i[4])
            image.append(i[5])
        cat = db.execute("select distinct item_category from items;")
        cats = cat.fetchall()
        for j in cats:
            item_category.append(j[0])
        con.commit()
        con.close()
        return render_template("home.html", code=code, item_name=item_name, item_category=item_category, item_price=item_price, description=description, image=image, ca=ca)
    else:
        item_code = request.form.get("code")
        number = int(request.form.get("number"))
        name = request.form.get("name")
        price = float(request.form.get("price"))
        total_price = number * price
        con = sqlite3.connect("market.db")
        db = con.cursor()
        cursor = db.execute("select name, email, phone from users where id = (?);", (session['user_id'],))
        user = cursor.fetchall()
        db.execute("insert into orders ('item_code', 'item_name', 'number', 'total_price', 'user_name', 'user_email', 'user_phone', 'time') values (?,?,?,?,?,?,?,?)", (item_code, name, number, total_price, user[0][0], user[0][1], user[0][2], datetime.datetime.now()))
        con.commit()
        con.close()
        return redirect("/home")

@app.route("/explore", methods=['GET','POST'])
def explore():
    if request.method == "GET":
        con = sqlite3.connect("market.db")
        db = con.cursor()
        cursor = db.execute("select * from items;")
        items = cursor.fetchall()
        item_name = []
        item_category = []
        item_price = []
        description = []
        image = []
        ca = []
        code = []
        for i in items:
            code.append(i[0])
            item_name.append(i[1])
            ca.append(i[2])
            item_price.append(i[3])
            description.append(i[4])
            image.append(i[5])
        cat = db.execute("select distinct item_category from items;")
        cats = cat.fetchall()
        for j in cats:
            item_category.append(j[0])
        con.commit()
        con.close()
        return render_template("explore.html", code=code, item_name=item_name, item_category=item_category, item_price=item_price, description=description, image=image, ca=ca)
    else:
        return redirect("/login")
