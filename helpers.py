import requests
import urllib.parse
from flask import redirect, render_template, session
from functools import wraps

def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    """Look up quote for symbol"""
    api_key = "YOUR_IEX_API_KEY"
    try:
        response = requests.get(f"https://api.iex.cloud/v1/data/core/quote/{symbol}?token={api_key}")
        quote = response.json()[0]
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except:
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

