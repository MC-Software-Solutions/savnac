from flask import Blueprint, render_template, request, Flask
from flask_login import login_required, current_user
from . import db
from .models import User
import requests
import datetime

pages = Blueprint('pages',__name__)

@pages.route('/')
def home():
	return render_template('home.html', user=current_user)

@pages.route('/courses')
@login_required
def list_courses():
	url = f'https://{current_user.domain}/api/v1/courses/'
	params = {'access_token':current_user.api_token.strip(),'enrollment_state':'active','exclude_blueprint_courses':'true','per_page':'100'}
	r = requests.get(url,params=params)
	data = [(item['id'], item['name']) for item in r.json()]
	return render_template('courses.html', user=current_user, data=data)

@pages.route('/courses/<course_id>')
@login_required
def list_assignments(course_id):
	url = f'https://{current_user.domain}/api/v1/courses/{course_id}/assignments/'
	params = {'access_token':current_user.api_token,'order_by':'due_at','per_page':'100','include':['submission']}
	r = requests.get(url,params=params)
	data = [(item['id'], item['name'], datetime.datetime.strptime(item['due_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p') if item['due_at'] else None, item['points_possible'], item['submission']['workflow_state'].title()) for item in r.json()]
	data.reverse()
	return render_template('assignments.html', user=current_user, data=data, course_id=course_id)

@pages.route('/courses/<course_id>/assignments/<assignment_id>')
@login_required
def assignment_details(course_id,assignment_id):
	url = f'https://{current_user.domain}/api/v1/courses/{course_id}/assignments/{assignment_id}'
	params = {'access_token':current_user.api_token,'order_by':'due_at','include':['submission']}
	r = requests.get(url,params=params)
	data = r.json()
	if data['due_at']:
		due_date = datetime.datetime.strptime(data['due_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p')
	else:
		due_date = None
	from .other import removeTags
	if data['description']:
		data['description'] = removeTags(data['description'])
	return render_template('assignment_details.html', user=current_user, data=data, course_id=course_id, due_date=due_date)

@pages.route('<stuff>')
def path(stuff):
	return render_template('not_found.html', user=current_user)

def register_404_pages(app):
	@app.errorhandler(404)
	def notfound():
		return render_template('not_found.html', user=current_user)
