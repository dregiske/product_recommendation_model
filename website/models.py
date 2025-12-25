from flask_login import UserMixin

from sqlalchemy.sql import func

from . import db

class User(db.model, UserMixin):
	id				= db.Column(db.Integer, primary_key=True)
	email			= db.Column(db.String(150), unique=True)
	password		= db.Column(db.String(150))
	first_name		= db.Column(db.String(100))
	search_history	= db.relationship(
		'SearchHistory',
		backref='user',
		lazy=True
	)

class Product(db.model):
	id				= db.Column(db.Integer, primary_key=True)
	product_name	= db.Column(db.String(100))
	price			= db.Column(db.Integer)
	country			= db.Column(db.String(2))
	rating			= db.Column(db.Integer)
	num_rating		= db.Column(db.Integer)
	search_history	= db.relationship(
		'SearchHistory',
		backref='product',
		lazy=True,
	)

class SearchHistory(db.model):
	id				= db.Column(db.Integer, primary_key=True)
	user_id			= db.Column(
		db.Integer,
		db.ForgeinKey('user.id'),
		nullable=False
	)
	product_id		= db.Column(
		db.Integer,
		db.ForgeinKey('product.id'),
		nullable=False
	)
	searched_at		= db.Column(db.DateTime(timezone=True), default=func.now())