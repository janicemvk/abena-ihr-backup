from fastapi import FastAPI
from src.clinical_outcomes.data_collection import outcome_router

app = FastAPI(
    title="Abena Clinical Outcomes API",
    version="1.0.0"
)

# Include the outcome router
app.include_router(outcome_router, prefix="/api/v1/outcomes", tags=["clinical_outcomes"])

@app.get("/")
def root():
    return {"message": "Abena Clinical Outcomes API is running."} 