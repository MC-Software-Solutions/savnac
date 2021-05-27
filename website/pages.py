from flask import Blueprint
from flask import render_template

pages = Blueprint('pages',__name__)

@pages.route('/')
def home():
	return '<a href="/login">Login</a>'
