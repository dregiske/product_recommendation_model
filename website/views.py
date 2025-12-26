from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from rec_system.recommender import recommend_adhoc

from .config import settings

# from .models import SearchHistory

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
		rating = request.method.get('rating', type=float)
		country = request.method.get('country')
		num_ratings = 0

		results = recommend_adhoc(
			product_title=name,
			product_price=price,
			product_star_rating=rating,
			country=country,
			product_num_ratings=num_ratings,
			k=settings.DEFAULT_K
		)

		# TODO: record searches


	return render_template("home.html", user=current_user, results=results)

@views.route('/delete-product', methods=['POST'])
def delete_search_history():
	# TODO: delete the search history for user
	pass