from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack


# ---------- Config ----------
# You can override these via environment variables if desired
MODEL_DIR = Path(os.getenv("MODEL_DIR", "app/models")).resolve()
LOOKUP_CSV = MODEL_DIR / "lookup.csv"   # produced by build_knn.py
DEFAULT_K = int(os.getenv("DEFAULT_K", "5"))


# ---------- Internal state ----------
@dataclass
class _State:
    tfidf: Any
    scaler: Any
    knn: Any
    lookup: pd.DataFrame  # same row order used during training


_STATE: Optional[_State] = None


# ---------- Loading ----------
def _ensure_loaded() -> _State:
    global _STATE
    if _STATE is not None:
        return _STATE

    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"MODEL_DIR not found: {MODEL_DIR}")

    tfidf = joblib.load(MODEL_DIR / "tfidf.joblib")
    scaler = joblib.load(MODEL_DIR / "scaler.joblib")
    knn = joblib.load(MODEL_DIR / "knn.joblib")

    # lookup.csv was saved in the same order as training data,
	# indices must match knn index
    lookup = pd.read_csv(LOOKUP_CSV)

    _STATE = _State(tfidf=tfidf, scaler=scaler, knn=knn, lookup=lookup)
    return _STATE


# ---------- Featurization (must mirror training) ----------
_NUM_COLS = ["product_price", "product_star_rating", "product_num_ratings"]


def _vectorize_rows(df_rows: pd.DataFrame, tfidf, scaler):
    # Make sure required columns exist
    rows = df_rows.copy()
    if "product_title" not in rows:
        rows["product_title"] = ""

    for c in _NUM_COLS:
        if c not in rows:
            rows[c] = 0.0

    # Text -> TF-IDF
    X_text = tfidf.transform(rows["product_title"].astype(str))

    # Numeric -> log1p then StandardScaler
    num = rows[_NUM_COLS].copy()
    if "product_price" in num:
        num["product_price"] = np.log1p(num["product_price"].clip(lower=0))
    if "product_num_ratings" in num:
        num["product_num_ratings"] = np.log1p(num["product_num_ratings"].clip(lower=0))

    X_num = scaler.transform(num)

    # Combine (sparse text + dense numeric)
    return hstack([X_text, X_num]).tocsr()


# ---------- Public API ----------
def recommend(asin: str, k: int = DEFAULT_K, same_country: bool = False) -> List[Dict[str, Any]]:
    """
    Return up to k similar products for a given ASIN.
    If same_country=True, only return neighbors from the same country as the seed item.
    """
    st = _ensure_loaded()
    lk = st.lookup

    mask = lk["asin"].astype(str) == str(asin)
    if not mask.any():
        return []  # ASIN not in index

    idx = int(lk.index[mask][0])
    seed_row = lk.iloc[[idx]].copy()
    seed_country = seed_row["country"].iloc[0] if "country" in seed_row.columns else None

    Xq = _vectorize_rows(seed_row, st.tfidf, st.scaler)

    # +1 because the first neighbor will be the item itself
    dists, inds = st.knn.kneighbors(Xq, n_neighbors=min(k + 1, len(lk)))
    cand_idxs = [i for i in inds[0].tolist() if i != idx]

    # Optional same-country filter
    if same_country and "country" in lk.columns and seed_country is not None:
        cand_idxs = [i for i in cand_idxs if lk.iloc[i]["country"] == seed_country]

    # Truncate to k after filtering
    cand_idxs = cand_idxs[:k]
    cand_dists = []
    # distances array corresponds to the original order; skip self and align
    for i, d in zip(inds[0].tolist(), dists[0].tolist()):
        if i != idx and i in cand_idxs:
            cand_dists.append(d)

    recs = lk.iloc[cand_idxs].copy()
    # similarity = 1 - cosine_distance
    # (cosine distance ∈ [0, 2], but in practice with TF-IDF it's [0, 1])
    # Align lengths defensively:
    sim = [1.0 - float(d) for d in cand_dists]
    # If lengths mismatch due to filtering order, recompute per-row (safe but a tad slower)
    if len(sim) != len(recs):
        # Recompute one-by-one to be safe
        sim = []
        for i in cand_idxs:
            Xi = _vectorize_rows(lk.iloc[[i]], st.tfidf, st.scaler)
            d, _ = st.knn.kneighbors(Xi, n_neighbors=1)
            sim.append(1.0 - float(d[0][0]))
    recs = recs.assign(similarity=sim)

    # Final shape / keys
    cols = [
        "asin",
        "product_title",
        "product_price",
        "product_star_rating",
        "product_num_ratings",
        "country",
        "product_url",
        "rank",
        "page",
        "similarity",
    ]
    cols = [c for c in cols if c in recs.columns]  # keep only available
    return recs[cols].to_dict(orient="records")


def recommend_adhoc(
    product_title: str,
    product_price: float | None = None,
    product_star_rating: float | None = None,
    product_num_ratings: float | None = None,
    country: str | None = None,
    k: int = DEFAULT_K,
) -> List[Dict[str, Any]]:
    """
    Recommend similar products for an item that is NOT in the index.
    Useful for 'cold-start' queries from a form.
    """
    st = _ensure_loaded()
    payload = {
        "product_title": product_title,
        "product_price": product_price or 0.0,
        "product_star_rating": product_star_rating or 0.0,
        "product_num_ratings": product_num_ratings or 0.0,
        "country": country or "",
    }
    df_row = pd.DataFrame([payload])
    Xq = _vectorize_rows(df_row, st.tfidf, st.scaler)
    dists, inds = st.knn.kneighbors(Xq, n_neighbors=min(k, len(st.lookup)))
    recs = st.lookup.iloc[inds[0].tolist()].copy()
    recs["similarity"] = [1.0 - float(d) for d in dists[0].tolist()]

    cols = [
        "asin",
        "product_title",
        "product_price",
        "product_star_rating",
        "product_num_ratings",
        "country",
        "product_url",
        "rank",
        "page",
        "similarity",
    ]
    cols = [c for c in cols if c in recs.columns]
    return recs[cols].to_dict(orient="records")


# ---------- CLI demo ----------
if __name__ == "__main__":
    # Quick manual test:
    import argparse

    parser = argparse.ArgumentParser(description="KNN Similarity Recommender (local)")
    parser.add_argument("--asin", type=str, help="ASIN to query (must exist in lookup.csv)")
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--same_country", action="store_true")
    parser.add_argument("--title", type=str, help="Ad-hoc title (if ASIN not provided)")
    parser.add_argument("--price", type=float, default=None)
    parser.add_argument("--rating", type=float, default=None)
    parser.add_argument("--reviews", type=float, default=None)
    parser.add_argument("--country", type=str, default=None)
    args = parser.parse_args()

    if args.asin:
        out = recommend(args.asin, k=args.k, same_country=args.same_country)
    else:
        if not args.title:
            raise SystemExit("Provide --asin OR --title for ad-hoc mode.")
        out = recommend_adhoc(
            product_title=args.title,
            product_price=args.price,
            product_star_rating=args.rating,
            product_num_ratings=args.reviews,
            country=args.country,
            k=args.k,
        )

    import json

    print(json.dumps(out, ensure_ascii=False, indent=2))
