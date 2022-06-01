from sqlite3 import connect
from flask import Flask, render_template, redirect, request, flash, session
from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators, IntegerField
from wtforms.validators import InputRequired, Email
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from model import User, Pet, Activity, GPS_Point, Friend, connect_to_db, db

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

app.secret_key = "testarooni"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route('/')
def index():
    """Homepage"""
    return render_template('homepage.html')

@app.route('/register', methods=["GET"])
def register():
    """Display form to register for account"""
    form = RegistrationForm()

    return render_template('register.html', form=form)

@app.route('/register', methods=["POST"])
def check_registration():
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    match = User.query.filter_by(email=email).first()
    if match is None:
        user = User(email = email, password = password, first_name = first_name, last_name = last_name)
        db.session.add(user)
        db.session.commit()
        flash('Account created!')
        return render_template('homepage.html')
    else:
        flash('Account already created with this email')
        return render_template('register.html', form=RegistrationForm())

@app.route('/login', methods=["GET"])
def login():
    form = LoginForm()

    return render_template('login.html', form=form)

@app.route('/login', methods=["POST"])
def check_login():
    email = request.form['email']
    password = request.form['password']
    match = User.query.filter_by(email=email).first()
    if match: 
        if match.password == password: 
            login_user(match)
            flash("You are successfully logged in!")
            return render_template('homepage.html')
        else:
            flash("Email/Password not valid. Register for an account if you have not created one already")
            return render_template('homepage.html')
    else:
            flash("Email/Password not valid. Register for an account if you have not created one already")
            return render_template('homepage.html')

@app.route('/profile')
def profile():

    return render_template('profile.html')

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out")
    return render_template('homepage.html')

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [InputRequired('Please enter your email address.'), Email('This field requires a valid email address')])
    first_name = StringField('First Name', [InputRequired('Please enter your first name')])
    last_name = StringField('Last Name', [InputRequired('Please enter your last name')])
    password = PasswordField('Create your password', [InputRequired('Please enter a password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField('Email Address', [InputRequired('Please enter your email address.'), Email('This field requires a valid email address')])
    password = PasswordField('Enter your password', [InputRequired('Please enter your password')])
    submit = SubmitField("Login")

if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(port=5000, host='0.0.0.0')

