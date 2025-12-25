import argparse

import json

from pathlib import Path

import joblib

import numpy as np

import pandas as pd

from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

NUMERIC_COLS = ["product_price", "product_star_rating", "product_num_ratings"]

def build_features(df: pd.DataFrame):
    # --- TF-IDF on product_title ---
    tfidf = TfidfVectorizer(min_df=3, ngram_range=(1, 2))
    X_text = tfidf.fit_transform(df["product_title"].astype(str))

    # --- Numeric features ---
    df_num = df[NUMERIC_COLS].copy()
    df_num["product_price"] = np.log1p(df_num["product_price"])
    df_num["product_num_ratings"] = np.log1p(df_num["product_num_ratings"])

    scaler = StandardScaler()
    X_num = scaler.fit_transform(df_num)

    # --- Combine text + numeric ---
    X = hstack([X_text, X_num]).tocsr()
    return X, tfidf, scaler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_csv", default="data/amazon_bestsellers_clean.csv")
    parser.add_argument("--out_dir", default="app/models")
    parser.add_argument("--neighbors", type=int, default=50)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.in_csv).dropna(subset=["asin", "product_title"]).reset_index(drop=True)

    X, tfidf, scaler = build_features(df)

    knn = NearestNeighbors(n_neighbors=args.neighbors, metric="cosine")
    knn.fit(X)

    # --- Save artifacts ---
    joblib.dump(tfidf, out_dir / "tfidf.joblib")
    joblib.dump(scaler, out_dir / "scaler.joblib")
    joblib.dump(knn, out_dir / "knn.joblib")

    # Save lookup table (to align ASINs with KNN index)
    keep = ["asin","product_title","product_price","product_star_rating",
            "product_num_ratings","product_url","country","rank","page"]
    cols = [c for c in keep if c in df.columns]
    df[cols].to_csv(out_dir / "lookup.csv", index=False)

    # Save metadata
    (out_dir / "meta.json").write_text(json.dumps({
        "neighbors": args.neighbors,
        "numeric_cols": NUMERIC_COLS,
        "metric": "cosine"
    }, indent=2))

    print(f"Built KNN on {len(df)} products. Artifacts saved in {out_dir}")

if __name__ == "__main__":
    main()