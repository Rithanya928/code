import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Use the correct database path
db = SQL("sqlite:////workspaces/190068345/birthdays/birthdays.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")

        # Validate form inputs
        if name and month and day:
            try:
                month = int(month)
                day = int(day)

                # Validate month and day ranges
                if 1 <= month <= 12 and 1 <= day <= 31:
                    # Insert into the database
                    db.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)", name, month, day)
            except ValueError:
                print("Invalid input.")

        return redirect("/")

    else:
        # Display all birthdays in the table
        birthdays = db.execute("SELECT * FROM birthdays ORDER BY month, day")
        return render_template("index.html", birthdays=birthdays)
