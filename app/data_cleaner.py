
import re
import argparse
import numpy as np
import pandas as pd

def clean_price(v):
    if pd.isna(v):
        return np.nan
    s = re.sub(r"[^\d.]", "", str(v))
    try:
        return float(s)
    except:
        return np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="Path to raw Amazon bestsellers CSV")
    ap.add_argument("--out_csv", required=True, help="Where to write cleaned CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)

    # Keep and standardize expected columns if present
    keep = [
        "rank","asin","product_title","product_price",
        "product_star_rating","product_num_ratings",
        "product_url","product_photo","country","page","rank_change_label"
    ]
    cols = [c for c in keep if c in df.columns]
    df = df[cols].copy()

    # Clean price -> float
    if "product_price" in df.columns:
        df["product_price"] = df["product_price"].apply(clean_price)

    # Coerce numerics
    for col in ["product_star_rating","product_num_ratings","rank","page","rank_change_label"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing numeric columns with column median
    for col in ["product_price","product_star_rating","product_num_ratings"]:
        if col in df.columns:
            med = df[col].median()
            df[col] = df[col].fillna(med)

    # Drop obvious empty titles/asin/urls if present
    for needed in ["asin","product_title"]:
        if needed in df.columns:
            df = df[df[needed].notna()]

    df.to_csv(args.out_csv, index=False)
    print(f"Cleaned {len(df)} rows -> {args.out_csv}")

if __name__ == "__main__":
    main()
