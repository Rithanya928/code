import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Use filesystem-based sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Custom filter for currency formatting
app.jinja_env.filters["usd"] = usd

# Ensure API key is set
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY not set")


### 🚀 ROUTES

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Fetch user’s current cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Fetch all stocks owned by the user
    stocks = db.execute(
        "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol", user_id
    )

    total_value = cash

    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["shares"] * stock["price"]
        total_value += stock["total"]

    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total_value))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate inputs
        if not username or not password or not confirmation:
            return apology("Please fill all fields", 400)

        if password != confirmation:
            return apology("Passwords do not match", 400)

        # Hash the password
        hash_password = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
            return redirect("/login")
        except:
            return apology("Username already exists", 400)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username and password were submitted
        if not username or not password:
            return apology("Please provide username and password", 403)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return apology("Invalid username or password", 403)

        # Store the user ID in the session
        session["user_id"] = user[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)

        if not quote:
            return apology("Invalid symbol", 400)

        return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol or not shares.isdigit() or int(shares) <= 0:
            return apology("Invalid symbol or shares", 400)

        shares = int(shares)
        quote = lookup(symbol)

        if not quote:
            return apology("Invalid stock symbol", 400)

        price = quote["price"]
        total_cost = price * shares
        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        if total_cost > cash:
            return apology("Not enough cash", 400)

        # Perform the transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, timestamp) VALUES (?, ?, ?, ?, ?)",
                   user_id, symbol, shares, price, datetime.datetime.now())

        # Update cash balance
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if shares <= 0:
            return apology("Invalid shares", 400)

        # Get the current shares
        rows = db.execute(
            "SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id, symbol
        )

        if len(rows) != 1 or rows[0]["shares"] < shares:
            return apology("Not enough shares", 400)

        # Get current price
        quote = lookup(symbol)
        price = quote["price"]

        # Perform the transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, timestamp) VALUES (?, ?, ?, ?, ?)",
                   user_id, symbol, -shares, price, datetime.datetime.now())

        # Update cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", price * shares, user_id)

        return redirect("/")
    else:
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
        return render_template("sell.html", symbols=symbols)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        user_id
    )

    return render_template("history.html", transactions=transactions)
