from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.model, UserMixin):
    """Human user of Track the Pack"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    password = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64))

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class Pet(db.model):
    """Pet of a given user"""

    __tablename__ = "pets"

    pet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    breed = db.Column(db.String(64))
    birthday = db.Column(db.Date)

    user = db.relationship("User", backref=db.backref('pets', order_by=pet_id))

    def __repr__(self):
        return f"<Pet pet_id={self.pet_id} name={self.pet_name} birthday={self.birthday}>"


class Activity(db.model):
    """Activities of a pet"""

    __tablename__ = 'activities'

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))
    activity_date = db.Column(db.Date)
    activity_type = db.Column(db.String(64))

    pet = db.relationship("Pet", bacref=db.backref("activities", order_by=activity_id))


class GPS_Point(db.model):
    """Stores gps data for activity"""

    __tablename__ = 'gps_points'

    gps_point_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'))
    time = db.Column(db.DateTime)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    elevation = db.Column(db.Float)
    distance = db.Column(db.Float)
    speed = db.Column(db.Float)

    activity = db.relationship("Activity", bacref=db.backref("gps_points", order_by=gps_point_id))


class Friend(db.model):
    """Stores friend lists for pets"""

    __tablename__ = 'friends'

    friend_list_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))

    pet = db.relationship("Pet", backref=db.backref('friends'), order_by=friend_list_id)