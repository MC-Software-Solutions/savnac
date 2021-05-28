from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
from .models import User

pages = Blueprint('pages',__name__)

@pages.route('/')
def home():
	return render_template('home.html', user=current_user)

@login_required
@pages.route('/courses')
def courses():
	return render_template('courses.html', user=current_user)
