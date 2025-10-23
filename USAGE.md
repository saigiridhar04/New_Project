# Moondream Safety Detection System - Usage Guide

## 🎯 **Your Complete Workflow**

```
📹 CCTV Video → Edge PC (ALL scenarios) → Cloud → FastAPI (validation) → True Positive Detection
```

## 📁 **Essential Files Only**

### **Core Workflow Files:**
- `edge_moondream_detector.py` - Edge PC component
- `cloud_storage.py` - Cloud integration  
- `true_positive_detector.py` - True positive detection
- `controllers/safety_controller.py` - Safety controller
- `router/safety_router.py` - FastAPI endpoints
- `server.py` - FastAPI server

### **Supporting Files:**
- `src/moondream/inference.py` - Moondream API client
- `prompts/scenario_prompts.py` - Scenario prompts
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `test_complete_workflow.py` - Testing

## 🚀 **How to Use**

### **1. Edge PC (Run on Edge Device)**
```bash
# Install dependencies
pip install -r requirements.txt

# Run edge detection
python edge_moondream_detector.py \
  --video /path/to/cctv_video.mp4 \
  --camera_id CAMERA_001 \
  --moondream_url http://localhost:2020 \
  --cloud_url https://your-cloud-api.com/edge-results
```

### **2. FastAPI Server (Run on Cloud/Server)**
```bash
# Start FastAPI server
python server.py

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### **3. Test Complete Workflow**
```bash
# Test the entire pipeline
python test_complete_workflow.py
```

## 🔄 **Complete Workflow Example**

### **Step 1: Edge PC Detection**
```
📹 CCTV Video → Extract frames 3,4,5 → Run ALL scenarios:
├── Smoke Detection: "Yes, visible smoke detected"
├── Fire Detection: "No, no fire visible"  
├── Fall Detection: "No, no person fallen"
├── Debris Detection: "No, no debris visible"
├── Missing Fire Extinguisher: "No, extinguisher present"
└── Unattended Object: "No, no unattended objects"

📤 Send to Cloud: {
    "camera_id": "CAMERA_001",
    "edge_results": {
        "smoke_detection": {"detected": true, "response": "Yes, visible smoke detected"},
        "fire_detection": {"detected": false, "response": "No, no fire visible"},
        // ... other scenarios
    }
}
```

### **Step 2: FastAPI True Positive Detection**
```
📥 Pull from Cloud → Get detected scenarios: ["smoke_detection"]
🔍 Run second-level validation:
├── Prompt: "Based on 'Yes, visible smoke detected', answer yes/no: Is there smoke detected?"
├── Response: "yes"
└── Result: TRUE POSITIVE ✅

📤 Final Response: {
    "true_positives": ["smoke_detection"],
    "violations": ["smoke_detection"],
    "action_required": true
}
```

## 🎯 **Key Features**

✅ **Edge PC Multi-Scenario Detection** - Runs ALL 6 scenarios simultaneously  
✅ **Cloud Storage Integration** - Stores and retrieves edge results  
✅ **True Positive Detection** - Compares edge vs FastAPI validation  
✅ **Two-Level Validation** - Edge detection + FastAPI validation  
✅ **Complete Workflow Testing** - End-to-end testing suite  
✅ **Alert Generation** - High-priority alerts for true positives  
✅ **Recommended Actions** - Scenario-specific safety actions  

## 📊 **Supported Scenarios**

- **smoke_detection** - Detects smoke, steam, or smoke-like substances
- **fire_detection** - Identifies fire, flames, or burning materials
- **fall_detection** - Detects if a person has fallen or is in distress
- **debris_detection** - Identifies debris, obstacles, or hazardous materials
- **missing_fire_extinguisher** - Checks if fire extinguisher is present
- **unattended_object** - Detects unattended objects or suspicious items

## 🔧 **Configuration**

Update `config.py` with your settings:
```python
# Moondream API URL
MOONDREAM_API_URL = "http://localhost:2020"

# Server settings
HOST = "0.0.0.0"
PORT = 8000

# Storage settings
IMAGES_DIR = "data/images"
VIDEO_DIR = "data/videos"
LOGS_DIR = "data/logs"
```

## 🧪 **Testing**

```bash
# Test complete workflow
python test_complete_workflow.py

# Test individual components
python edge_moondream_detector.py --help
python true_positive_detector.py --help
```

Your project is now clean and focused on the essential workflow! 🎉
