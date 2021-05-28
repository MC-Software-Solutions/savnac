from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
from .models import User
import requests

pages = Blueprint('pages',__name__)

@pages.route('/')
def home():
	return render_template('home.html', user=current_user)

@pages.route('/courses')
@login_required
def courses():
	url = f'https://{current_user.domain}/api/v1/courses/'
	params = {'access_token':current_user.api_token.strip(),'enrollment_state':'active','exclude_blueprint_courses':'true','per_page':'100'}
	r = requests.get(url,params=params)
	data = [(item['id'], item['name']) for item in r.json()]
	return render_template('courses.html', user=current_user, data=data)

@pages.route('<stuff>')
def path(stuff):
	return render_template('not_found.html', user=current_user)
