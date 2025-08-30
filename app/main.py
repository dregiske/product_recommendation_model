from fastapi import FastAPI, HTTPException, Query
from app.recommender import recommend

app = FastAPI(title="Amazon KNN Recommender", version="0.1.0")

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/recommend")
def recommend_api(asin: str = Query(...), k: int = 5, same_country: bool = False):
    recs = recommend(asin, k=k, same_country=same_country)
    if not recs: raise HTTPException(status_code=404, detail="ASIN not found")
    return {"asin": asin, "k": k, "same_country": same_country, "recommendations": recs}
