"""
Edge PC Moondream Detector
Runs on Edge PC to detect ALL safety scenarios simultaneously
Extracts frames 3,4,5 from 12-second videos and runs all scenarios
"""

import os
import time
import base64
import requests
import cv2
import json
from datetime import datetime
from pathlib import Path
from PIL import Image
from io import BytesIO
from typing import Dict, Any, List, Optional

from prompts.scenario_prompts import get_scenario_prompt


class EdgeMoondreamDetector:
    def __init__(self, moondream_api_url: str = "http://localhost:2020", cloud_api_url: str = None):
        """
        Initialize Edge PC Moondream Detector
        
        Args:
            moondream_api_url: URL of local Moondream API server
            cloud_api_url: URL of cloud API for sending results
        """
        self.moondream_api_url = moondream_api_url
        self.cloud_api_url = cloud_api_url or "https://your-cloud-api.com/edge-results"
        self.query_endpoint = f"{moondream_api_url}/v1/query"
        
        # All safety scenarios to detect
        self.scenarios = [
            "smoke_detection",
            "fire_detection", 
            "fall_detection",
            "debris_detection",
            "missing_fire_extinguisher",
            "unattended_object"
        ]
        
        # Test Moondream API connection
        if not self._test_moondream_connection():
            raise ConnectionError("Cannot connect to Moondream API server")
        
        print("✅ Edge Moondream Detector initialized successfully")
        print(f"📡 Moondream API: {moondream_api_url}")
        print(f"☁️  Cloud API: {self.cloud_api_url}")
        print(f"🎯 Scenarios: {len(self.scenarios)} safety scenarios")
    
    def _test_moondream_connection(self) -> bool:
        """Test Moondream API connectivity"""
        try:
            # Create a simple test image
            test_image = Image.new('RGB', (1, 1), color='white')
            with BytesIO() as buffer:
                test_image.save(buffer, format='JPEG')
                test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "image_url": f"data:image/jpeg;base64,{test_base64}",
                "question": "What do you see? Answer Yes or No."
            }
            
            response = requests.post(self.query_endpoint, headers=headers, json=payload, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Moondream API connection failed: {e}")
            return False
    
    def extract_frames_from_video(self, video_path: str, target_frames: List[int] = [3, 4, 5]) -> List[Image.Image]:
        """
        Extract specific frames from 12-second video
        
        Args:
            video_path: Path to the video file
            target_frames: List of frame numbers to extract (1-indexed)
            
        Returns:
            List of PIL Images
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print(f"📹 Processing video: {os.path.basename(video_path)}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"   📊 Video info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s duration")
        print(f"   🎯 Extracting frames: {target_frames}")
        
        extracted_frames = []
        
        for frame_num in target_frames:
            # Calculate frame position (1-indexed to 0-indexed)
            frame_position = frame_num - 1
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            
            # Read frame
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                extracted_frames.append(pil_image)
                print(f"   ✅ Extracted frame {frame_num}")
            else:
                print(f"   ❌ Failed to extract frame {frame_num}")
        
        cap.release()
        return extracted_frames
    
    def encode_image(self, image: Image.Image) -> str:
        """Convert PIL image to base64 for API transmission"""
        try:
            with BytesIO() as buffer:
                image.save(buffer, format='JPEG')
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
    
    def call_moondream_api(self, image_base64: str, prompt: str) -> Dict:
        """Call Moondream API with error handling and retries"""
        headers = {"Content-Type": "application/json"}
        payload = {
            "image_url": f"data:image/jpeg;base64,{image_base64}",
            "question": prompt
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = 2.0 * (1.5 ** attempt)
                    time.sleep(delay)
                
                response = requests.post(self.query_endpoint, headers=headers, json=payload, timeout=15)
                
                if response.status_code == 429:
                    return {"error": "Rate limit hit"}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2.0)
                else:
                    return {"error": str(e)}
    
    def analyze_frames_for_scenario(self, frames: List[Image.Image], scenario: str) -> Dict[str, Any]:
        """
        Analyze frames for a specific scenario
        
        Args:
            frames: List of PIL Images
            scenario: Safety scenario type
            
        Returns:
            Dictionary containing analysis results
        """
        prompt = get_scenario_prompt(scenario, "vision")
        print(f"   🔍 Analyzing {scenario}...")
        
        frame_results = []
        detected_count = 0
        
        for i, frame in enumerate(frames):
            # Encode frame
            frame_base64 = self.encode_image(frame)
            if frame_base64 is None:
                frame_results.append({
                    "frame_number": i+1,
                    "success": False,
                    "error": "Failed to encode frame"
                })
                continue
            
            # Call API
            api_result = self.call_moondream_api(frame_base64, prompt)
            
            if "error" in api_result:
                frame_results.append({
                    "frame_number": i+1,
                    "success": False,
                    "error": api_result["error"]
                })
            else:
                response = api_result.get("answer", "").strip()
                is_detected = self._parse_detection(response)
                if is_detected:
                    detected_count += 1
                
                frame_results.append({
                    "frame_number": i+1,
                    "success": True,
                    "response": response,
                    "detected": is_detected
                })
        
        # Determine overall detection
        overall_detected = detected_count > 0
        overall_response = self._generate_overall_response(frame_results, scenario)
        
        return {
            "scenario": scenario,
            "detected": overall_detected,
            "response": overall_response,
            "frame_results": frame_results,
            "detected_frames": detected_count,
            "total_frames": len(frames)
        }
    
    def _parse_detection(self, response: str) -> bool:
        """
        Parse Moondream response to determine if detection occurred
        
        Args:
            response: Response from Moondream API
            
        Returns:
            True if detection occurred, False otherwise
        """
        response_lower = response.lower().strip()
        
        # Positive indicators
        positive_indicators = [
            "yes", "detected", "visible", "present", "found", "smoke", "fire", 
            "fallen", "debris", "missing", "unattended", "i see", "there is"
        ]
        
        # Negative indicators
        negative_indicators = [
            "no", "not detected", "not visible", "not present", "not found", 
            "absent", "clear", "nothing", "no smoke", "no fire"
        ]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        return positive_count > negative_count
    
    def _generate_overall_response(self, frame_results: List[Dict], scenario: str) -> str:
        """
        Generate overall response from frame results
        
        Args:
            frame_results: List of frame analysis results
            scenario: Safety scenario type
            
        Returns:
            Combined analysis string
        """
        successful_responses = [r["response"] for r in frame_results if r["success"]]
        
        if not successful_responses:
            return f"No analysis available for {scenario}"
        
        if len(successful_responses) == 1:
            return successful_responses[0]
        
        # Count detections
        detections = [r["response"] for r in frame_results if r["success"] and r["detected"]]
        
        if detections:
            return f"Analysis of {len(successful_responses)} frames indicates {scenario.replace('_', ' ')} detection. Details: {'; '.join(detections)}"
        else:
            return f"Analysis of {len(successful_responses)} frames indicates no {scenario.replace('_', ' ')} detection. Details: {'; '.join(successful_responses)}"
    
    def process_cctv_video(self, video_path: str, camera_id: str) -> Dict[str, Any]:
        """
        Process CCTV video for ALL safety scenarios
        
        Args:
            video_path: Path to the video file
            camera_id: Camera identifier
            
        Returns:
            Dictionary containing all scenario results
        """
        print(f"🎬 Starting Edge PC Analysis")
        print(f"📹 Video: {os.path.basename(video_path)}")
        print(f"📷 Camera: {camera_id}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Extract frames 3, 4, 5
            frames = self.extract_frames_from_video(video_path, [3, 4, 5])
            
            if not frames:
                return {
                    "success": False,
                    "error": "No frames extracted from video",
                    "camera_id": camera_id,
                    "video_path": video_path
                }
            
            # Run ALL scenarios
            print(f"\n🔍 Running {len(self.scenarios)} safety scenarios...")
            scenario_results = {}
            
            for scenario in self.scenarios:
                print(f"\n   🎯 Scenario: {scenario}")
                result = self.analyze_frames_for_scenario(frames, scenario)
                scenario_results[scenario] = {
                    "detected": result["detected"],
                    "response": result["response"],
                    "detected_frames": result["detected_frames"],
                    "total_frames": result["total_frames"]
                }
                
                status = "✅ DETECTED" if result["detected"] else "❌ NOT DETECTED"
                print(f"   {status}: {result['response'][:100]}...")
            
            # Generate summary
            detected_scenarios = [scenario for scenario, result in scenario_results.items() if result["detected"]]
            total_processing_time = time.time() - start_time
            
            edge_results = {
                "success": True,
                "camera_id": camera_id,
                "video_path": video_path,
                "timestamp": datetime.now().isoformat(),
                "processing_time": total_processing_time,
                "scenarios_analyzed": len(self.scenarios),
                "detected_scenarios": detected_scenarios,
                "edge_results": scenario_results
            }
            
            # Print summary
            print(f"\n📊 EDGE PC ANALYSIS SUMMARY")
            print("=" * 60)
            print(f"⏱️  Processing time: {total_processing_time:.2f} seconds")
            print(f"📈 Scenarios analyzed: {len(self.scenarios)}")
            print(f"✅ Detected scenarios: {len(detected_scenarios)}")
            if detected_scenarios:
                print(f"🚨 Violations: {', '.join(detected_scenarios)}")
            else:
                print("✅ No violations detected")
            print("=" * 60)
            
            return edge_results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "camera_id": camera_id,
                "video_path": video_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def send_to_cloud(self, edge_results: Dict[str, Any]) -> bool:
        """
        Send edge results to cloud storage
        
        Args:
            edge_results: Complete edge analysis results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"☁️  Sending results to cloud...")
            
            # Prepare cloud payload
            cloud_payload = {
                "camera_id": edge_results["camera_id"],
                "timestamp": edge_results["timestamp"],
                "video_path": edge_results["video_path"],
                "edge_results": edge_results["edge_results"],
                "detected_scenarios": edge_results["detected_scenarios"],
                "processing_time": edge_results["processing_time"]
            }
            
            # Send to cloud API
            response = requests.post(
                self.cloud_api_url,
                json=cloud_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Results sent to cloud successfully")
                return True
            else:
                print(f"❌ Cloud upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Cloud upload error: {e}")
            return False
    
    def run_complete_edge_analysis(self, video_path: str, camera_id: str) -> Dict[str, Any]:
        """
        Complete edge analysis pipeline
        
        Args:
            video_path: Path to the video file
            camera_id: Camera identifier
            
        Returns:
            Dictionary containing complete analysis results
        """
        # Process video
        edge_results = self.process_cctv_video(video_path, camera_id)
        
        if edge_results["success"]:
            # Send to cloud
            cloud_success = self.send_to_cloud(edge_results)
            edge_results["cloud_upload"] = cloud_success
        
        return edge_results


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Edge PC Moondream Detector")
    parser.add_argument("-v", "--video", type=str, required=True, help="Path to video file")
    parser.add_argument("-c", "--camera_id", type=str, required=True, help="Camera identifier")
    parser.add_argument("-m", "--moondream_url", type=str, default="http://localhost:2020", help="Moondream API URL")
    parser.add_argument("-u", "--cloud_url", type=str, help="Cloud API URL")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file path")
    
    args = parser.parse_args()
    
    try:
        # Initialize detector
        detector = EdgeMoondreamDetector(args.moondream_url, args.cloud_url)
        
        # Run complete analysis
        result = detector.run_complete_edge_analysis(args.video, args.camera_id)
        
        # Save results if output path provided
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Results saved to: {args.output}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
