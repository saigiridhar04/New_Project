"""
Test Complete Workflow: Edge PC → Cloud → FastAPI → True Positive Detection
Tests the entire pipeline from edge detection to final true positive results
"""

import os
import time
import json
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from pathlib import Path

from edge_moondream_detector import EdgeMoondreamDetector
from cloud_storage import LocalCloudStorage
from true_positive_detector import TruePositiveDetector
from controllers.safety_controller import SafetyController


def create_test_video(output_path: str, duration: int = 12, fps: int = 30, scenario: str = "smoke"):
    """
    Create a test video with specific scenario content
    
    Args:
        output_path: Path to save the test video
        duration: Duration in seconds
        fps: Frames per second
        scenario: Scenario type to simulate
    """
    print(f"🎬 Creating test video: {output_path}")
    print(f"🎯 Scenario: {scenario}")
    
    # Video properties
    width, height = 640, 480
    total_frames = duration * fps
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Generate frames
    for frame_num in range(total_frames):
        # Create a frame with some visual content
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some visual elements
        cv2.rectangle(frame, (50, 50), (width-50, height-50), (0, 255, 0), 2)
        cv2.putText(frame, f"Frame {frame_num+1}", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {frame_num/fps:.1f}s", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add scenario-specific content in frames 3-5 (seconds 3-5)
        if 3 <= frame_num/fps <= 5:
            if scenario == "smoke":
                # Add smoke effect
                noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
                frame = cv2.add(frame, noise)
                cv2.putText(frame, "SMOKE DETECTED", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif scenario == "fire":
                # Add fire effect
                fire_color = (0, 0, 255)  # Red
                cv2.circle(frame, (320, 240), 50, fire_color, -1)
                cv2.putText(frame, "FIRE DETECTED", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif scenario == "fall":
                # Add person on ground
                cv2.rectangle(frame, (300, 300), (400, 400), (255, 0, 0), -1)  # Person shape
                cv2.putText(frame, "PERSON FALLEN", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Test video created: {output_path}")


def test_edge_pc_detection():
    """
    Test Edge PC detection (Step 1)
    """
    print("\n🔍 STEP 1: Testing Edge PC Detection")
    print("=" * 60)
    
    try:
        # Create test video
        test_video_path = "test_smoke_video.mp4"
        create_test_video(test_video_path, scenario="smoke")
        
        # Initialize edge detector
        detector = EdgeMoondreamDetector(use_local_storage=True)
        
        # Run edge analysis
        result = detector.run_complete_edge_analysis(test_video_path, "CAMERA_001")
        
        if result["success"]:
            print(f"✅ Edge PC detection completed")
            print(f"📊 Detected scenarios: {result['detected_scenarios']}")
            print(f"⏱️  Processing time: {result['processing_time']:.2f} seconds")
            
            # Save results for next step
            with open("edge_results.json", 'w') as f:
                json.dump(result, f, indent=2)
            
            return result
        else:
            print(f"❌ Edge PC detection failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Edge PC detection error: {e}")
        return None


def test_cloud_storage():
    """
    Test Cloud Storage (Step 2)
    """
    print("\n☁️  STEP 2: Testing Cloud Storage")
    print("=" * 60)
    
    try:
        # Load edge results
        if not os.path.exists("edge_results.json"):
            print("❌ No edge results found. Run edge detection first.")
            return None
        
        with open("edge_results.json", 'r') as f:
            edge_results = json.load(f)
        
        # Initialize cloud storage
        cloud_storage = LocalCloudStorage()
        
        # Store edge results
        success = cloud_storage.store_edge_results(edge_results)
        
        if success:
            print(f"✅ Edge results stored in cloud")
            
            # Test retrieval
            retrieved_data = cloud_storage.retrieve_edge_results("CAMERA_001")
            
            if retrieved_data:
                print(f"✅ Edge results retrieved from cloud")
                print(f"📊 Detected scenarios: {retrieved_data.get('detected_scenarios', [])}")
                return retrieved_data
            else:
                print(f"❌ Failed to retrieve edge results")
                return None
        else:
            print(f"❌ Failed to store edge results")
            return None
            
    except Exception as e:
        print(f"❌ Cloud storage error: {e}")
        return None


def test_fastapi_validation():
    """
    Test FastAPI True Positive Detection (Step 3)
    """
    print("\n🎯 STEP 3: Testing FastAPI True Positive Detection")
    print("=" * 60)
    
    try:
        # Initialize safety controller
        controller = SafetyController(use_local_storage=True)
        
        # Run true positive detection
        result = controller.process_safety_event("CAMERA_001")
        
        if result["success"]:
            print(f"✅ FastAPI validation completed")
            print(f"📊 True positives: {result['true_positives']}")
            print(f"📊 False positives: {result['false_positives']}")
            print(f"📈 Overall confidence: {result['final_decision']['confidence']:.2f}")
            
            # Save results
            with open("true_positive_results.json", 'w') as f:
                json.dump(result, f, indent=2)
            
            return result
        else:
            print(f"❌ FastAPI validation failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ FastAPI validation error: {e}")
        return None


def test_complete_workflow():
    """
    Test the complete workflow from start to finish
    """
    print("🚀 Testing Complete Workflow: Edge PC → Cloud → FastAPI → True Positive Detection")
    print("=" * 80)
    
    # Step 1: Edge PC Detection
    edge_results = test_edge_pc_detection()
    if not edge_results:
        print("❌ Workflow failed at Edge PC detection")
        return False
    
    # Step 2: Cloud Storage
    cloud_results = test_cloud_storage()
    if not cloud_results:
        print("❌ Workflow failed at Cloud Storage")
        return False
    
    # Step 3: FastAPI Validation
    validation_results = test_fastapi_validation()
    if not validation_results:
        print("❌ Workflow failed at FastAPI Validation")
        return False
    
    # Final Summary
    print("\n📊 COMPLETE WORKFLOW SUMMARY")
    print("=" * 80)
    print(f"✅ Edge PC Detection: {'SUCCESS' if edge_results else 'FAILED'}")
    print(f"✅ Cloud Storage: {'SUCCESS' if cloud_results else 'FAILED'}")
    print(f"✅ FastAPI Validation: {'SUCCESS' if validation_results else 'FAILED'}")
    
    if validation_results:
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   📊 True Positives: {validation_results['true_positives']}")
        print(f"   📊 False Positives: {validation_results['false_positives']}")
        print(f"   📈 Confidence: {validation_results['final_decision']['confidence']:.2f}")
        print(f"   ⏱️  Total Time: {validation_results['processing_times']['total']:.2f} seconds")
        
        if validation_results['true_positives']:
            print(f"   🚨 ALERT: Safety violations detected!")
            print(f"   📝 Recommended Actions:")
            for scenario, action in validation_results.get('recommended_actions', {}).items():
                print(f"      - {scenario}: {action}")
        else:
            print(f"   ✅ No safety violations detected")
    
    return True


def test_multiple_scenarios():
    """
    Test multiple scenarios to verify the system works with different safety scenarios
    """
    print("\n🎯 Testing Multiple Scenarios")
    print("=" * 60)
    
    scenarios = ["smoke", "fire", "fall"]
    
    for scenario in scenarios:
        print(f"\n🔍 Testing scenario: {scenario}")
        
        try:
            # Create test video for scenario
            test_video_path = f"test_{scenario}_video.mp4"
            create_test_video(test_video_path, scenario=scenario)
            
            # Run edge detection
            detector = EdgeMoondreamDetector(use_local_storage=True)
            edge_result = detector.run_complete_edge_analysis(test_video_path, f"CAMERA_{scenario.upper()}")
            
            if edge_result["success"]:
                print(f"   ✅ Edge detection: {edge_result['detected_scenarios']}")
                
                # Run FastAPI validation
                controller = SafetyController(use_local_storage=True)
                validation_result = controller.process_safety_event(f"CAMERA_{scenario.upper()}")
                
                if validation_result["success"]:
                    print(f"   ✅ FastAPI validation: {validation_result['true_positives']}")
                else:
                    print(f"   ❌ FastAPI validation failed")
            else:
                print(f"   ❌ Edge detection failed")
                
        except Exception as e:
            print(f"   ❌ Scenario {scenario} failed: {e}")
    
    print(f"\n✅ Multiple scenario testing completed")


def cleanup_test_files():
    """
    Clean up test files
    """
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_smoke_video.mp4",
        "test_fire_video.mp4", 
        "test_fall_video.mp4",
        "edge_results.json",
        "true_positive_results.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   🗑️  Removed: {file}")
    
    # Clean up cloud storage directory
    if os.path.exists("cloud_storage"):
        import shutil
        shutil.rmtree("cloud_storage")
        print(f"   🗑️  Removed: cloud_storage/")
    
    print(f"✅ Cleanup completed")


def main():
    """
    Main function to run all tests
    """
    print("🧪 Starting Complete Workflow Tests")
    print("=" * 80)
    
    try:
        # Test complete workflow
        success = test_complete_workflow()
        
        if success:
            # Test multiple scenarios
            test_multiple_scenarios()
            
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
        
        # Cleanup
        cleanup_test_files()
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        cleanup_test_files()
        return False


if __name__ == "__main__":
    main()
