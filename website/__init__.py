from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

	return app
