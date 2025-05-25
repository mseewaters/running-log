# src/runs/app.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from datetime import date
import uuid

print("Starting app.py module...")  # Debug

# Import your existing models and DAL (works in both Lambda and test environments)
try:
    # Try absolute imports first (works in Lambda)
    print("Trying absolute imports...")
    from models.run import Run
    from dal.run_dal import save_run, get_runs_by_user

    print("Absolute imports successful!")
except ImportError as e:
    # Fall back to relative imports (works in tests)
    print(f"Absolute imports failed: {e}")
    print("Trying relative imports...")
    from .models.run import Run
    from .dal.run_dal import save_run, get_runs_by_user

    print("Relative imports successful!")

app = FastAPI(title="Running Log API", version="1.0.0")
print("FastAPI app created!")

# Temporary hardcoded user_id (will be replaced with auth later)
TEMP_USER_ID = "user-123"


# Pydantic models for API
class RunRequest(BaseModel):
    date: str = Field(..., description="Run date in YYYY-MM-DD format")
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    duration: str = Field(..., description="Duration in HH:MM:SS format")
    notes: Optional[str] = Field("", description="Optional notes about the run")


class RunResponse(BaseModel):
    run_id: str
    date: str
    distance_km: float
    duration: str
    pace: str
    notes: str


def run_to_response(run: Run) -> RunResponse:
    """Convert Run model to API response"""
    return RunResponse(
        run_id=run.run_id,
        date=run.date.isoformat(),
        distance_km=float(run.distance_km),
        duration=run.duration_formatted,
        pace=run.pace_per_km_formatted,
        notes=run.notes,
    )


@app.get("/")
def health_check():
    """Health check endpoint"""
    print("Health check called")  # Debug
    return {"status": "healthy", "service": "running-log-api"}


@app.get("/health")  # Add this as backup
def health_check_alt():
    return {"status": "healthy", "service": "running-log-api"}


@app.post("/runs", status_code=201, response_model=RunResponse)
def create_run(run_request: RunRequest):
    """Create a new run entry"""
    try:
        # Create Run model from request (using Decimal for distance_km)
        from decimal import Decimal

        run = Run(
            user_id=TEMP_USER_ID,
            date=date.fromisoformat(run_request.date),
            distance_km=Decimal(str(run_request.distance_km)),
            duration=run_request.duration,
            notes=run_request.notes or "",  # Convert None to empty string
        )

        # Save to database
        save_run(run)

        # Return response
        return run_to_response(run)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # Temporarily comment out generic exception handling to see the real error
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/runs", response_model=List[RunResponse])
def get_runs():
    """Get all runs for the current user"""
    try:
        print("GET /runs called")  # Debug
        # Get runs from database
        runs = get_runs_by_user(TEMP_USER_ID)
        print(f"Retrieved {len(runs)} runs from database")  # Debug

        # Convert to response format and return directly as list
        result = [run_to_response(run) for run in runs]
        print(f"Returning {len(result)} formatted runs")  # Debug
        return result

    except Exception as e:
        print(f"Error in get_runs: {e}")  # Debug
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Lambda handler for AWS
def lambda_handler(event, context):
    """AWS Lambda handler"""
    print(f"Received event: {event}")  # Debug logging
    print(f"Path from API Gateway: {event.get('path', 'NO PATH')}")  # Add this line
    print(f"Raw path: {event.get('rawPath', 'NO RAW PATH')}")  # Add this line
    try:
        from mangum import Mangum

        handler = Mangum(app, api_gateway_base_path="/Prod")
        return handler(event, context)
    except Exception as e:
        print(f"Handler error: {e}")
        return {"statusCode": 500, "body": f"Handler error: {str(e)}"}
