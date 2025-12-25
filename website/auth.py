from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		email = request.form.get('email')
		firstName = request.form.get('firstName')
		password_create = request.form.get('password_create')
		password_confirm = request.form.get('password_confirm')

		user = User.query.filter_by(email=email).first()

		if user:
			flash('Email already exists.', category='error')
		
		else:
			if len(email) < 4:
				flash('Invalid email.', category='error')
			if len(firstName) < 2:
				flash('Invalid first name (must be greater than 1 character).', category='error')
			if password_create != password_confirm:
				flash('Passwords don\'t match', category='error')
			if len(password_create) < 7:
				flash('Password must be greater than 7 characters', category='error')
			
			else:
				hashed_password = generate_password_hash(password_confirm)
				new_user = User(
					email=email,
					password=hashed_password,
					first_name=firstName,
				)
				try:
					db.session.add(new_user)
					db.session.commit()
					flash('Account created.', category='success')
					login_user(new_user, remember=True)
					return redirect(url_for('views.home'))
				except:
					flash('Error creating new user.', category='error')

	return render_template("signup.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')

		user = User.query.filter_by(email=email).first()
		if user:
			if check_password_hash(password, user.password):
				flash('Logging in...', category='success')
				login_user(user, remember=True)
				return redirect(url_for('views.home'))
			else:
				flash('Incorrect password.', category='error')
		else:
			flash('Incorrect email.', category='error')

		return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('auth.login'))