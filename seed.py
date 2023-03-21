# TODO: look at imports
from app import app
from models import db, connect_db, Cupcake

db.drop_all()
db.create_all()