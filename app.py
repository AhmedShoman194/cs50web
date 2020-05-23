import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    symbols = db.execute('SELECT symbol, shares FROM owned WHERE user_id= :id', id=session['user_id'])
    symbol = []
    shares = []
    price = []
    total_price = []
    table = []
    big_total = 0
    for r in symbols:
        symbol.append(r['symbol'])
        shares.append(r['shares'])
    for j in symbol:
        price.append(lookup(j)['price'])

    for i in range(len(shares)):
        total_price.append(float(shares[i])*float(price[i]))
    big_total = sum(total_price)
    
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
    big_total = usd(big_total + int(cash[0]["cash"]))
    cash = usd(cash[0]["cash"])
    for i in range(len(symbol)):
        table.append(symbol[i])
        table.append(shares[i])
        table.append(usd(price[i]))
        table.append(usd(total_price[i]))
    return render_template("index.html", table=table, big_total=big_total, cash=cash)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:

        stock = lookup(request.form.get("symbol"))
        if stock == None:
            message = "No such Symbol!"
            return apology(message)

        name = stock["name"]
        price = stock["price"]
        symbol = stock["symbol"]

        if not name or not price or not symbol:
            message = "Somthing went wrong!"
            return apology(message)

        shares = request.form.get("shares")
        try:
            shares = int(shares)
            if shares < 1:
                message = "shares must be a positive number!"
                return apology(message)
        except ValueError:
            message = "shares must be a positive number!"
            return apology(message)

        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        x = int(cash[0]["cash"])
        y = price * shares
        if x < y :
            message = "Sorry you don't have enough money to buy this amount!"
            return apology(message)
        
        db.execute("INSERT INTO trans (user_id, symbol, trans, shares, time, price) VALUES (:user_id, :symbol, :trans, :shares, :time, :price)", user_id=session["user_id"], symbol=symbol, trans="buy", shares=shares, time=datetime.datetime.now(), price=y)
        check = db.execute("SELECt symbol FROM owned WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        if len(check) == 1:
            db.execute("UPDATE owned SET shares = shares + :newshares WHERE user_id = :user_id AND symbol = :symbol", newshares=shares, user_id=session["user_id"], symbol=symbol)
        else:
            db.execute("INSERT INTO owned (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)", user_id=session["user_id"], symbol=symbol, shares=shares)
        newcash = cash[0]["cash"] - y
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash=newcash, user_id=session["user_id"])        
        return render_template("bought.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute('SELECT symbol, shares, trans, price, time FROM trans WHERE user_id= :id', id=session['user_id'])
    symbol = []
    shares = []
    price = []
    trans = []
    table = []
    time = []
    for r in history:
        symbol.append(r['symbol'])
        shares.append(r['shares'])
        price.append(usd(r['price']))
        trans.append(r['trans'])
        time.append(r['time'])
    
    for i in range(len(symbol)):
        table.append(symbol[i])
        table.append(shares[i])
        table.append(price[i])
        table.append(trans[i])
        table.append(time[i])
    return render_template("history.html", table=table)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")
    else:

        stock = lookup(request.form.get("symbol"))
        if stock == None:
            message = "No such Symbol!"
            return apology(message)

        name = stock["name"]
        price = usd(stock["price"])
        symbol = stock["symbol"]

        if not name or not price or not symbol:
            message = "Somthing went wrong!"
            return apology(message)

        return render_template("quoted.html", name=name, price=price, symbol=symbol )



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not name or not password or not confirm or password != confirm:
            message = "Check the name and password again!"
            return apology(message)
        check = db.execute("SELECT username FROM users WHERE username = :name", name = name)
        if len(check) == 1:
            message = "Username is already in use!"
            return apology(message)
        h = generate_password_hash(password)
        db.execute("INSERT INTO users ('username', 'hash') VALUES (:name, :hash)", name = name, hash = h)
        return redirect("/")
    


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        x = db.execute("SELECt symbol FROM owned WHERE user_id = :user_id", user_id=session["user_id"])
        symbol = []
        for r in x:
            symbol.append(r['symbol'])
        return render_template("sell.html", symbol=symbol)

    else:
        stock = lookup(request.form.get("symbol"))
        if stock == None:
            message = "No such Symbol!"
            return apology(message)

        price = stock["price"]
        symbol = stock["symbol"]

        if not price:
            message = "Somthing went wrong!"
            return apology(message)

        shares = request.form.get("shares")
        try:
            shares = int(shares)
            if shares < 1:
                message = "shares must be a positive number!"
                return apology(message)
        except ValueError:
            message = "shares must be a positive number!"
            return apology(message)

        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        x = int(cash[0]["cash"])
        y = price * shares
        z = db.execute("SELECt shares FROM owned WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        if shares > z[0]["shares"]:
            message = "You don't have that many shares to sell!"
            return apology(message)
        db.execute("INSERT INTO trans (user_id, symbol, trans, shares, time, price) VALUES (:user_id, :symbol, :trans, :shares, :time, :price)", user_id=session["user_id"], symbol=symbol, trans="sell", shares=shares, time=datetime.datetime.now(), price=y)
        db.execute("UPDATE owned SET shares = shares - :newshares WHERE user_id = :user_id AND symbol = :symbol", newshares=shares, user_id=session["user_id"], symbol=symbol)
        check = db.execute("SELECt shares FROM owned WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        if check[0]["shares"] == 0:
            db.execute("DELETE FROM owned WHERE user_id = :user_id AND symbol = :symbol", user_id=session["user_id"], symbol=symbol)
        newcash = x + y
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash=newcash, user_id=session["user_id"])        
        return render_template("sold.html")
        

@app.route("/password", methods=['GET', 'POST'])
@login_required
def password():
    if request.method == "GET":
        return render_template("password.html")
    else:
        old = request.form.get("old")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not old or not password or not confirm or password != confirm:
            message = "Check for missing data or confirm password!"
            return apology(message)
        h1 = db.execute("SELECT hash FROM users WHERE id = :id", id=session['user_id'])
        if not check_password_hash(h1[0]['hash'], old):
            message = "Current Password doesn't match!"
            return apology(message)
        x = generate_password_hash(password)
        db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", hash=x, user_id=session["user_id"])
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
