"""
Moondream Safety Detection Server
FastAPI server for scenario-based safety detection using Moondream model
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

import uvicorn
from config import PORT, HOST, IMAGES_DIR, VIDEO_DIR, LOGS_DIR

# Import routers
from router.safety_router import router as safety_router

# Create FastAPI app
app = FastAPI(
    title="Moondream Safety Detection API", 
    description="API for scenario-based safety detection using Moondream model",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")
app.mount("/logs", StaticFiles(directory=LOGS_DIR), name="logs")

# Include routers
app.include_router(safety_router)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Moondream Safety Detection API",
        "version": "2.0.0",
        "description": "Scenario-based safety detection using Moondream model",
        "docs_url": "/docs",
        "supported_scenarios": [
            "smoke_detection",
            "fire_detection", 
            "fall_detection",
            "debris_detection",
            "missing_fire_extinguisher",
            "unattended_object"
        ]
    }

# Custom OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title="Moondream Safety Detection API",
        version="2.0.0",
        description="API for scenario-based safety detection using Moondream model",
        routes=app.routes,
    )

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Moondream Safety Detection API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


def main():    
    """
    Main function to run the server
    """
    print(f"Starting Moondream Safety Detection Server...")
    print(f"Server: http://{HOST}:{PORT}")
    print(f"API Documentation: http://{HOST}:{PORT}/docs")
    print(f"Supported Scenarios: smoke_detection, fire_detection, fall_detection, debris_detection, missing_fire_extinguisher, unattended_object")
    
    uvicorn.run(app, host=str(HOST), port=int(PORT))


if __name__ == "__main__":
    main()
