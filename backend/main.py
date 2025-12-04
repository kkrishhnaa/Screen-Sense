from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional
import pandas as pd
import os
from utils import RecommendationEngine

app = FastAPI(title="Screen Time Advisor API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load engine
engine = RecommendationEngine(csv_path=os.getenv("DATA_CSV", "data.csv"))

class RecommendRequest(BaseModel):
    age: int
    gender: str
    primary_device: str
    educational_hours: float
    recreational_hours: float
    health_impacts: Optional[str] = None
    urban_or_rural: str

    @validator("age")
    def validate_age(cls, v):
        if not 8 <= v <= 18:
            raise ValueError("Age must be between 8 and 18")
        return v

    @validator("educational_hours", "recreational_hours")
    def validate_hours(cls, v):
        if v < 0:
            raise ValueError("Hours must be non-negative")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        if v.lower() not in ["male", "female", "other"]:
            raise ValueError("Gender must be Male, Female, or Other")
        return v

    @validator("primary_device")
    def validate_device(cls, v):
        if v.lower() not in ["smartphone", "laptop", "tv", "tablet"]:
            raise ValueError("Primary device must be one of: Smartphone, Laptop, TV, Tablet")
        return v

    @validator("urban_or_rural")
    def validate_location(cls, v):
        if v.lower() not in ["urban", "rural"]:
            raise ValueError("Location must be Urban or Rural")
        return v

class FeedbackRequest(BaseModel):
    name: Optional[str] = None
    rating: int
    comments: str

    @validator("rating")
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be 1-5")
        return v

@app.post("/api/recommend")
async def recommend(req: RecommendRequest):
    try:
        total_hours = req.educational_hours + req.recreational_hours
        result = engine.generate_insights(req.dict(), total_hours)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    try:
        feedback_data = {
            "name": req.name,
            "rating": req.rating,
            "comments": req.comments,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        file_path = "feedback.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = pd.read_json(f).to_dict("records")
        else:
            data = []
        data.append(feedback_data)
        with open(file_path, "w") as f:
            pd.DataFrame(data).to_json(f, orient="records", indent=2)
        return {"message": "Feedback submitted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store feedback")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)