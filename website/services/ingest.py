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
	
	if "asin" in df.columns:
		df["asin"] = df["asin"].astype(str).str.strip()
	else:
		print("Error, needs ASIN")
	
	if "product_url" in df.columns:
		df["product_url"] = df["product_url"].astype(str).str.strip()
	else:
		df["product_url"] = ""
	
	def to_float(x):
		try:
			return float(x)
		except Exception:
			return np.nan
		
	def to_int(x):
		try:
			return int(float(x))
		except Exception:
			return np.nan
		
	if "product_price" in df.columns:
		df["product_price"] = df["product_price"].apply(to_float)
	else:
		df["product_price"] = np.nan

	if "product_star_rating" in df.columns:
		df["product_star_rating"] = df["product_star_rating"].apply(to_float)
	else:
		df["product_price"] = np.nan

	if "product_num_ratings" in df.columns:
		df["product_num_ratings"] = df["product_num_ratings"].apply(to_int)
	else:
		df["product_num_ratings"] = np.nan

	keep = [
		"asin",
		"product_title",
		"product_price",
		"product_star_rating",
		"product_num_ratings",
		"product_url",
		"product_photo",
		"country"
	]
	keep = [col for col in keep if col in df.columns]
	df = df[keep].dropna(subset=["unique_key"])
	df = df[df["unique_key"] != ""]
	return df



def upsert_into_db(df_normalized: pd.DataFrame):
	'''
	Upsert the normalized data into the database
	'''
	# TODO: upsert into db
	pass