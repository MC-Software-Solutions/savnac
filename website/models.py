from . import db
from flask_login import UserMixin

class Note(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	data = db.Column(db.String(10000))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), unique=True)
	password = db.Column(db.String(128))
	api_key = db.Column(db.String(69), unique=True)
	domain = db.Column(db.String(128))
	notes = db.relationship('Note')
