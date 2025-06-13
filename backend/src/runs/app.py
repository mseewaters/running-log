# src/runs/app.py
import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
    from auth.jwt_middleware import extract_user_id_from_token

    print("Absolute imports successful!")
except ImportError as e:
    # Fall back to relative imports (works in tests)
    print(f"Absolute imports failed: {e}")
    print("Trying relative imports...")
    from .models.run import Run
    from .dal.run_dal import save_run, get_runs_by_user
    from .auth.jwt_middleware import extract_user_id_from_token

    print("Relative imports successful!")

app = FastAPI(title="Running Log API", version="1.0.0")
print("FastAPI app created!")

# Add CORS middleware - put this right after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Security scheme
security = HTTPBearer()

# JWT secret from environment
JWT_SECRET = os.environ.get("JWT_SECRET", "default-secret")


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extract and validate user ID from JWT token

    Args:
        credentials: JWT token from Authorization header

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = credentials.credentials
    user_id = extract_user_id_from_token(token, JWT_SECRET)

    if not user_id:
        raise HTTPException(
            status_code=401, detail="Invalid or expired authorization token"
        )

    return user_id


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


# NEW: Authentication API models
class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str


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


# NEW: Authentication endpoints
@app.post("/auth/register", status_code=201, response_model=AuthResponse)
def register_user(register_request: RegisterRequest):
    """Register a new user and return JWT token"""
    try:
        # Import CognitoService (with proper import handling)
        try:
            from auth.cognito_service import CognitoService
        except ImportError:
            from .auth.cognito_service import CognitoService

        # Create CognitoService instance
        cognito_service = CognitoService()

        # Prepare user data
        user_data = {
            "email": register_request.email,
            "password": register_request.password,
            "first_name": register_request.first_name,
            "last_name": register_request.last_name,
        }

        # Register user (creates in both Cognito and DynamoDB)
        result = cognito_service.register_user(user_data)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Create JWT token for immediate login
        import jwt as jwt_lib
        from datetime import datetime, timedelta

        payload = {
            "sub": result["user_id"],  # Cognito user ID
            "email": register_request.email,
            "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour token
        }

        token = jwt_lib.encode(payload, JWT_SECRET, algorithm="HS256")

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user_id=result["user_id"],
            email=register_request.email,
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Registration error: {e}")  # Debug
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login", response_model=AuthResponse)
def login_user(login_request: LoginRequest):
    """Authenticate existing user and return JWT token"""
    try:
        # Import CognitoService (with proper import handling)
        try:
            from auth.cognito_service import CognitoService
        except ImportError:
            from .auth.cognito_service import CognitoService

        # Create CognitoService instance
        cognito_service = CognitoService()

        # Authenticate with Cognito
        result = cognito_service.authenticate_user(
            login_request.email, login_request.password
        )

        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])

        # Create JWT token for the session
        import jwt as jwt_lib
        from datetime import datetime, timedelta

        payload = {
            "sub": result["user_id"],  # Cognito user ID
            "email": result["email"],
            "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour token
        }

        token = jwt_lib.encode(payload, JWT_SECRET, algorithm="HS256")

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user_id=result["user_id"],
            email=result["email"],
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Login error: {e}")  # Debug
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.post("/runs", status_code=201, response_model=RunResponse)
def create_run(
    run_request: RunRequest, current_user_id: str = Depends(get_current_user_id)
):
    """Create a new run entry - NOW REQUIRES AUTHENTICATION"""
    try:
        # Create Run model from request (using real user ID from JWT)
        from decimal import Decimal

        run = Run(
            user_id=current_user_id,  # Use real user ID from JWT token
            date=date.fromisoformat(run_request.date),
            distance_km=Decimal(str(run_request.distance_km)),
            duration=run_request.duration,
            notes=run_request.notes or "",
        )

        # Save to database
        save_run(run)

        # Return response
        return run_to_response(run)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/runs", response_model=List[RunResponse])
def get_runs(current_user_id: str = Depends(get_current_user_id)):
    """Get all runs for the current user - NOW REQUIRES AUTHENTICATION"""
    try:
        print(f"GET /runs called for user: {current_user_id}")  # Debug
        # Get runs from database using real user ID
        runs = get_runs_by_user(current_user_id)
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

        # Configure Mangum to strip the API Gateway stage from the path
        handler = Mangum(app, api_gateway_base_path="/Prod")
        return handler(event, context)
    except Exception as e:
        print(f"Handler error: {e}")
        return {"statusCode": 500, "body": f"Handler error: {str(e)}"}
