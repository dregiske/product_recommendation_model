from website import db

from models import User, Product, SearchHistory

import pandas as pd

import numpy as np

NUMERIC_COLS = [
	"product_price",
	"product_star_rating",
	"product_num_ratings"
]

def normalize_csv_data(df: pd.DataFrame):
	'''
	Grab the CSV data and normalize it
	to match database SQL models
	'''
	df = df.copy()

	if "product_title" in df.columns:
		df["product_title"] = df["product_title"].astype(str).fillna("").str.strip()
	else:
		df["product_title"] = ""
	# TODO: NORMALIZE DATA
	



def upsert_into_db():
	'''
	Upsert the normalized data into the database
	'''
	# TODO: INSERT INTO DB
