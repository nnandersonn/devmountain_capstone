from sqlite3 import connect
from flask import Flask, render_template, redirect, request, flash, session
from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators, IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from model import User, Pet, Activity, GPS_Point, Friend, connect_to_db, db

app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)

app.secret_key = "testarooni"



@app.route('/')
def index():
    """Homepage"""
    return render_template('homepage.html')


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(port=5000, host='0.0.0.0')

    