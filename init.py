from model import db, connect_to_db
from server import app

connect_to_db(app)
with app.app_context():
    db.create_all()