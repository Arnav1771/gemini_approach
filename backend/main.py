import os
import io
import json
import hashlib
from typing import List, Dict, Optional
import google.generativeai as genai
import PIL.Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/graph_analysis")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY)

# --- Database Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GraphDataHistory(Base):
    __tablename__ = "graph_data_history"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    value = Column(Numeric, nullable=False)
    extracted_at = Column(DateTime, default=func.now())
    source_graph_hash = Column(String(64))

# Create tables
Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI(title="Graph Analysis AI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class InsightResponse(BaseModel):
    chart_type: str
    summary: str
    trends: List[str]
    anomalies: List[str]
    recommendations: List[str]
    extracted_data: List[Dict]

class ScreenCapRequest(BaseModel):
    image_data: str  # base64 encoded image

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Core Gemini Logic ---
async def analyze_graph_with_gemini(image: PIL.Image.Image) -> str:
    """
    Sends an image of a graph to Gemini and gets structured insights.
    This is the first pass analysis.
    """
    model = genai.GenerativeModel('gemini-pro-vision')

    # This prompt is engineered to get a structured JSON output.
    prompt = """
    You are an expert data analyst. Analyze the provided chart image.
    Respond in a valid JSON format with the following keys:
    - "chart_type": (e.g., "Line Chart", "Bar Chart", "Pie Chart")
    - "summary": A brief, one-sentence summary of the chart's main point.
    - "trends": A list of key trends or patterns observed.
    - "anomalies": A list of any outliers or unexpected data points.
    - "recommendations": A list of 2-3 actionable business recommendations based ONLY on the data in this chart.
    - "extracted_data": An array of JSON objects representing the data points. For example, [{"category": "Jan", "value": 150}, {"category": "Feb", "value": 170}].

    Here is the chart:
    """

    try:
        response = await model.generate_content_async([prompt, image])
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API call failed: {str(e)}")

def get_validated_insights(initial_insights: dict, db_session: Session) -> dict:
    """
    Validates and refines insights using historical data from the database.
    """
    extracted_data = initial_insights.get("extracted_data", [])
    if not extracted_data:
        return initial_insights  # Cannot validate without data

    # 1. Infer metric name from chart (simplified - could be more sophisticated)
    metric_name = "general_metric"  # This should be inferred from the chart title/labels
    categories = [item.get('category', '') for item in extracted_data if 'category' in item]
    
    if not categories:
        return initial_insights

    # 2. Query DB for relevant historical data
    historical_records = db_session.query(GraphDataHistory).filter(
        GraphDataHistory.metric_name == metric_name,
        GraphDataHistory.category.in_(categories)
    ).all()
    
    if not historical_records:
        # No historical data, store current data and return initial insights
        store_new_data_in_db(extracted_data, metric_name, db_session)
        return initial_insights
    
    historical_data_str = json.dumps(
        [{"category": r.category, "value": float(r.value)} for r in historical_records]
    )

    # 3. Construct the second, validation-focused prompt
    validation_model = genai.GenerativeModel('gemini-pro')  # Text-only is fine here
    validation_prompt = f"""
    An initial analysis of a new chart produced these insights:
    {json.dumps(initial_insights)}

    Here is the relevant historical data for the same metrics from our database:
    {historical_data_str}

    Your task is to act as a senior auditor.
    1. Cross-check the "trends" and "anomalies" from the initial analysis against the historical data.
    2. Refine, confirm, or challenge the "recommendations". A recommendation is only valid if supported by both the new chart and the historical context.
    3. Return a final, validated JSON object with the same structure as the initial analysis, but with the refined content.
    """
    
    try:
        validation_response = validation_model.generate_content(validation_prompt)
        final_insights = json.loads(validation_response.text)
        
        # Store new data in database
        store_new_data_in_db(extracted_data, metric_name, db_session)
        
        return final_insights
    except Exception as e:
        # If validation fails, return initial insights and log error
        print(f"Validation failed: {str(e)}")
        store_new_data_in_db(extracted_data, metric_name, db_session)
        return initial_insights

def store_new_data_in_db(extracted_data: List[Dict], metric_name: str, db_session: Session):
    """
    Stores new data points in the database.
    """
    for data_point in extracted_data:
        if 'category' in data_point and 'value' in data_point:
            db_record = GraphDataHistory(
                metric_name=metric_name,
                category=data_point['category'],
                value=float(data_point['value']),
                source_graph_hash=hashlib.sha256(str(data_point).encode()).hexdigest()[:64]
            )
            db_session.add(db_record)
    
    db_session.commit()

def calculate_image_hash(image_content: bytes) -> str:
    """Calculate SHA256 hash of image content."""
    return hashlib.sha256(image_content).hexdigest()

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Graph Analysis AI API", "version": "1.0.0"}

@app.post("/api/analyze/upload", response_model=InsightResponse)
async def analyze_uploaded_graph(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint to analyze a user-uploaded graph image.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    # Read and process image
    image_content = await file.read()
    image_hash = calculate_image_hash(image_content)
    
    try:
        image = PIL.Image.open(io.BytesIO(image_content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    # Get initial analysis from Gemini
    raw_insights_json_str = await analyze_graph_with_gemini(image)

    try:
        initial_insights = json.loads(raw_insights_json_str)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Gemini response: {str(e)}")
    
    # Validate and refine insights using historical data
    validated_insights = get_validated_insights(initial_insights, db)
    
    return InsightResponse(**validated_insights)

@app.post("/api/analyze/screencap", response_model=InsightResponse)
async def analyze_screen_capture(request: ScreenCapRequest, db: Session = Depends(get_db)):
    """
    Endpoint to analyze a screen capture of a graph.
    """
    try:
        # Decode base64 image
        import base64
        image_data = base64.b64decode(request.image_data.split(',')[1])  # Remove data:image/png;base64, prefix
        image = PIL.Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    # Get initial analysis from Gemini
    raw_insights_json_str = await analyze_graph_with_gemini(image)

    try:
        initial_insights = json.loads(raw_insights_json_str)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Gemini response: {str(e)}")
    
    # Validate and refine insights using historical data
    validated_insights = get_validated_insights(initial_insights, db)
    
    return InsightResponse(**validated_insights)

@app.get("/api/history")
async def get_historical_data(db: Session = Depends(get_db)):
    """
    Endpoint to retrieve historical data.
    """
    records = db.query(GraphDataHistory).order_by(GraphDataHistory.extracted_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "metric_name": r.metric_name,
            "category": r.category,
            "value": float(r.value),
            "extracted_at": r.extracted_at.isoformat()
        }
        for r in records
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
