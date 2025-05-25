from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Running Tracker - Targets API")
lambda_handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Running Tracker Targets API"}
