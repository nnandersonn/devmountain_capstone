from curses import update_lines_cols
from random import choices
from sqlite3 import connect
from turtle import distance
from flask import Flask, render_template, redirect, request, flash, session
from numpy import empty
from wtforms import Form, BooleanField, StringField, DateField, PasswordField, SubmitField, SelectField, SelectMultipleField, validators, IntegerField
from wtforms.validators import InputRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import delete, desc
from dotenv import load_dotenv
from datetime import datetime
import arrow
import requests
import json
import os
import math

from model import Pet_Activity, User, Pet, Activity, GPS_Point, Friend, connect_to_db, db
from gpx import parse_file
from map import create_map
from weather import get_forecast, should_i_walk

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route('/')
def index():
    """Homepage"""
    weather = None
    weather_sentence = None
    upcoming_birthdays = None
    if current_user.is_active:
        weather = get_forecast(current_user.city)
        weather_sentence = should_i_walk(weather['current_temp'], weather['current_weather'])
        print( weather_sentence)

        upcoming_birthdays = get_pack_birthdays()

    return render_template('homepage.html', weather = weather, weather_sentence=weather_sentence, upcoming_birthdays=upcoming_birthdays)

@app.route('/register', methods=["GET", "POST"])
def register():
    """Display form to register for account"""
    form = RegistrationForm()

    if form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        city = request.form['city'].capitalize()
        state = request.form['state']
        match = User.query.filter_by(email=email).first()
        if match is None:
            user = User(email = email, password = password, first_name = first_name, last_name = last_name, city = city, state = state)
            db.session.add(user)
            db.session.commit()
            flash('Account created!')
            return redirect('/')
        else:
            flash('Account already created with this email')
            return render_template('register.html', form=RegistrationForm())

    return render_template('register.html', form=form)

# @app.route('/register', methods=["POST"])
# def check_registration():
#     email = request.form['email']
#     password = request.form['password']
#     first_name = request.form['first_name']
#     last_name = request.form['last_name']
#     city = request.form['city'].capitalize()
#     state = request.form['state']
#     match = User.query.filter_by(email=email).first()
#     if match is None:
#         user = User(email = email, password = password, first_name = first_name, last_name = last_name, city = city, state = state)
#         db.session.add(user)
#         db.session.commit()
#         flash('Account created!')
#         return redirect('/')
#     else:
#         flash('Account already created with this email')
#         return render_template('register.html', form=RegistrationForm())

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']
        match = User.query.filter_by(email=email).first()
        if match: 
            if match.password == password: 
                login_user(match)
                flash("You are successfully logged in!")
                return redirect('/')
            else:
                flash("Email/Password not valid. Register for an account if you have not created one already")
                return redirect('/')
        else:
                flash("Email/Password not valid. Register for an account if you have not created one already")
                return redirect('/')

    return render_template('login.html', form=form)


@app.route('/profile')
def profile():

    return render_template('profile.html')

@app.route('/add_pet', methods=["GET"])
def add_pet():
    form = PetRegistrationForm()



    return render_template('add_pet.html', form=form)

@app.route('/add_pet', methods=["POST"])
def create_pet():
    pet_name = request.form['name'].capitalize()
    breed = request.form['breed'].capitalize()
    birthday = request.form['birthday']
    pet = Pet(pet_name = pet_name, user_id = current_user.user_id, breed = breed, birthday = birthday)
    db.session.add(pet)
    db.session.commit()
    flash(f"Your pet {pet_name} has been added to your account!")
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect('/')

@app.route('/pets')
def display_pets():
    pets = get_pets()
    print(pets)

    return render_template('pets.html', pets=pets)

@app.route('/edit_pet/<pet_id>', methods=["GET", "POST"])
def edit_pet(pet_id):
    pet = Pet.query.filter_by(pet_id = pet_id).first()
    form = PetEditForm()
    form.name.data = pet.pet_name
    form.breed.data = pet.breed
    form.birthday.data = pet.birthday

    if form.validate_on_submit():
        pet = Pet.query.filter_by(pet_id = pet_id).first()
        pet_name = request.form['name']
        breed = request.form['breed']
        birthday = request.form['birthday']
        pet.pet_name = pet_name
        pet.breed = breed
        pet.birthday = birthday
        db.session.commit()
        flash(f"{pet_name}'s info has been successfully updated!")
        return redirect('/')


    return render_template('edit_pet.html', pet=pet, form=form)

# @app.route('/edit_pet/<pet_id>', methods=["POST"])
# def update_pet(pet_id):
#     pet = Pet.query.filter_by(pet_id = pet_id).first()
#     pet_name = request.form['name']
#     breed = request.form['breed']
#     birthday = request.form['birthday']
#     pet.pet_name = pet_name
#     pet.breed = breed
#     pet.birthday = birthday
#     db.session.commit()
#     flash(f"{pet_name}'s info has been successfully updated!")
#     return redirect('/')
    
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

        pet = form.pet_select.data
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
    flash(f'Activity {activity.activity_name} successfully removed')
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
    max_speed = get_max_speed(activity_id)
    avg_speed = get_avg_speed(activity_id)
    total_distance = get_total_distance(activity_id)

    return render_template('display_activity.html', activity = activity, m_h = m_h, max_speed=max_speed, avg_speed=avg_speed, total_distance=total_distance, lng=longitude, lat=latitude)


@app.route('/pack', methods=["GET", "POST"])
def display_pack():
    form = PetSearchForm()
    pack = set()
    total_distances={}
    for pet in current_user.pets:
        pack.add(pet)
        total_distance = total_distance_for_pet(pet.pet_id)
        total_distances[pet.pet_name] = total_distance
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        for existing_friend in existing_friends:
            friend_id = existing_friend.friend_id
            friend = Pet.query.filter_by(pet_id = friend_id).first()
            pack.add(friend)
            total_distance = total_distance_for_pet(friend_id)
            total_distances.update({friend.pet_name: total_distance})
    leaderboard = get_pack()

    if form.validate_on_submit():
        name_search = form.name_search.data
        possible_matches = Pet.query.filter_by(pet_name=name_search).all()

        return render_template('pack_search.html', possible_matches=possible_matches)

    return render_template('pack.html', form=form, pack=pack, total_distances=total_distances, leaderboard=leaderboard)


@app.route('/add_friend/<friend_id>', methods=["GET", "POST"])
def add_to_pack(friend_id):
    for pet in current_user.pets:
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        print("Existing friends:", existing_friends)
        if len(existing_friends) == 0:
            friend = Friend(pet_id = pet.pet_id, friend_id = friend_id)
            reverse_friend = Friend(pet_id = friend_id, friend_id = pet.pet_id)
            db.session.add(friend)
            db.session.add(reverse_friend)
            db.session.commit()
            flash('Your pack has grown')
        for existing_friend in existing_friends:
            if existing_friend.friend_id == friend_id:
                flash("This pet is already in your pack!")
                return redirect('/')
            else:
                friend = Friend(pet_id = pet.pet_id, friend_id = friend_id)
                reverse_friend = Friend(pet_id = friend_id, friend_id = pet.pet_id)
                db.session.add(friend)
                db.session.add(reverse_friend)
                db.session.commit()
                flash('Your pack has grown')

        print(pet.pet_name)
    return redirect('/')

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
    pet_select = SelectField("Pet Select", coerce=int)
    date = DateField("Date", [InputRequired("Enter the date of the activity")])

    gpx_file = FileField("GPX File", [InputRequired("Upload a .gpx file")])

    submit = SubmitField("Create Activity")

class PetSearchForm(FlaskForm):
    name_search = StringField("Add someone to the pack", [InputRequired("Enter the name of your furry friend")] )
    search = SubmitField("Search")


def get_total_distance(activity_id):
    points = GPS_Point.query.filter_by(activity_id = activity_id).all()
    distance = []
    for point in points:
        distance.append(point.distance)
    total_distance = round(sum(distance)/1609.344, 2)
    return total_distance

def total_distance_for_pet(pet_id):
    pet_activities = Pet_Activity.query.filter_by(pet_id=pet_id).all()
    grand_total=0
    activity_ids = [p_a.activity_id for p_a in pet_activities]
    for activity_id in activity_ids:
        activities = Activity.query.filter_by(activity_id=activity_id).all()
        for activity in activities:
            grand_total += get_total_distance(activity.activity_id)

    return round(grand_total, 2)

def get_max_speed(activity_id):
    points = GPS_Point.query.filter_by(activity_id = activity_id).all()
    speed = []
    for point in points:
        speed.append(point.speed)
    max_speed = round(max(speed), 2)
    return max_speed

def get_avg_speed(activity_id):
    points = GPS_Point.query.filter_by(activity_id = activity_id).all()
    speed = []
    for point in points:
        speed.append(point.speed)
    avg_speed = round((sum(speed)/len(speed)), 2)
    return avg_speed

def get_activities(user):
    all_activities = {}
    for pet in user.pets:
        for pet_activity in pet.pet_activities:
            all_activities[pet.pet_id] = pet_activity.activities

    return all_activities
    
def get_pack():
    pack = set()
    total_distances={}
    for pet in current_user.pets:
        pack.add(pet)
        total_distance = total_distance_for_pet(pet.pet_id)
        total_distances[pet.pet_name] = total_distance
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        for existing_friend in existing_friends:
            friend_id = existing_friend.friend_id
            friend = Pet.query.filter_by(pet_id = friend_id).first()
            pack.add(friend)
            total_distance = total_distance_for_pet(friend_id)
            total_distances.update({friend.pet_name: total_distance})
    return sorted(total_distances.items(), key= lambda ele:ele[1], reverse = True)

def get_pets():
    pets = []
    for pet in current_user.pets:
        current_pet = {}
        current_pet["pet_id"] = pet.pet_id
        current_pet["pet_name"] = pet.pet_name
        current_pet["breed"] = pet.breed
        current_pet["age"] = get_pet_age(pet)
        pets.append(current_pet)

    return pets



def get_pet_age(pet):
    print(pet.birthday.year)
    current_date = arrow.utcnow()
    age = current_date - arrow.get(pet.birthday)
    age = (age.days)/365.25
    if age < 1:
        age = round(age, 1)
    else:
        age = math.floor(age)
    return age

def get_pack_birthdays():
    pack = set()
    for pet in current_user.pets:
        pack.add(pet)
        existing_friends = Friend.query.filter_by(pet_id = pet.pet_id).all()
        for existing_friend in existing_friends:
            friend_id = existing_friend.friend_id
            friend = Pet.query.filter_by(pet_id = friend_id).first()
            pack.add(friend)

    pets = []
    for pet in pack:
        current_pet = {}
        current_pet["pet_name"] = pet.pet_name
        birthday = arrow.get(pet.birthday)
        today = arrow.now()
        how_close = (((today-birthday).days)/365.25)%1
        current_pet["close_to_birthday"] = how_close 
        pet_birthday = arrow.get(pet.birthday)
        current_pet["birthday"] = pet_birthday.format('MMMM DD')
        current_pet["upcoming_age"] = math.floor(get_pet_age(pet)+1)
        pets.append(current_pet)

    def sort_pets(e):
        return e['close_to_birthday']

    pets.sort(reverse=True, key=sort_pets)
    print(pets)

    return pets


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    app.run(port=5000, host='0.0.0.0')

