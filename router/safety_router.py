"""
Safety Router for Moondream-based scenario detection
FastAPI router for handling safety scenario requests
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import time
import uuid
from datetime import datetime

from controllers.safety_controller import SafetyController
from config import SUPPORTED_SCENARIOS, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

# Initialize router
router = APIRouter(prefix="/api/safety", tags=["Safety Detection"])

# Initialize safety controller
safety_controller = SafetyController()

# Job tracking for async operations
safety_jobs = {}

class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@router.post("/analyze")
async def analyze_safety_scenario(
    camera_id: str = Form(..., description="Camera identifier"),
    timestamp: Optional[str] = Form(None, description="Timestamp of the event"),
    image: Optional[UploadFile] = File(None, description="Optional image file for validation")
):
    """
    Analyze safety scenarios using true positive detection workflow
    
    Args:
        camera_id: Camera identifier
        timestamp: Optional timestamp filter
        image: Optional image file for validation
        
    Returns:
        True positive detection results with violation status and recommendations
    """
    try:
        # Validate camera_id
        if not camera_id:
            raise HTTPException(status_code=400, detail="Camera ID is required")
        
        # Validate file if provided
        if image and image.filename:
            # Check file extension
            file_ext = "." + image.filename.split(".")[-1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file_ext}. Allowed types: {ALLOWED_EXTENSIONS}"
                )
            
            # Check file size
            image.file.seek(0, 2)  # Seek to end
            file_size = image.file.tell()
            image.file.seek(0)  # Reset to beginning
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large: {file_size} bytes. Maximum size: {MAX_FILE_SIZE} bytes"
                )
        
        # Process the safety event using true positive detection
        result = safety_controller.process_safety_event(
            camera_id=camera_id,
            timestamp=timestamp,
            image=image
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze/async")
async def analyze_safety_scenario_async(
    camera_id: str = Form(..., description="Camera identifier"),
    timestamp: Optional[str] = Form(None, description="Timestamp of the event"),
    image: Optional[UploadFile] = File(None, description="Optional image file for validation")
):
    """
    Analyze safety scenarios asynchronously using true positive detection
    
    Returns:
        Job ID for tracking the analysis progress
    """
    try:
        # Validate camera_id
        if not camera_id:
            raise HTTPException(status_code=400, detail="Camera ID is required")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job entry
        safety_jobs[job_id] = {
            "id": job_id,
            "camera_id": camera_id,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": JobStatus.PENDING,
            "create_time": datetime.now().isoformat(),
            "start_time": None,
            "end_time": None,
            "result": None,
            "error": None
        }
        
        # Start background processing
        import threading
        thread = threading.Thread(
            target=_process_safety_event_async,
            args=(job_id, camera_id, timestamp, image)
        )
        thread.daemon = True
        thread.start()
        
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "message": "True positive detection started"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of an async safety analysis job
    
    Args:
        job_id: The job ID returned from async analysis
        
    Returns:
        Job status and results if completed
    """
    if job_id not in safety_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JSONResponse(content=safety_jobs[job_id])


@router.get("/scenarios")
async def get_supported_scenarios():
    """
    Get list of supported safety scenarios
    
    Returns:
        List of supported scenarios with descriptions
    """
    from prompts.scenario_prompts import get_scenario_description
    
    scenarios = []
    for scenario in SUPPORTED_SCENARIOS:
        scenarios.append({
            "name": scenario,
            "description": get_scenario_description(scenario),
            "display_name": scenario.replace("_", " ").title()
        })
    
    return JSONResponse(content={
        "success": True,
        "scenarios": scenarios,
        "total_count": len(scenarios)
    })


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        System health status
    """
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supported_scenarios": len(SUPPORTED_SCENARIOS),
        "model_loaded": True
    })


def _process_safety_event_async(job_id: str, camera_id: str, timestamp: str = None, image: UploadFile = None):
    """
    Process safety event asynchronously using true positive detection
    
    Args:
        job_id: Job identifier
        camera_id: Camera identifier
        timestamp: Event timestamp
        image: Optional image file
    """
    try:
        # Update job status
        safety_jobs[job_id]["status"] = JobStatus.PROCESSING
        safety_jobs[job_id]["start_time"] = datetime.now().isoformat()
        
        # Process the safety event using true positive detection
        result = safety_controller.process_safety_event(
            camera_id=camera_id,
            timestamp=timestamp,
            image=image
        )
        
        # Update job with results
        safety_jobs[job_id]["status"] = JobStatus.COMPLETED
        safety_jobs[job_id]["end_time"] = datetime.now().isoformat()
        safety_jobs[job_id]["result"] = result
        
    except Exception as e:
        # Update job with error
        safety_jobs[job_id]["status"] = JobStatus.FAILED
        safety_jobs[job_id]["end_time"] = datetime.now().isoformat()
        safety_jobs[job_id]["error"] = str(e)
