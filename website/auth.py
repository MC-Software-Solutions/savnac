from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
	session.pop('_flashes', None)
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		
		user = User.query.filter_by(username=username).first()
		if user:
			if check_password_hash(user.password, password):
				flash('Successfully logged in!', category='success')
				login_user(user, remember=True)
				return redirect(url_for('pages.todo'))
			else:
				flash('Incorrect password.', category='error')
		else:
			flash('User does not exist.', category='error')	
	return render_template('login.html', user=current_user)

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
	session.pop('_flashes', None)
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm-password')
		api_token = request.form.get('api-token')
		domain = request.form.get('domain')
		user = User.query.filter_by(username=username).first()

		try:
			r = requests.get(f'https://{domain}/api/v1/courses?access_token={api_token}')
			if r.status_code == 200:
				api_domain_check = True
			else:
				api_domain_check = False
		except:
			api_domain_check = False

		if user and user.is_active:
			flash('User already exists.', category='error')
		elif len(username) == 0:
			flash('Username cannot empty.', category='error')
		elif len(password) == 0:
			flash('Password cannot empty.', category='error')
		elif password != confirm_password:
			flash('Passwords must match.', category='error')
		elif len(api_token) == 0:
			flash('API token cannot be empty.', category='error')
		elif len(domain) == 0:
			flash('Organization domain cannot empty.', category='error')
		elif not api_domain_check:
			flash('Your API token or domain name is invalid.', category='error')
		else:
			new_user = User(username=username, password=generate_password_hash(password, method='sha256'), api_token=api_token, domain=domain)
			db.session.add(new_user)
			db.session.commit()
			login_user(new_user, remember=True)
			flash('Account created!', category='success')
			return redirect(url_for('pages.todo'))
	return render_template('sign_up.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
	session.pop('_flashes', None)
	logout_user()
	return redirect(url_for('auth.login'))
