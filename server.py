from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User
from functions import password_hash, check_password
# import requests
# import stripe
# import datetime
# import os

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "MYSECRETKEY"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register-form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    password = request.form.get("password")
    payer_seller = request.form.get("payer_or_receiver")

    password = password_hash(password)

    # check to see if user already exists. If so, update their details.
    if User.fetch_by_email(email) is None:
        current_user = User.add(fullname, email, password, payer_seller)

    else:
        current_user = User.fetch_by_email(email)
        current_user.fullname = fullname
        current_user.password = password
        current_user.payer_seller = payer_seller

    db.session.commit()

    flash("User %s added." % fullname)

    session["user_id"] = current_user.user_id
    session["payer_seller"] = current_user.payer_seller
    return redirect("/dashboard")


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.fetch_by_email(email)

    if not user:
        flash("No such user")
        return redirect("/login")

    pw_hash = user.password

    if check_password(pw_hash, password) is False:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id
    session["payer_seller"] = user.payer_seller

    flash("Logged in")
    return redirect("/dashboard")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    del session["payer_seller"]
    flash("Logged Out.")
    return redirect("/")

@app.route('/account-page')
def load_account():
    """Homepage."""

    return render_template("account_page.html")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    # connect_to_db(app, "postgresql:///samsmith")

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")