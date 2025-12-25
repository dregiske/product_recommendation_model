from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from . import db

import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
	results = None
	if request.method == 'POST':
		name = request.method.get('product-name')
		price = request.method.get('price', type=float)
		country = request.method.get('country')
		rating = request.method.get('rating', type=float)

		

	return render_template("home.html", user=current_user, results=results)

@views.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_search_history():
	if request.method == 'POST':
		# TODO: input => a product from the user, output => 5 similar products
		# add the input product to the users search history
		pass

@views.route('/delete-product', methods=['POST'])
def delete_search_history():
	# TODO: delete the search history for user
	pass