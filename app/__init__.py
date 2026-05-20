#===========================================================
# APP NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------
@app.get("/")
def show_welcome():
    return render_template("pages/welcome.jinja")
#-----------------------------------------------------------
# Signup page
#-----------------------------------------------------------
@app.get("/user/new")
def show_signup_form():
    return render_template("pages/user_form.jinja")
#-----------------------------------------------------------
# Hanlde user signup
#-----------------------------------------------------------
@app.post("/user")
def add_user():
    forename = request.form.get('forename', '').strip()
    surname  = request.form.get('surname',  '').strip()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        password_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (forename, surname, username, password_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (forename, surname, username, password_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("pages/login.jinja")


#-----------------------------------------------------------
# login page
#-----------------------------------------------------------
@app.get("/login")
def show_login_form():
    return render_template("pages/login.jinja")

#-----------------------------------------------------------
# logOUT HANDLING
#-----------------------------------------------------------
@app.get("/logout")
def logout_user():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")


#-----------------------------------------------------------
# login post
#-----------------------------------------------------------
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, forename, surname, password_hash
            FROM users
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login")

        if not check_password_hash(user["password_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login")

        session["logged_in"] = True
        session["user"] = {
            "username": username,
            "forename": user["forename"],
            "surname":  user["surname"],
        }

        flash("Login successful", "success")
        return redirect("/")
    
#-----------------------------------------------------------
# New Message
#-----------------------------------------------------------
@app.get("/message/new")
def show_message_form():
    return render_template("pages/message.jinja")

#-----------------------------------------------------------
# Show Message Form
#-----------------------------------------------------------
@app.get("/message")
def show_messages():
    return render_template("pages/message.jinja")
#-----------------------------------------------------------
# Post Message
#-----------------------------------------------------------
@app.post("/message")
def post_message():

    # Get form data
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()

    # Validate data
    if not title:
        flash("Title is required", "error")
        return redirect("/message")

    if len(title) > 40:
        flash("Title is too long (max 40 chars)", "error")
        return redirect("/message")

    # Escape text inputs
    title = html.escape(title)
    body = html.escape(body)

    user_id =session["user"]["id"]

    # Add to database
    with connect_db() as db:
        sql = """
            INSERT INTO messages (title, body, user_id)
            VALUES (?, ?, ?)
        """
        params = (title, body, user_id)
        db.execute(sql, params)

    flash(f"Message added")
    return redirect("/")

#-----------------------------------------------------------
# Creature list page - Show all the creatures
#-----------------------------------------------------------
@app.get("/creatures")
def show_all_creatures():
    with connect_db() as db:
        sql = """
            SELECT id, species, name
            FROM creatures
        """
        params = ()
        creatures = db.execute(sql, params).fetchall()

        return render_template("pages/creature_list.jinja", creatures=creatures)


#-----------------------------------------------------------
# Help page - Show some help
#-----------------------------------------------------------
@app.get("/help")
def show_help():

    flash("Flash test message")
    flash("Flash test message with a longer bit of text")
    flash("Success test message", "success")
    flash("Error test message", "error")

    return render_template("pages/help.jinja")


#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

