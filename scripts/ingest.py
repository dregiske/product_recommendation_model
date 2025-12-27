from website import db

from website.models import Product

import pandas as pd

import numpy as np

from sqlalchemy import select

required_columns = [
	"product_asin",
	"product_title",
	"product_url"
]

# Helper functions

def clean_str(s):
	return s.astype(str).fillna("").str.strip()

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


def normalize_csv_data(df: pd.DataFrame):
	'''
	Grab the CSV data and normalize it
	to match database SQL models
	'''
	df = df.copy()

	df.columns = [c.strip() for c in df.columns]

	if "asin" in df.columns:
		df["product_asin"] = df["asin"]
	elif "product_asin" in df.columns:
		df["product_asin"] = df["product_asin"]
	else:
		raise ValueError("CSV missing ASIN column.")
	
	if "product_title" not in df.columns:
		df["product_title"] = ""
	if "product_url" not in df.columns:
		df["product_url"] = ""

	missing = [ c for c in required_columns if c not in df.columns]
	if missing:
		raise ValueError(f"CSV Missing required columns: {missing}")

	# Clean required string columns
	df["product_asin"] 	= clean_str(df["product_asin"])
	df["product_title"] = clean_str(df["product_title"])
	df["product_url"] 	= clean_str(df["product_url"])

	# Clean optional string columns
	for col in ["product_photo", "country"]:
		if col in df.columns:
			df[col] = clean_str(df[col])
		else:
			df[col] = ""

	df["country"] = df["country"].str.upper().str.slice(0,2)

	# Clean numeric columns
	if "product_price" in df.columns:
		df["product_price"] = df["product_price"].apply(to_float)
	else:
		df["product_price"] = np.nan

	if "product_star_rating" in df.columns:
		df["product_star_rating"] = df["product_star_rating"].apply(to_float)
	else:
		df["product_star_rating"] = np.nan

	if "product_num_ratings" in df.columns:
		df["product_num_ratings"] = df["product_num_ratings"].apply(to_int)
	else:
		df["product_num_ratings"] = np.nan

	keep = [
		"product_asin",
		"product_title",
		"product_price",
		"product_star_rating",
		"product_num_ratings",
		"product_url",
		"product_photo",
		"country"
	]
	df = df[keep]

	# Removing empty ASIN, and drop duplicates
	df = df[df["product_asin"].ne("")]
	df = df.drop_duplicates(subset=["product_asin"], keep="last").reset_index(drop=True)

	df = df.replace({np.nan: None})

	return df

def upsert_into_db(df_normalized: pd.DataFrame):
	'''
	Upsert the normalized data into the database
	'''

	# Convert normalized data into dictionaries
	rows = df_normalized.to_dict(orient="records")
	if not rows:
		return (0, 0)
	
	asins = [r["product_asin"] for r in rows]

	existing = db.session.execute(
		select(Product).where(Product.product_asin.in_(asins))
	).scalars().all()
	existing_by_asin = {p.product_asin: p for p in existing}

	inserted = 0
	updated  = 0

	for row in rows:
		asin = row["product_asin"]
		obj = existing_by_asin.get(asin)

		if obj is None:
			obj = Product(
				product_asin=asin,
				product_title=row["product_title"],
				product_url=row["product_url"],
				product_photo=row.get("product_photo") or None,
				country=row.get("country") or None,
				product_price=row["product_price"],
				product_star_rating=row["product_star_rating"],
				product_num_ratings=row["product_num_ratings"],
			)
			db.session.add(obj)
			inserted += 1
		else:
			changed = False

			def set_if_diff(attr, new_val):
				nonlocal changed
				if getattr(obj, attr) != new_val:
					setattr(obj, attr, new_val)
					changed = True

			set_if_diff("product_title", row["product_title"])
			set_if_diff("product_url", row["product_url"])
			set_if_diff("product_photo", row.get("product_photo") or None)
			set_if_diff("country", row.get("country") or None)
			set_if_diff("product_price", row.get("product_price"))
			set_if_diff("product_star_rating", row.get("product_star_rating"))
			set_if_diff("product_num_ratings", row.get("product_num_ratings"))

			if changed:
				updated += 1
	
	db.session.commit()
	return (inserted, updated)