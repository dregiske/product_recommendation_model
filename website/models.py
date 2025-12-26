from flask_login import UserMixin

from sqlalchemy.sql import func

from . import db

class User(db.Model, UserMixin):
	id					= db.Column(db.Integer, primary_key=True)
	email				= db.Column(db.String(150), unique=True)
	password			= db.Column(db.String(150))
	first_name			= db.Column(db.String(100))
	search_history		= db.relationship(
		'SearchHistory',
		backref='user',
		lazy=True
	)

class Product(db.Model):
	id					= db.Column(db.Integer, primary_key=True)
	product_title		= db.Column(db.String(100), nullable=False)
	product_price		= db.Column(db.Integer)
	country				= db.Column(db.String(2))
	poduct_star_rating	= db.Column(db.Integer)
	product_num_ratings	= db.Column(db.Integer)
	product_url			= db.Column(db.String(200), nullable=False, unique=True)
	search_history		= db.relationship(
		'SearchHistory',
		backref='product',
		lazy=True,
	)

class SearchHistory(db.Model):
	id					= db.Column(db.Integer, primary_key=True)
	user_id				= db.Column(
		db.Integer,
		db.ForeignKey('user.id'),
		nullable=False
	)
	product_id			= db.Column(
		db.Integer,
		db.ForeignKey('product.id'),
		nullable=False
	)
	searched_at			= db.Column(db.DateTime(timezone=True), default=func.now())