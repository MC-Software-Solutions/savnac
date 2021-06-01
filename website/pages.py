from flask import Blueprint, render_template, request, Flask, session, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from .other import removeTags
import requests
import datetime
import random

pages = Blueprint('pages',__name__)

@pages.route('/')
def home():
	image = f'study_{random.randint(0,4)}.png'
	return render_template('home.html', user=current_user, image=image)

@pages.route('/courses')
@login_required
def list_courses():
	if request.args.get('assignments'):
		dest = 'assignments'
	elif request.args.get('announcements'):
		dest = 'announcements'
	else:
		dest = 'assignments'
	url = f'https://{current_user.domain}/api/v1/courses/'
	params = {'access_token':current_user.api_token.strip(),'enrollment_state':'active','exclude_blueprint_courses':'true','per_page':'100'}
	r = requests.get(url,params=params)
	data = [(item['id'], item['name']) for item in r.json()]
	return render_template('courses.html', user=current_user, data=data, dest=dest)

@pages.route('/courses/<course_id>/assignments')
@login_required
def list_assignments(course_id):
	url = f'https://{current_user.domain}/api/v1/courses/{course_id}/assignments/'
	params = {'access_token':current_user.api_token,'order_by':'due_at','per_page':'100','include':['submission']}
	r = requests.get(url,params=params)
	data = [(item['id'], item['name'], datetime.datetime.strptime(item['due_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p') if item['due_at'] else None, item['points_possible'], item['submission']['workflow_state'].title()) for item in r.json()]
	data.reverse()
	return render_template('assignments.html', user=current_user, data=data, course_id=course_id)

@pages.route('/courses/<course_id>/announcements')
@login_required
def list_announcements(course_id):
	url = f'https://{current_user.domain}/api/v1/announcements/'
	params = {'access_token':current_user.api_token,'context_codes[]':f'course_{str(course_id)}','per_page':'100'}
	r = requests.get(url,params=params)
	data = r.json()
	for item in data:
		if item['posted_at']:
			item['posted_at'] = datetime.datetime.strptime(item['posted_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p')
	return render_template('announcements.html', user=current_user, data=data, course_id=course_id)

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
	if data['description']:
		data['description'] = removeTags(data['description'])
	return render_template('assignment_details.html', user=current_user, data=data, course_id=course_id, due_date=due_date)

@pages.route('/courses/<course_id>/announcements/<announcement_id>')
@login_required
def announcement_details(course_id, announcement_id):
	url = f'https://{current_user.domain}/api/v1/announcements/'
	params = {'access_token':current_user.api_token,'context_codes[]':f'course_{str(course_id)}','per_page':'100'}
	r = requests.get(url,params=params)
	for item in r.json():
		if item['id'] == int(announcement_id):
			data = item
			if data['message']:
				data['message'] = removeTags(data['message'])
			if data['posted_at']:
				data['posted_at'] = datetime.datetime.strptime(data['posted_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p')
			return render_template('announcement_details.html', user=current_user, data=data, course_id=course_id)

@pages.route('/todo')
@login_required
def todo():
	url = f'https://{current_user.domain}/api/v1/users/self/missing_submissions/'
	params = {'access_token':current_user.api_token}
	r = requests.get(url,params=params)
	data = r.json()
	for item in data:
		if item['due_at']:
			item['due_at'] = datetime.datetime.strptime(item['due_at'],'%Y-%m-%dT%H:%M:%Sz').strftime('%m/%d/%Y %I:%M %p')
	return render_template('todo.html', user=current_user, data=data)

@pages.route('/feedback', methods=['GET','POST'])
def feedback():
	#session.pop('_flashes', None)
	if request.method == 'POST':
		first_name = request.form.get('fname')
		last_name = request.form.get('lname')
		email = request.form.get('email')
		feedback = request.form.get('feedback')
		if len(first_name) == 0:
			flash('First name cannot be empty.', category='feedback-error')
		elif len(last_name) == 0:
			flash('Last name cannot be empty.', category='feedback-error')
		elif len(email) == 0:
			flash('Email cannot be empty.', category='feedback-error')
		elif len(feedback) == 0:
			flash('Feedback cannot be empty.', category='feedback-error')
		else:
			flash('Your feedback has been submitted!', category='feedback-success')
			print(first_name, last_name, email, feedback)
			return redirect(url_for('pages.feedback'))
	return render_template('feedback.html', user=current_user)

@pages.route('/settings', methods=['GET','POST'])
@login_required
def settings():
	if request.method == 'POST':
		api_token = request.form.get('api_token')
		domain = request.form.get('domain')
		
		try:
			r = requests.get(f'https://{domain}/api/v1/courses?access_token={api_token}')
			if r.status_code == 200:
				api_domain_check = True
			else:
				api_domain_check = False
		except:
			api_domain_check = False

		if len(api_token) == 0:
			flash('API token cannot be empty.', category='settings-error')
		elif len(domain) == 0:
			flash('Organization domain cannot be empty.', category='settings-error')
		elif not api_domain_check:
			flash('Your API token or domain name is invalid.', category='settings-error')
		else:
			user_update = User.query.filter_by(id=current_user.id).first()
			user_update.api_token = api_token
			user_update.domain = domain
			db.session.commit()
			flash('Your settings have been updated!', category='settings-success')
			return redirect(url_for('pages.settings'))
	return render_template("settings.html", user=current_user)

@pages.route('/change_password', methods=['GET','POST'])
@login_required
def change_password():
	if request.method == 'POST':
		current_password = request.form.get('current_password')
		new_password = request.form.get('new_password')
		confirm_new_password = request.form.get('confirm_new_password')
		if len(current_password) == 0:
			flash('Current password cannot be empty.', category='password-error')
		elif not check_password_hash(current_user.password, current_password):
			flash('Current password is incorrect.', category='password-error')
		elif len(new_password) == 0:
			flash('New password cannot be empty.', category='password-error')
		elif len(confirm_new_password) == 0:
			flash('Confirm new password cannot be empty.', category='password-error')
		elif new_password != confirm_new_password:
			flash('Passwords must match.', category='password-error')
		else:
			user_update = User.query.filter_by(id=current_user.id).first()
			user_update.password = generate_password_hash(new_password, method='sha256')
			db.session.commit()
			flash('Password changed!', category='password-success')
			return redirect(url_for('pages.settings'))
	return redirect(url_for('pages.settings'))
