from random import choices
from sqlite3 import connect
from turtle import distance
from flask import Flask, render_template, redirect, request, flash, session
from wtforms import Form, BooleanField, StringField, DateField, PasswordField, SubmitField, SelectField, SelectMultipleField, validators, IntegerField
from wtforms.validators import InputRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import delete
import json
import os

from model import Pet_Activity, User, Pet, Activity, GPS_Point, Friend, connect_to_db, db
from gpx import parse_file
from map import create_map

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

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
    city = request.form['city']
    state = request.form['state']
    match = User.query.filter_by(email=email).first()
    if match is None:
        user = User(email = email, password = password, first_name = first_name, last_name = last_name, city = city, state = state)
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

@app.route('/add_pet', methods=["GET"])
def add_pet():
    form = PetRegistrationForm()
    return render_template('add_pet.html', form=form)

@app.route('/add_pet', methods=["POST"])
def create_pet():
    pet_name = request.form['name']
    breed = request.form['breed']
    birthday = request.form['birthday']
    pet = Pet(pet_name = pet_name, user_id = current_user.user_id, breed = breed, birthday = birthday)
    db.session.add(pet)
    db.session.commit()
    flash(f"Your pet {pet_name} has been added to your account!")
    return render_template('homepage.html')


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out")
    return render_template('homepage.html')

@app.route('/pets')
def display_pets():
    return render_template('pets.html')

@app.route('/edit_pet/<pet_id>', methods=["GET"])
def edit_pet(pet_id):
    pet = Pet.query.filter_by(pet_id = pet_id).first()
    form = PetEditForm()
    form.name.data = pet.pet_name
    form.breed.data = pet.breed
    form.birthday.data = pet.birthday

    return render_template('edit_pet.html', pet=pet, form=form)

@app.route('/edit_pet/<pet_id>', methods=["POST"])
def update_pet(pet_id):
    pet = Pet.query.filter_by(pet_id = pet_id).first()
    pet_name = request.form['name']
    breed = request.form['breed']
    birthday = request.form['birthday']
    pet.pet_name = pet_name
    pet.breed = breed
    pet.birthday = birthday
    db.session.commit()
    flash(f"{pet_name}'s info has been successfully updated!")
    return render_template('homepage.html')
    
@app.route('/activities', methods=["GET"])
def activities():
    
    return render_template('activities.html')

@app.route('/activity', methods=["GET", "POST"])
def activity():
    form = ActivityForm()
    if current_user.pets is not None:
        form.pet_select.choices = [(pet.pet_id, pet.pet_name) for pet in current_user.pets]

    if form.validate_on_submit():
        activity_name = form.activity_name.data
        activity_type = form.activity_type.data
        date = form.date.data
        activity = Activity(activity_name=activity_name, date = date, activity_type=activity_type)
        db.session.add(activity)
        db.session.commit()
        activity_id = activity.activity_id

        pets = form.pet_select.data
        for pet in pets:
            pet_activity = Pet_Activity(pet_id = pet, activity_id = activity_id)
            db.session.add(pet_activity)
            db.session.commit()

        file = request.files.get('gpx_file')
        
        latitude, longitude, elevation, time, seg_distance, seg_speed = parse_file(file)
        for i in range(len(latitude)):
            gps_point = GPS_Point(activity_id=activity_id, time=time[i], longitude=longitude[i], latitude=latitude[i], elevation=elevation[i], distance=seg_distance[i], speed=seg_speed[i])
            db.session.add(gps_point)
            db.session.commit()
        

        return render_template('activities.html')

    return render_template('activity.html', form=form)


@app.route('/activity/delete/<activity_id>', methods=["GET", "POST"])
def remove_activity(activity_id):
    activity = Activity.query.filter_by(activity_id = activity_id).first()
    pet_activities = Pet_Activity.query.filter_by(activity_id=activity_id)
    for p_a in pet_activities:
        db.session.delete(p_a)
    gps_points = GPS_Point.query.filter_by(activity_id=activity_id)
    for gps_point in gps_points:
        db.session.delete(gps_point)
    db.session.delete(activity)
    db.session.commit()
    flash(f'Activity {activity_id} successfully removed')
    return redirect('/')


@app.route('/activity/<activity_id>', methods=["GET"])
def display_activity(activity_id):
    
    points = GPS_Point.query.filter_by(activity_id=activity_id).order_by('time')
    activity = Activity.query.filter_by(activity_id=activity_id).first()
    longitude = []
    latitude = []
    elevation = []
    speed = []
    distance = []
    path = []
    for point in points:
        longitude.append(point.longitude)
        latitude.append(point.latitude)
        elevation.append(point.elevation)
        speed.append(point.speed)
        distance.append(point.distance)
        dict = {"lat": point.latitude, "lng": point.longitude}
        path.append(dict)
    m_h = create_map(longitude, latitude, speed)
    max_speed = round(max(speed)*2.236936, 2)
    avg_speed = round((sum(speed)/len(speed))*2.236936, 2)
    total_distance = round(sum(distance)/1609.344, 2)


    return render_template('display_activity.html', activity = activity, m_h = m_h, max_speed=max_speed, avg_speed=avg_speed, total_distance=total_distance, lng=longitude, lat=latitude)


@app.route('/pack', methods=["GET", "POST"])
def display_pack():
    form = PetSearchForm()
    friends = set()
    for pet in current_user.pets:
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        for existing_friend in existing_friends:
            friends.add(existing_friend.pet)

    if form.validate_on_submit():
        name_search = form.name_search.data
        possible_matches = Pet.query.filter_by(pet_name=name_search).all()

        return render_template('pack_search.html', possible_matches=possible_matches)

    return render_template('pack.html', form=form, friends=friends)


@app.route('/add_friend/<friend_id>', methods=["GET", "POST"])
def add_to_pack(friend_id):
    for pet in current_user.pets:
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        print("Existing friends:", existing_friends)
        if len(existing_friends) == 0:
            print("No friends, but now we should be adding")
            friend = Friend(pet_id = pet.pet_id, friend_id = friend_id)
            reverse_friend = Friend(pet_id = friend_id, friend_id = pet.pet_id)
            db.session.add(friend)
            db.session.add(reverse_friend)
            db.session.commit()
            flash('Your pack has grown')
        for existing_friend in existing_friends:
            if existing_friend.friend_id == friend_id:
                print('IF Statement')
                flash("This pet is already in your pack!")
                return render_template('homepage.html')
            else:
                print("Else statement")
                friend = Friend(pet_id = pet.pet_id, friend_id = friend_id)
                reverse_friend = Friend(pet_id = friend_id, friend_id = pet.pet_id)
                db.session.add(friend)
                db.session.add(reverse_friend)
                db.session.commmit()
                flash('Your pack has grown')

        print(pet.pet_name)
    return render_template('homepage.html')

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [InputRequired('Please enter your email address.'), Email('This field requires a valid email address')])
    first_name = StringField('First Name', [InputRequired('Please enter your first name')])
    last_name = StringField('Last Name', [InputRequired('Please enter your last name')])
    password = PasswordField('Create your password', [InputRequired('Please enter a password')])
    city = StringField("City", [InputRequired("Enter City of residence.")])
    state = StringField("State", [InputRequired("Enter the State of residence.")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField('Email Address', [InputRequired('Please enter your email address.'), Email('This field requires a valid email address')])
    password = PasswordField('Enter your password', [InputRequired('Please enter your password')])
    submit = SubmitField("Login")

class PetRegistrationForm(FlaskForm):
    name = StringField("Name", [InputRequired("Enter your pet's name")] )
    breed = StringField("Breed", [InputRequired("Enter the breed of your pet")])
    birthday = DateField("Birthday", [InputRequired("Enter your pet's birthday (or best guess)")])
    

    submit = SubmitField("Add Pet")
    

class PetEditForm(FlaskForm):
    name = StringField("Name", [InputRequired("Update your pet's name")] )
    breed = StringField("Breed", [InputRequired("Update the breed of your pet")])
    birthday = DateField("Birthday", [InputRequired("Update your pet's birthday")])
    submit = SubmitField("Submit Changes")

class ActivityForm(FlaskForm):
    activity_name = StringField("Activity Title", [InputRequired("Please enter a name for your activity")])
    activity_type = SelectField("Activity Type", choices=["Walk", "Run", "Hike", "Swim", "Other"])
    pet_select = SelectMultipleField("Pet Select", coerce=int)
    date = DateField("Date", [InputRequired("Enter the date of the activity")])

    gpx_file = FileField("GPX File")

    submit = SubmitField("Create Activity")

class PetSearchForm(FlaskForm):
    name_search = StringField("Search the name of your future pack member", [InputRequired("Enter the name of your furry friend")] )
    search = SubmitField("Search")


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(port=5000, host='0.0.0.0')

