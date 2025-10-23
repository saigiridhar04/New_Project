"""
Cloud Storage Integration
Handles storage and retrieval of edge results from cloud
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os


class CloudStorage:
    def __init__(self, cloud_api_url: str = "https://your-cloud-api.com", api_key: str = None):
        """
        Initialize Cloud Storage
        
        Args:
            cloud_api_url: URL of the cloud API
            api_key: API key for authentication
        """
        self.cloud_api_url = cloud_api_url
        self.api_key = api_key
        self.edge_results_endpoint = f"{cloud_api_url}/edge-results"
        self.retrieve_endpoint = f"{cloud_api_url}/retrieve"
        
        print(f"☁️  Cloud Storage initialized")
        print(f"📡 Cloud API: {cloud_api_url}")
    
    def store_edge_results(self, edge_data: Dict[str, Any]) -> bool:
        """
        Store edge results in cloud
        
        Args:
            edge_data: Edge analysis results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"☁️  Storing edge results for camera {edge_data['camera_id']}")
            
            # Prepare payload
            payload = {
                "camera_id": edge_data["camera_id"],
                "timestamp": edge_data["timestamp"],
                "video_path": edge_data["video_path"],
                "edge_results": edge_data["edge_results"],
                "detected_scenarios": edge_data["detected_scenarios"],
                "processing_time": edge_data["processing_time"],
                "status": "pending_validation"
            }
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Send to cloud
            response = requests.post(
                self.edge_results_endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Edge results stored successfully")
                return True
            else:
                print(f"❌ Cloud storage failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Cloud storage error: {e}")
            return False
    
    def retrieve_edge_results(self, camera_id: str, timestamp: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve edge results from cloud
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            Edge results if found, None otherwise
        """
        try:
            print(f"☁️  Retrieving edge results for camera {camera_id}")
            
            # Prepare query parameters
            params = {"camera_id": camera_id}
            if timestamp:
                params["timestamp"] = timestamp
            
            # Prepare headers
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Retrieve from cloud
            response = requests.get(
                self.retrieve_endpoint,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Edge results retrieved successfully")
                    return data["data"]
                else:
                    print(f"❌ No edge results found")
                    return None
            else:
                print(f"❌ Cloud retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Cloud retrieval error: {e}")
            return None
    
    def get_detected_scenarios(self, camera_id: str, timestamp: str = None) -> List[str]:
        """
        Get list of detected scenarios from edge results
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            List of detected scenario names
        """
        edge_data = self.retrieve_edge_results(camera_id, timestamp)
        
        if edge_data and "edge_results" in edge_data:
            detected_scenarios = []
            for scenario, result in edge_data["edge_results"].items():
                if result.get("detected", False):
                    detected_scenarios.append(scenario)
            return detected_scenarios
        
        return []
    
    def update_validation_status(self, camera_id: str, timestamp: str, validation_results: Dict[str, Any]) -> bool:
        """
        Update cloud storage with validation results
        
        Args:
            camera_id: Camera identifier
            timestamp: Timestamp of the edge results
            validation_results: FastAPI validation results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"☁️  Updating validation status for camera {camera_id}")
            
            # Prepare payload
            payload = {
                "camera_id": camera_id,
                "timestamp": timestamp,
                "validation_results": validation_results,
                "status": "validation_complete",
                "updated_at": datetime.now().isoformat()
            }
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Update cloud
            response = requests.put(
                f"{self.cloud_api_url}/update-validation",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Validation status updated successfully")
                return True
            else:
                print(f"❌ Cloud update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Cloud update error: {e}")
            return False


class LocalCloudStorage:
    """
    Local cloud storage implementation for testing
    Uses local file system instead of actual cloud
    """
    
    def __init__(self, storage_dir: str = "cloud_storage"):
        """
        Initialize local cloud storage
        
        Args:
            storage_dir: Directory to store edge results
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        print(f"💾 Local Cloud Storage initialized")
        print(f"📁 Storage directory: {storage_dir}")
    
    def store_edge_results(self, edge_data: Dict[str, Any]) -> bool:
        """
        Store edge results locally
        
        Args:
            edge_data: Edge analysis results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"💾 Storing edge results locally for camera {edge_data['camera_id']}")
            
            # Create filename
            camera_id = edge_data["camera_id"]
            timestamp = edge_data["timestamp"].replace(":", "-").replace(".", "-")
            filename = f"{camera_id}_{timestamp}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Store data
            with open(filepath, 'w') as f:
                json.dump(edge_data, f, indent=2)
            
            print(f"✅ Edge results stored locally: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Local storage error: {e}")
            return False
    
    def retrieve_edge_results(self, camera_id: str, timestamp: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve edge results from local storage
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            Edge results if found, None otherwise
        """
        try:
            print(f"💾 Retrieving edge results locally for camera {camera_id}")
            
            # Find matching files
            matching_files = []
            for filename in os.listdir(self.storage_dir):
                if filename.startswith(camera_id) and filename.endswith('.json'):
                    if timestamp:
                        if timestamp.replace(":", "-").replace(".", "-") in filename:
                            matching_files.append(filename)
                    else:
                        matching_files.append(filename)
            
            if not matching_files:
                print(f"❌ No edge results found for camera {camera_id}")
                return None
            
            # Get the most recent file
            latest_file = max(matching_files, key=lambda x: os.path.getmtime(os.path.join(self.storage_dir, x)))
            filepath = os.path.join(self.storage_dir, latest_file)
            
            # Load data
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Edge results retrieved locally: {filepath}")
            return data
            
        except Exception as e:
            print(f"❌ Local retrieval error: {e}")
            return None
    
    def get_detected_scenarios(self, camera_id: str, timestamp: str = None) -> List[str]:
        """
        Get list of detected scenarios from local edge results
        
        Args:
            camera_id: Camera identifier
            timestamp: Optional timestamp filter
            
        Returns:
            List of detected scenario names
        """
        edge_data = self.retrieve_edge_results(camera_id, timestamp)
        
        if edge_data and "edge_results" in edge_data:
            detected_scenarios = []
            for scenario, result in edge_data["edge_results"].items():
                if result.get("detected", False):
                    detected_scenarios.append(scenario)
            return detected_scenarios
        
        return []
    
    def update_validation_status(self, camera_id: str, timestamp: str, validation_results: Dict[str, Any]) -> bool:
        """
        Update local storage with validation results
        
        Args:
            camera_id: Camera identifier
            timestamp: Timestamp of the edge results
            validation_results: FastAPI validation results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"💾 Updating validation status locally for camera {camera_id}")
            
            # Find the file
            matching_files = []
            for filename in os.listdir(self.storage_dir):
                if filename.startswith(camera_id) and filename.endswith('.json'):
                    if timestamp.replace(":", "-").replace(".", "-") in filename:
                        matching_files.append(filename)
            
            if not matching_files:
                print(f"❌ No edge results found to update")
                return False
            
            # Update the file
            filepath = os.path.join(self.storage_dir, matching_files[0])
            
            # Load existing data
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Add validation results
            data["validation_results"] = validation_results
            data["status"] = "validation_complete"
            data["updated_at"] = datetime.now().isoformat()
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Validation status updated locally: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Local update error: {e}")
            return False


def main():
    """Main function for testing cloud storage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud Storage Test")
    parser.add_argument("-c", "--camera_id", type=str, required=True, help="Camera identifier")
    parser.add_argument("-t", "--timestamp", type=str, help="Timestamp filter")
    parser.add_argument("--local", action="store_true", help="Use local storage")
    
    args = parser.parse_args()
    
    try:
        if args.local:
            # Test local storage
            storage = LocalCloudStorage()
        else:
            # Test cloud storage
            storage = CloudStorage()
        
        # Test retrieval
        edge_data = storage.retrieve_edge_results(args.camera_id, args.timestamp)
        
        if edge_data:
            print(f"✅ Retrieved edge data:")
            print(f"   Camera: {edge_data['camera_id']}")
            print(f"   Timestamp: {edge_data['timestamp']}")
            print(f"   Detected scenarios: {edge_data.get('detected_scenarios', [])}")
        else:
            print(f"❌ No edge data found")
        
        return edge_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
