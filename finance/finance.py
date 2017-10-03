"""Main routing and controllers"""
import sqlite3
import datetime
from tempfile import mkdtemp
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from helpers import *

# configure application
APP = Flask(__name__)

# ensure responses aren't cached
if APP.config["DEBUG"]:
    @APP.after_request
    def after_request(response):
        """Setup request headers."""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
APP.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
APP.config["SESSION_FILE_DIR"] = mkdtemp()
APP.config["SESSION_PERMANENT"] = False
APP.config["SESSION_TYPE"] = "filesystem"
Session(APP)

# configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")

CONN = sqlite3.connect('finance.db')
CONN.row_factory = sqlite3.Row
DB = CONN.cursor()


@APP.route("/")
@login_required
def index():
    """Application frontpage"""
    session_id = session["user_id"]

    DB.execute(
        "SELECT *, SUM(qty) FROM users JOIN history ON "
        "users.id = history.id WHERE users.id = :id GROUP BY stock",
        (session_id,)
    )
    stocks = DB.fetchall()

    DB.execute(
        "SELECT symbol FROM users JOIN history ON users.id = history.id "
        "WHERE users.id = :id AND history.type = :buy GROUP BY stock",
        (session_id, 'BUY')
    )
    symbols = DB.fetchall()

    DB.execute(
        "SELECT cash FROM users WHERE id = :id",
        (session_id,)
    )
    cash = DB.fetchone()

    current_price = []

    for symbol in symbols:
        quote_symbol = lookup(str(symbol['symbol']))
        current_price.append(quote_symbol['price'])

    return render_template("index.html", stocks=stocks, current_price=current_price, cash=cash)


@APP.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""

    if request.method == "POST":
        stock = lookup(request.form.get("stock symbol"))
        stock_name = stock["name"]
        stock_qty = int(request.form.get("qty"))
        stocks_price = float(stock["price"]) * stock_qty
        session_id = session["user_id"]
        DB.execute(
            "SELECT cash FROM users WHERE id = :id",
            (session_id,)
        )
        cash = (DB.fetchone())[0]

        if cash < stocks_price:
            return apology("You don't have enough money")
        else:
            new_cash = cash - stocks_price
            DB.execute("UPDATE users SET cash = :cash WHERE id = :id",
                       (new_cash, session_id))
            DB.execute(
                "INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id,
                 stock_name,
                 str(datetime.datetime.now()),
                 stock_qty,
                 request.form.get("stock symbol"), float(stock['price']), 'BUY')
            )
            CONN.commit()
            return redirect(url_for("index"))
    else:
        return render_template("display.html")


@APP.route("/history")
@login_required
def history():
    """Show history of transactions."""

    session_id = session["user_id"]
    DB.execute(
        "SELECT * FROM history WHERE history.id = :id",
        (session_id,)
    )
    db_history = DB.fetchall()

    return render_template("history.html", history=db_history)


@APP.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        username = request.form.get("username")
        rows = DB.execute(
            "SELECT * FROM users WHERE username = :username", (username,))

        # ensure username exists and password is correct
        results = rows.fetchone()
        if results is None or not pwd_context.verify(request.form.get("password"), results[2]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = results[0]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@APP.route("/logout")
def logout():
    """Log user out."""

    # redirect user to login form
    return redirect(url_for("login"))


@APP.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        stock_name = request.form.get("stock symbol")
        stock = lookup(stock_name)
        if stock != None:
            return render_template(
                "quoted.html",
                name=stock["name"],
                price=stock["price"],
                symbol=stock["symbol"]
            )
        else:
            return apology(stock_name + " stock not found")

    else:
        return render_template("quote.html")


@APP.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must enter username")

        elif not request.form.get("password") or not request.form.get("Repeat Password"):
            return apology("must enter password")

        elif request.form.get("password") != request.form.get("Repeat Password"):
            return apology("passwords must match")

        # Hash the given password
        password_hash = pwd_context.encrypt(request.form.get("password"))

        # Register the user in the database
        username = request.form.get("username")
        result = DB.execute(
            "INSERT INTO users (username, hash) VALUES (:username, :password_hash)", (username, password_hash))
        CONN.commit()

        if not result:
            return apology("username already taken")

        # Log in automatically
        # session["user_id"]

        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@APP.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":
        stock = lookup(request.form.get("stock symbol"))
        stock_name = stock["name"]
        stock_qty = -1 * int(request.form.get("qty"))
        session_id = session["user_id"]

        # Updates user cash
        DB.execute(
            "SELECT cash FROM users WHERE id = :id",
            (session_id,)
        )
        current_cash = DB.fetchone()
        new_cash = current_cash['cash'] + \
            abs(stock_qty * float(stock["price"]))
        DB.execute(
            "UPDATE users SET cash = :cash WHERE id = :id",
            (new_cash, session_id)
        )

        DB.execute(
            "SELECT *, SUM(qty) FROM users JOIN history ON users.id = history.id WHERE users.id = :id AND history.type = :buy AND history.stock = :stock GROUP BY stock",
            (session_id, 'BUY', stock_name)
        )
        stocks = DB.fetchone()  # or fetchall(), let's test

        current_stocks = int(stocks[11])

        if abs(stock_qty) > current_stocks:
            return apology("You don't own that many stocks!")

        DB.execute(
            "INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id,
             stock_name,
             str(datetime.datetime.now()),
             stock_qty,
             request.form.get("stock symbol"), float(stock['price']), 'SELL')
        )
        CONN.commit()

        return redirect(url_for("index"))

    else:
        return render_template("sell.html")
