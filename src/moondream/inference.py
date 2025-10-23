"""
Moondream Model Inference Module
Uses local Docker API server for Moondream model inference
Adapted from VISIONAI-VIT system for scenario-specific safety detection
"""

import os
import time
import base64
import requests
from typing import List, Optional, Dict, Any
from PIL import Image as PILImage
from io import BytesIO
from fastapi import UploadFile


class MoondreamInference:
    def __init__(self, api_url: str = "http://localhost:2020"):
        """
        Initialize the Moondream API client
        
        Args:
            api_url: URL of the local Moondream Docker server
        """
        print("Initializing Moondream API client...")
        
        self.api_url = api_url
        self.query_endpoint = f"{api_url}/v1/query"
        
        # Test API connectivity
        self.api_working = self.test_api_connection()
        
        if self.api_working:
            print("✅ Moondream API connection successful")
        else:
            print("❌ Moondream API connection failed")
            raise ConnectionError("Cannot connect to Moondream API server")
    
    def test_api_connection(self) -> bool:
        """Test API connectivity with a simple request"""
        try:
            # Create a simple test image
            test_image = PILImage.new('RGB', (1, 1), color='white')
            with BytesIO() as buffer:
                test_image.save(buffer, format='JPEG')
                test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "image_url": f"data:image/jpeg;base64,{test_base64}",
                "question": "What do you see? Answer Yes or No."
            }
            
            response = requests.post(self.query_endpoint, headers=headers, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ API connection successful ({self.query_endpoint})")
                return True
            else:
                print(f"❌ API connection failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API test failed. Is Docker running on port 2020? Error: {e}")
            return False
    
    def encode_image(self, image: PILImage.Image) -> str:
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
                    return {"error": "Rate limit hit (try reducing workers)"}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2.0)
                else:
                    return {"error": str(e)}
    
    def run_inference(self, prompt: str, images: List[PILImage.Image]) -> Dict[str, Any]:
        """
        Run inference with the Moondream API
        
        Args:
            prompt: Text prompt for the model
            images: List of PIL Images
            
        Returns:
            Dictionary containing the response and metadata
        """
        start_time = time.time()
        
        try:
            if not images:
                return {"error": "No images provided"}
            
            # Use the first image
            image = images[0]
            image_base64 = self.encode_image(image)
            
            if image_base64 is None:
                return {"error": "Failed to encode image"}
            
            # Call API
            result = self.call_moondream_api(image_base64, prompt)
            
            if "error" in result:
                return {"error": result["error"]}
            
            # Extract response
            response_text = result.get("answer", "").strip()
            total_time = time.time() - start_time
            
            return {
                "response": response_text,
                "processing_time": total_time,
                "data": {
                    "frame_response": response_text,
                    "frame_time": round(total_time * 1000, 2),
                    "frame_number": len(images)
                }
            }
            
        except Exception as e:
            print(f"Error during Moondream inference: {str(e)}")
            return {"error": str(e)}
    
    def run_fast_inference(self, prompt: str, image: UploadFile = None) -> Dict[str, Any]:
        """
        Run fast inference with image from memory
        
        Args:
            prompt: Text prompt for the model
            image: UploadFile object containing the image
            
        Returns:
            Dictionary containing the response and metadata
        """
        start_time = time.time()
        
        try:
            if not image:
                return {"error": "No image provided"}
            
            # Read the content from UploadFile
            image_content = image.file.read()
            
            # Convert to PIL Image
            pil_image = PILImage.open(BytesIO(image_content))
            
            # Encode image
            image_base64 = self.encode_image(pil_image)
            
            if image_base64 is None:
                return {"error": "Failed to encode image"}
            
            # Call API
            result = self.call_moondream_api(image_base64, prompt)
            
            if "error" in result:
                return {"error": result["error"]}
            
            # Extract response
            response_text = result.get("answer", "").strip()
            total_time = time.time() - start_time
            
            return {
                "response": response_text,
                "processing_time": total_time,
                "data": {
                    "frame_response": response_text,
                    "frame_time": round(total_time * 1000, 2),
                    "frame_number": 1
                }
            }
                
        except Exception as e:
            print(f"Error during fast inference: {str(e)}")
            return {"error": str(e)}
    
    def cleanup(self):
        """
        Clean up resources (no model cleanup needed for API client)
        """
        print("Moondream API client cleanup completed")


# Example usage if run directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--api_url", type=str, default="http://localhost:2020", 
        help="Moondream API server URL"
    )
    parser.add_argument(
        "-i", "--image_path", type=str, help="Path to image"
    )
    parser.add_argument(
        "-p", "--prompt", type=str, default="What do you see?", help="Text prompt"
    )
    
    args = parser.parse_args()
    
    try:
        moondream = MoondreamInference(args.api_url)
        
        if args.image_path and os.path.exists(args.image_path):
            image = PILImage.open(args.image_path)
            result = moondream.run_inference(args.prompt, [image])
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print("\nResponse:")
                print(result["response"])
                print(f"\nProcessing time: {result['processing_time']:.2f} seconds")
        else:
            print("Please provide a valid image path")
    except Exception as e:
        print(f"Error: {e}")
