# Moondream Safety Detection System

A scenario-based safety detection system using the Moondream model for industrial safety monitoring.

## Overview

This system adapts the VISIONAI-VIT architecture to use the Moondream model with scenario-specific prompts for detecting various safety violations in industrial environments.

## Supported Scenarios

- **Smoke Detection**: Detects smoke, steam, or smoke-like substances
- **Fire Detection**: Identifies fire, flames, or burning materials  
- **Fall Detection**: Detects if a person has fallen or is in distress
- **Debris Detection**: Identifies debris, obstacles, or hazardous materials
- **Missing Fire Extinguisher**: Checks if fire extinguisher is present in designated location
- **Unattended Object**: Detects unattended objects or suspicious items

## System Architecture

### Phase 1: Event Reception and Vision Analysis
1. **Edge System Detection** → Captures image and metadata
2. **FastAPI Router** → Validates request and routes to controller
3. **Scenario Identification** → Maps to appropriate scenario type
4. **Moondream Vision Analysis** → Analyzes image with scenario-specific prompt

### Phase 2: Text Validation and Veto Mechanism
5. **Text Validation Prompt** → Generates binary decision prompt
6. **Moondream Text Model** → Validates the vision analysis
7. **Veto Mechanism** → Confirms or rejects the initial detection

### Phase 3: Decision and Action
8. **Decision Logic** → Determines if violation occurred
9. **Alert Generation** → Sends high-priority alerts for violations
10. **Logging & Storage** → Records event with metadata

## Installation

### Prerequisites

- Python 3.8+
- Moondream Docker server running on port 2020
- 4GB+ RAM

### Setup

```bash
# Clone the repository
git clone https://github.com/saigiridhar04/New_Project.git
cd New_Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Moondream Docker Server Setup

Before running the safety detection system, you need to have the Moondream Docker server running:

```bash
# Start your Moondream Docker container on port 2020
# (This should already be set up based on your existing implementation)
```

### Configuration

Update `config.py` with your API settings:

```python
# Model Configuration
MOONDREAM_API_URL = "http://localhost:2020"  # Your Moondream Docker server URL

# Storage Configuration
IMAGES_DIR = "data/images"
VIDEO_DIR = "data/videos"
LOGS_DIR = "data/logs"
```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start at `http://localhost:8000` with API documentation available at `http://localhost:8000/docs`.

### API Endpoints

#### Analyze Safety Scenario
```bash
POST /api/safety/analyze
```

**Parameters:**
- `scenario`: Safety scenario type (required)
- `image`: Image file (required)
- `camera_id`: Camera identifier (optional)
- `timestamp`: Event timestamp (optional)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/safety/analyze" \
  -F "scenario=smoke_detection" \
  -F "image=@test_image.jpg" \
  -F "camera_id=camera_001"
```

#### Async Analysis
```bash
POST /api/safety/analyze/async
```

Returns a job ID for tracking progress.

#### Check Job Status
```bash
GET /api/safety/status/{job_id}
```

#### Get Supported Scenarios
```bash
GET /api/safety/scenarios
```

### Testing

Test the complete workflow:

```bash
python test_complete_workflow.py
```

## Project Structure

```
New_Project/
├── edge_moondream_detector.py    # Edge PC component
├── cloud_storage.py              # Cloud integration
├── true_positive_detector.py     # True positive detection
├── controllers/
│   └── safety_controller.py      # Safety controller
├── router/
│   └── safety_router.py          # FastAPI routes
├── src/moondream/
│   └── inference.py              # Moondream API client
├── prompts/
│   └── scenario_prompts.py       # Scenario prompts
├── config.py                     # Configuration
├── server.py                     # FastAPI server
├── test_complete_workflow.py    # Complete workflow test
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## Key Features

### Scenario-Based Processing
- **Camera-specific** → **Scenario-specific** prompts
- Dynamic prompt selection based on detected scenario
- Specialized prompts for each safety scenario

### Two-Phase Validation
1. **Vision Analysis**: Moondream analyzes the image
2. **Text Validation**: Veto mechanism confirms the detection

### Comprehensive Logging
- Event tracking with metadata
- Performance monitoring
- Alert generation for violations

### Async Processing
- Background job processing
- Job status tracking
- Scalable architecture

## Example Workflow

### Smoke Detection Example

1. **Edge System** → Detects potential smoke → Sends image to `/api/safety/analyze`
2. **FastAPI** → Routes to SafetyController with `scenario=smoke_detection`
3. **Vision Analysis** → Moondream: "Do you see any smoke or smoke-like substances?"
4. **Response** → "Yes, there is visible white smoke coming from the machinery"
5. **Text Validation** → "Based on 'visible white smoke', answer yes/no: Is there smoke detected?"
6. **Decision** → "yes" → Violation confirmed
7. **Alert** → High-priority alert sent to safety team
8. **Logging** → Event recorded as True Positive

## Configuration Options

### Environment Variables

```bash
export MOONDREAM_MODEL_PATH="/path/to/model"
export MOONDREAM_EXECUTION_PROVIDER="cuda"
export HOST="0.0.0.0"
export PORT="8000"
export MAX_FILE_SIZE="52428800"  # 50MB
```

### Model Settings

- **Model Path**: Path to Moondream model files
- **Execution Provider**: `cuda`, `cpu`, or `dml`
- **Max File Size**: Maximum upload size (default: 50MB)
- **Supported Extensions**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.mp4`, `.avi`, `.mov`

## Performance Considerations

- **GPU Memory**: Ensure sufficient VRAM for Moondream model
- **Batch Processing**: Use async endpoints for multiple requests
- **Caching**: Consider implementing model caching for production
- **Monitoring**: Track processing times and resource usage

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Check model path configuration
   - Verify GPU memory availability
   - Ensure proper CUDA installation

2. **Memory Issues**
   - Reduce batch size
   - Use CPU execution provider
   - Implement model cleanup

3. **API Errors**
   - Check file size limits
   - Verify supported file formats
   - Ensure proper scenario names

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test suite for examples