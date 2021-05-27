from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		if len(username) == 0:
			flash('Username cannot empty.', category='error')
		elif len(password) == 0:
			flash('Password cannot empty.', category='error')
		else:
			# log in user
			flash('Successfully logged in!')
	return render_template('login.html', text="Test")

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm-password')
		api_token = request.form.get('api-token')
		domain = request.form.get('domain')
		if len(username) == 0:
			flash('Username cannot empty.', category='error')
		elif len(password) == 0:
			flash('Password cannot empty.', category='error')
		elif password != confirm_password:
			flash('Passwords must match.', category='error')
		elif len(api_token) == 0:
			flash('API token cannot empty.', category='error')
		elif len(domain) == 0:
			flash('Organization domain cannot empty.', category='error')
		else:
			flash('Account created!', category='success')
			# database stuff
			
	return render_template('sign_up.html')

@auth.route('/logout')
def logout():
	return '<h1>Logout</h1>'
