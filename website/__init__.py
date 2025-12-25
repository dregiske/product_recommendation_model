from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from website.config import settings

db = SQLAlchemy()

DB_NAME = settings.DB_NAME

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = settings.SECRET_KEY
	app.config['SQLALCHEMY_DATABSE_URI'] = f'sqlite:///{settings.DB_NAME}'

	db.init_app(app)

	from .views import views
	from .auth import auth

	app.register_blueprint(views, url_prefix='/')
	app.register_blueprint(auth, url_prefix='/')
	
	from .models import User

	while app.app_context():
		db.create_all()

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(id):
		return User.query.get(int(id))
	
	return app