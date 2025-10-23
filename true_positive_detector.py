"""
True Positive Detection Logic
Compares edge results with FastAPI validation to determine true positives
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.moondream.inference import MoondreamInference
from prompts.scenario_prompts import get_text_validation_prompt
from cloud_storage import CloudStorage, LocalCloudStorage


class TruePositiveDetector:
    def __init__(self, api_url: str = "http://localhost:2020", use_local_storage: bool = True):
        """
        Initialize True Positive Detector
        
        Args:
            api_url: URL of the Moondream API server
            use_local_storage: Whether to use local storage for testing
        """
        self.moondream_model = MoondreamInference(api_url)
        
        # Initialize cloud storage
        if use_local_storage:
            self.cloud_storage = LocalCloudStorage()
        else:
            self.cloud_storage = CloudStorage()
        
        print("✅ True Positive Detector initialized successfully")
    
    def validate_scenario(self, scenario: str, edge_response: str, image_data: Any = None) -> Dict[str, Any]:
        """
        Validate a single scenario using second-level validation
        
        Args:
            scenario: Safety scenario type
            edge_response: Response from edge analysis
            image_data: Optional image data for validation
            
        Returns:
            Dictionary containing validation results
        """
        print(f"🔍 Validating scenario: {scenario}")
        
        try:
            # Get validation prompt
            validation_prompt = get_text_validation_prompt(scenario, edge_response)
            
            # Run second-level validation
            if image_data:
                # Use image for validation
                validation_result = self.moondream_model.run_fast_inference(validation_prompt, image_data)
            else:
                # Use text-only validation (create dummy image)
                from PIL import Image
                dummy_image = Image.new('RGB', (1, 1), color='white')
                validation_result = self.moondream_model.run_inference(validation_prompt, [dummy_image])
            
            if "error" in validation_result:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "scenario": scenario
                }
            
            # Parse validation response
            validation_response = validation_result["response"].strip().lower()
            is_valid = self._parse_validation_response(validation_response)
            
            result = {
                "success": True,
                "scenario": scenario,
                "edge_response": edge_response,
                "validation_prompt": validation_prompt,
                "validation_response": validation_response,
                "is_valid": is_valid,
                "confidence": self._calculate_confidence(edge_response, validation_response),
                "processing_time": validation_result["processing_time"]
            }
            
            print(f"   ✅ {scenario}: {'VALID' if is_valid else 'INVALID'}")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scenario": scenario
            }
    
    def _parse_validation_response(self, response: str) -> bool:
        """
        Parse validation response to determine if scenario is valid
        
        Args:
            response: The validation response from the model
            
        Returns:
            True if scenario is valid, False otherwise
        """
        response_lower = response.lower().strip()
        
        # Positive indicators for valid scenario
        positive_indicators = ["yes", "true", "valid", "detected", "present", "found"]
        negative_indicators = ["no", "false", "invalid", "not detected", "absent", "not found"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        if positive_count > negative_count:
            return True
        elif negative_count > positive_count:
            return False
        else:
            # Default to valid if unclear
            return True
    
    def _calculate_confidence(self, edge_response: str, validation_response: str) -> float:
        """
        Calculate confidence score based on responses
        
        Args:
            edge_response: Response from edge analysis
            validation_response: Response from validation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence on response clarity
        edge_confidence = 0.8 if len(edge_response.strip()) > 10 else 0.5
        validation_confidence = 0.9 if validation_response.strip() in ["yes", "no", "true", "false"] else 0.6
        
        return (edge_confidence + validation_confidence) / 2
    
    def detect_true_positives(self, camera_id: str, timestamp: str = None, image_data: Any = None) -> Dict[str, Any]:
        """
        Detect true positives by comparing edge results with FastAPI validation
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            image_data: Optional image data for validation
            
        Returns:
            Dictionary containing true positive detection results
        """
        print(f"🎯 Starting True Positive Detection")
        print(f"📷 Camera: {camera_id}")
        print(f"⏰ Timestamp: {timestamp or 'Latest'}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Retrieve edge results from cloud
            edge_data = self.cloud_storage.retrieve_edge_results(camera_id, timestamp)
            
            if not edge_data:
                return {
                    "success": False,
                    "error": "No edge results found",
                    "camera_id": camera_id,
                    "timestamp": timestamp
                }
            
            # Get detected scenarios from edge
            detected_scenarios = edge_data.get("detected_scenarios", [])
            
            if not detected_scenarios:
                return {
                    "success": True,
                    "camera_id": camera_id,
                    "timestamp": edge_data["timestamp"],
                    "true_positives": [],
                    "message": "No scenarios detected at edge level",
                    "edge_results": edge_data["edge_results"]
                }
            
            print(f"🔍 Detected scenarios from edge: {detected_scenarios}")
            
            # Run second-level validation for each detected scenario
            validation_results = {}
            for scenario in detected_scenarios:
                edge_response = edge_data["edge_results"][scenario]["response"]
                validation_result = self.validate_scenario(scenario, edge_response, image_data)
                validation_results[scenario] = validation_result
            
            # Determine true positives
            true_positives = []
            false_positives = []
            
            for scenario, result in validation_results.items():
                if result["success"] and result["is_valid"]:
                    true_positives.append(scenario)
                else:
                    false_positives.append(scenario)
            
            # Calculate processing time
            total_processing_time = time.time() - start_time
            
            # Prepare final results
            final_results = {
                "success": True,
                "camera_id": camera_id,
                "timestamp": edge_data["timestamp"],
                "video_path": edge_data["video_path"],
                "edge_results": edge_data["edge_results"],
                "validation_results": validation_results,
                "true_positives": true_positives,
                "false_positives": false_positives,
                "processing_times": {
                    "edge_processing": edge_data["processing_time"],
                    "validation_processing": total_processing_time,
                    "total": edge_data["processing_time"] + total_processing_time
                },
                "final_decision": {
                    "violations_detected": len(true_positives) > 0,
                    "violation_count": len(true_positives),
                    "violation_types": true_positives,
                    "confidence": self._calculate_overall_confidence(validation_results)
                }
            }
            
            # Update cloud storage with validation results
            self.cloud_storage.update_validation_status(camera_id, edge_data["timestamp"], validation_results)
            
            # Print summary
            print(f"\n📊 TRUE POSITIVE DETECTION SUMMARY")
            print("=" * 60)
            print(f"✅ True Positives: {len(true_positives)}")
            if true_positives:
                print(f"🚨 Violations: {', '.join(true_positives)}")
            print(f"❌ False Positives: {len(false_positives)}")
            if false_positives:
                print(f"⚠️  False Alarms: {', '.join(false_positives)}")
            print(f"📈 Overall Confidence: {final_results['final_decision']['confidence']:.2f}")
            print(f"⏱️  Total Processing Time: {final_results['processing_times']['total']:.2f} seconds")
            print("=" * 60)
            
            return final_results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"True positive detection failed: {str(e)}",
                "camera_id": camera_id,
                "timestamp": timestamp
            }
    
    def _calculate_overall_confidence(self, validation_results: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score
        
        Args:
            validation_results: Dictionary of validation results
            
        Returns:
            Overall confidence score
        """
        if not validation_results:
            return 0.0
        
        valid_results = [result for result in validation_results.values() if result["success"]]
        if not valid_results:
            return 0.0
        
        confidence_scores = [result["confidence"] for result in valid_results]
        return sum(confidence_scores) / len(confidence_scores)
    
    def get_recommended_actions(self, true_positives: List[str]) -> Dict[str, str]:
        """
        Get recommended actions for true positive violations
        
        Args:
            true_positives: List of true positive scenario names
            
        Returns:
            Dictionary mapping scenarios to recommended actions
        """
        action_map = {
            "smoke_detection": "Immediately investigate source of smoke and evacuate if necessary",
            "fire_detection": "Activate fire alarm, call emergency services, and evacuate area",
            "fall_detection": "Provide immediate medical assistance and secure the area",
            "debris_detection": "Clear debris and investigate source of obstruction",
            "missing_fire_extinguisher": "Replace missing fire extinguisher immediately",
            "unattended_object": "Investigate unattended object and remove if safe to do so"
        }
        
        return {scenario: action_map.get(scenario, "Investigate and take appropriate safety measures") 
                for scenario in true_positives}
    
    def generate_alert(self, true_positive_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate alert for true positive violations
        
        Args:
            true_positive_results: Results from true positive detection
            
        Returns:
            Dictionary containing alert information
        """
        if not true_positive_results["success"]:
            return {"alert_generated": False, "reason": "Detection failed"}
        
        true_positives = true_positive_results["true_positives"]
        
        if not true_positives:
            return {"alert_generated": False, "reason": "No violations detected"}
        
        # Generate alert
        alert = {
            "alert_generated": True,
            "priority": "high" if len(true_positives) > 0 else "low",
            "camera_id": true_positive_results["camera_id"],
            "timestamp": true_positive_results["timestamp"],
            "violations": true_positives,
            "violation_count": len(true_positives),
            "recommended_actions": self.get_recommended_actions(true_positives),
            "confidence": true_positive_results["final_decision"]["confidence"],
            "message": f"Safety violations detected: {', '.join(true_positives)}"
        }
        
        return alert


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="True Positive Detector")
    parser.add_argument("-c", "--camera_id", type=str, required=True, help="Camera identifier")
    parser.add_argument("-t", "--timestamp", type=str, help="Timestamp filter")
    parser.add_argument("-u", "--api_url", type=str, default="http://localhost:2020", help="Moondream API URL")
    parser.add_argument("--local", action="store_true", help="Use local storage")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file path")
    
    args = parser.parse_args()
    
    try:
        # Initialize detector
        detector = TruePositiveDetector(args.api_url, args.local)
        
        # Run true positive detection
        result = detector.detect_true_positives(args.camera_id, args.timestamp)
        
        # Generate alert if violations detected
        if result["success"] and result["true_positives"]:
            alert = detector.generate_alert(result)
            result["alert"] = alert
        
        # Save results if output path provided
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Results saved to: {args.output}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
