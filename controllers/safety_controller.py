"""
Safety Controller for True Positive Detection
Handles cloud integration and true positive detection workflow
"""

import time
import os
from typing import Dict, Any, List, Optional
from PIL import Image as PILImage
from io import BytesIO
from fastapi import UploadFile

from true_positive_detector import TruePositiveDetector
from cloud_storage import CloudStorage, LocalCloudStorage
from config import SUPPORTED_SCENARIOS, MOONDREAM_API_URL


class SafetyController:
    def __init__(self, api_url: str = None, use_local_storage: bool = True):
        """
        Initialize the Safety Controller for True Positive Detection
        
        Args:
            api_url: URL of the Moondream API server
            use_local_storage: Whether to use local storage for testing
        """
        self.true_positive_detector = TruePositiveDetector(api_url or MOONDREAM_API_URL, use_local_storage)
        self.supported_scenarios = SUPPORTED_SCENARIOS
        
    def process_safety_event(self, 
                            camera_id: str, 
                            timestamp: str = None,
                            image: UploadFile = None) -> Dict[str, Any]:
        """
        Process safety event using true positive detection workflow
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            image: Optional image file for validation
            
        Returns:
            Dictionary containing true positive detection results
        """
        print(f"🎯 Processing Safety Event")
        print(f"📷 Camera: {camera_id}")
        print(f"⏰ Timestamp: {timestamp or 'Latest'}")
        print("=" * 60)
        
        try:
            # Run true positive detection
            result = self.true_positive_detector.detect_true_positives(camera_id, timestamp, image)
            
            if not result["success"]:
                return result
            
            # Generate alert if violations detected
            if result["true_positives"]:
                alert = self.true_positive_detector.generate_alert(result)
                result["alert"] = alert
                
                # Add recommended actions
                result["recommended_actions"] = self.true_positive_detector.get_recommended_actions(result["true_positives"])
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Safety event processing failed: {str(e)}",
                "camera_id": camera_id,
                "timestamp": timestamp
            }
    
    def get_edge_results(self, camera_id: str, timestamp: str = None) -> Dict[str, Any]:
        """
        Get edge results from cloud storage
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            Dictionary containing edge results
        """
        return self.true_positive_detector.cloud_storage.retrieve_edge_results(camera_id, timestamp)
    
    def get_detected_scenarios(self, camera_id: str, timestamp: str = None) -> List[str]:
        """
        Get list of detected scenarios from edge results
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            List of detected scenario names
        """
        return self.true_positive_detector.cloud_storage.get_detected_scenarios(camera_id, timestamp)
    
    def get_supported_scenarios(self) -> List[str]:
        """
        Get list of supported scenarios
        
        Returns:
            List of supported scenario names
        """
        return self.supported_scenarios
    
    def cleanup(self):
        """
        Clean up resources
        """
        if hasattr(self, 'true_positive_detector'):
            # Cleanup is handled by the true positive detector
            pass


# Example usage
if __name__ == "__main__":
    controller = SafetyController()
    
    # Test with a sample camera
    print("Supported scenarios:", controller.get_supported_scenarios())
    
    # Test edge results retrieval
    edge_results = controller.get_edge_results("CAMERA_001")
    if edge_results:
        print("Edge results found:", edge_results.get("detected_scenarios", []))
    else:
        print("No edge results found")
    
    # Cleanup
    controller.cleanup()
