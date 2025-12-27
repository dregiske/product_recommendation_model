import pandas as pd

from website import create_app, db
from website.models import Product
from .ingest import normalize_csv_data, upsert_into_db

def main():
	app = create_app()

	with app.app_context():
		df = pd.read_csv("data/Amazon_bestsellers_items_2025.csv")

		df_normalized = normalize_csv_data(df)

		inserted, updated = upsert_into_db(df_normalized)

		print(f"Inserted: {inserted}, Updated: {updated}")

if __name__ == "__main__":
	main()