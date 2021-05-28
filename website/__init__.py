from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'supersecretkeythatyouwillnotread'
	app.config['SQLALCHEMY_DATABSE_URI'] = f'sqlite:///{DB_NAME}'
	db.init_app(app)

	from .pages import pages
	from .auth import auth
	
	app.register_blueprint(pages,url_prefix='/')
	app.register_blueprint(auth,url_prefix='/')

	from .models import User, Note
	create_database(app)

	return app

def create_database(app):
	if not path.exists(f'website/{DB_NAME}'):
		db.create_all(app=app)
		print('Created database')
