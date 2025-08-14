from fastapi import FastAPI, Request
from typing import List, Dict, Any
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

app = FastAPI(title="Clinical Research Service")

class ClinicalResearch:
    def __init__(self):
        self.model = LogisticRegression()

    def select_cohort(self, data: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(data)
        query = ' & '.join([f'({k} == {repr(v)})' for k, v in criteria.items()])
        selected = df.query(query) if query else df
        return selected.to_dict(orient="records")

    def predict_outcome(self, data: List[Dict[str, Any]], features: List[str], target: str) -> Dict[str, Any]:
        df = pd.DataFrame(data)
        X = df[features]
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        return {"accuracy": acc, "predictions": y_pred.tolist()}

    def statistical_analysis(self, data: List[Dict[str, Any]], column: str) -> Dict[str, float]:
        df = pd.DataFrame(data)
        stats = {
            "mean": float(df[column].mean()),
            "std": float(df[column].std()),
            "min": float(df[column].min()),
            "max": float(df[column].max()),
            "count": int(df[column].count())
        }
        return stats

research_engine = ClinicalResearch()

@app.post("/research/cohort")
async def select_cohort(request: Request):
    data = await request.json()
    cohort = research_engine.select_cohort(data["data"], data.get("criteria", {}))
    return {"cohort": cohort}

@app.post("/research/predict")
async def predict_outcome(request: Request):
    data = await request.json()
    result = research_engine.predict_outcome(data["data"], data["features"], data["target"])
    return result

@app.post("/research/stats")
async def statistical_analysis(request: Request):
    data = await request.json()
    stats = research_engine.statistical_analysis(data["data"], data["column"])
    return {"stats": stats} 