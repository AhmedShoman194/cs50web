import os
import datetime
import requests
from flask import Flask, session, redirect, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def apology(message):
    return render_template("apology.html", message=message)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not name or not password or not confirm or password != confirm:
            message = "Check the name and password again!"
            return apology(message)
        check = db.execute("SELECT name FROM users WHERE name = :name", {"name": name}).fetchall()
        if len(check) == 1:
            message = "User name is already in use!"
            return apology(message)
        db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": password})
        db.commit()
        return redirect("/login")


@app.route("/login", methods=['GET','POST'])
def login():
    session.clear()
    session["logged_in"] = False
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        if not name or not password:
            message = "Check User name and password again!"
            return apology(message)
        data = db.execute("SELECT id, name, password FROM users WHERE name = :name", {"name": name}).fetchall()
        if len(data) != 1 or password != data[0][2]:
            message = "Password or User name is wrong!"
            return apology(message)
        session["user_id"] = data[0][0]
        session["logged_in"] = True
        db.commit()
        return redirect("/")

@app.route("/", methods=["GET","POST"])
def index():
    #todo if not logged in render page with login and reg links
    if request.method == "GET":
        return render_template("index.html")
    else:
        name = request.form.get("name")
        if not name:
            message = "Please enter a book name!"
            return apology(message)
        books = db.execute("SELECT * FROM books WHERE isbn ILIKE :name OR title ILIKE :name or auther ILIKE :name or year LIKE :name", {"name": f"%{name}%"}).fetchall()
        db.commit()
        return render_template("index.html", books=books)
        
@app.route("/<string:book>", methods=["GET","POST"])
def book(book):
    if request.method == "GET":
        books = db.execute("SELECT * FROM books WHERE isbn = :book", {"book": book}).fetchall()
        if books is None:
            message = "This book is not found!"
            return apology(message)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "huM2a8fV2BVwepQIPFZHig", "isbns": book})
        good = res.json()
        reviews = db.execute("SELECT * FROM review WHERE book_isbn = :book", {"book": book}).fetchall()
        reviewers = []
        for i in reviews:
            r = db.execute("SELECT name FROM users WHERE id = :id", {"id": i[0]}).fetchone()
            reviewers.append(r[0])
        db.commit()
        rev = []
        for review, reviewer in zip(reversed(reviews), reversed(reviewers)):
            rev.append(reviewer)
            rev.append(review[4])
            rev.append(review[2])
            rev.append(review[3])
        for j in reviews:
            if j[0] == session["user_id"]:
                return render_template ("book1.html", books=books, rev=rev, goodcount=good["books"][0]["work_ratings_count"], goodrate=good["books"][0]["average_rating"])
        return render_template("book.html", books=books, rev=rev, goodcount=good["books"][0]["work_ratings_count"], goodrate=good["books"][0]["average_rating"])
    else:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "huM2a8fV2BVwepQIPFZHig", "isbns": book})
        good = res.json()
        review = request.form.get("review")
        rate = int(request.form.get("rate"))
        if review is None or rate is None:
            message = "No reviews or rate added!"
            return apology(message)
        db.execute("INSERT INTO review (user_id, book_isbn, review, rev_time, rate) VALUES (:a, :b, :c, :d, :e)", {"a": session['user_id'], "b": book, "c": review, "d": datetime.datetime.now(), "e": rate})
        books = db.execute("SELECT * FROM books WHERE isbn = :book", {"book": book}).fetchall()
        if books is None:
            message = "This book is not found!"
            return apology(message)
        reviews = db.execute("SELECT * FROM review WHERE book_isbn = :book", {"book": book}).fetchall()
        reviewers = []
        for i in reviews:
            r = db.execute("SELECT name FROM users WHERE id = :id", {"id": i[0]}).fetchone()
            reviewers.append(r[0])
        db.commit()
        rev = []
        for review, reviewer in zip(reversed(reviews), reversed(reviewers)):
            rev.append(reviewer)
            rev.append(review[4])
            rev.append(review[2])
            rev.append(review[3])
        for j in reviews:
            if j[0] == session["user_id"]:
                return render_template ("book1.html", books=books, rev=rev, goodcount=good["books"][0]["work_ratings_count"], goodrate=good["books"][0]["average_rating"])
        return render_template("book.html", books=books, rev=rev, goodcount=good["books"][0]["work_ratings_count"], goodrate=good["books"][0]["average_rating"])


@app.route("/api/<string:book_api>")
def book_api(book_api):
    book = db.execute("SELECT * FROM books WHERE isbn = :book", {"book": book_api}).fetchall()
    reviews_count = db.execute("SELECT COUNT(*) FROM review WHERE book_isbn = :book", {"book": book_api}).fetchall()
    rate = db.execute("SELECT AVG(rate) FROM review WHERE book_isbn = :book", {"book": book_api}).fetchall()
    print (book, reviews_count, rate)
    return jsonify({
            "title": book[0][1],
            "author": book[0][2],
            "year": book[0][3],
            "isbn": book[0][0],
            "review_count": str(reviews_count[0][0]),
            "average_score": str(rate[0][0])
        })

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")