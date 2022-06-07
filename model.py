from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Human user of Track the Pack"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    password = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    email = db.Column(db.String(64))

    pets = db.relationship("Pet", backref='users')

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class Pet(db.Model):
    """Pet of a given user"""

    __tablename__ = "pets"

    pet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    breed = db.Column(db.String(64))
    birthday = db.Column(db.Date)

    pet_activities = db.relationship("Pet_Activity", backref='pets')
    

    def __repr__(self):
        return f"<Pet pet_id={self.pet_id} name={self.pet_name} birthday={self.birthday}>"


class Activity(db.Model):
    """Activities of a pet"""

    __tablename__ = 'activities'

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    activity_name = db.Column(db.String(64))
    activity_type = db.Column(db.String(64))
    date = db.Column(db.Date)

    gps_points = db.relationship("GPS_Point", backref='activities')
    def __repr__(self):
        return f"<Activity: activity_id={self.activity_id} name={self.activity_name} type={self.activity_type}>"

class Pet_Activity(db.Model):
    """Junction table to join many pets to many activities"""

    __tablename__ = 'pet_activities'
    pet_activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'))
    
    activities = db.relationship("Activity", backref='pet_activities')



class GPS_Point(db.Model):
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



class Friend(db.Model):
    """Stores friend lists for pets"""

    __tablename__ = 'friends'

    friend_list_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'))

    pet = db.relationship("Pet", foreign_keys=[pet_id])
    # friend = db.relationship("Pet", foreign_keys=[friend_id])
    

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///trackthepack'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
