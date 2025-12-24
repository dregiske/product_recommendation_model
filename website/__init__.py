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