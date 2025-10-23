"""
Scheduled Event Puller for FastAPI
Automatically pulls events from cloud storage every 5-10 minutes
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from threading import Thread
import schedule

from true_positive_detector import TruePositiveDetector
from cloud_storage import LocalCloudStorage, CloudStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventScheduler:
    def __init__(self, 
                 pull_interval_minutes: int = 5,
                 use_local_storage: bool = True,
                 moondream_api_url: str = "http://localhost:2020"):
        """
        Initialize Event Scheduler
        
        Args:
            pull_interval_minutes: How often to pull events (5 or 10 minutes)
            use_local_storage: Whether to use local storage for testing
            moondream_api_url: URL of Moondream API server
        """
        self.pull_interval = pull_interval_minutes
        self.use_local_storage = use_local_storage
        self.moondream_api_url = moondream_api_url
        
        # Initialize components
        self.true_positive_detector = TruePositiveDetector(
            api_url=moondream_api_url,
            use_local_storage=use_local_storage
        )
        
        if use_local_storage:
            self.cloud_storage = LocalCloudStorage()
        else:
            self.cloud_storage = CloudStorage()
        
        self.is_running = False
        self.scheduler_thread = None
        
        logger.info(f"🕐 Event Scheduler initialized")
        logger.info(f"⏰ Pull interval: {pull_interval_minutes} minutes")
        logger.info(f"💾 Storage type: {'Local' if use_local_storage else 'Cloud'}")
    
    def pull_events_from_cloud(self):
        """
        Pull events from cloud storage and process them
        """
        try:
            logger.info("🔄 Starting scheduled event pull from cloud storage...")
            
            # Get all cameras with recent events
            cameras = self.cloud_storage.list_cameras_with_events()
            
            if not cameras:
                logger.info("📭 No cameras with recent events found")
                return
            
            logger.info(f"📷 Found {len(cameras)} cameras with events")
            
            total_processed = 0
            total_true_positives = 0
            
            for camera_id in cameras:
                try:
                    logger.info(f"🔍 Processing camera: {camera_id}")
                    
                    # Run true positive detection
                    result = self.true_positive_detector.detect_true_positives(camera_id)
                    
                    if result.get("success", False):
                        true_positives = result.get("true_positives", [])
                        false_positives = result.get("false_positives", [])
                        confidence = result.get("confidence", 0)
                        
                        total_processed += 1
                        total_true_positives += len(true_positives)
                        
                        logger.info(f"✅ Camera {camera_id} processed:")
                        logger.info(f"   📊 True Positives: {len(true_positives)}")
                        logger.info(f"   📊 False Positives: {len(false_positives)}")
                        logger.info(f"   📈 Confidence: {confidence:.2f}")
                        
                        # Generate alerts for true positives
                        if true_positives:
                            self._generate_alerts(camera_id, true_positives, confidence)
                    else:
                        logger.warning(f"❌ Failed to process camera {camera_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing camera {camera_id}: {str(e)}")
                    continue
            
            logger.info(f"🎯 Scheduled pull completed:")
            logger.info(f"   📊 Cameras processed: {total_processed}")
            logger.info(f"   🚨 True positives found: {total_true_positives}")
            
        except Exception as e:
            logger.error(f"❌ Error in scheduled event pull: {str(e)}")
    
    def _generate_alerts(self, camera_id: str, true_positives: List[str], confidence: float):
        """
        Generate alerts for true positive detections
        
        Args:
            camera_id: Camera identifier
            true_positives: List of true positive scenarios
            confidence: Overall confidence score
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for scenario in true_positives:
                alert = {
                    "camera_id": camera_id,
                    "scenario": scenario,
                    "confidence": confidence,
                    "timestamp": timestamp,
                    "priority": "HIGH" if confidence > 0.8 else "MEDIUM",
                    "action_required": True
                }
                
                # Log the alert
                logger.warning(f"🚨 ALERT: {scenario} detected on {camera_id}")
                logger.warning(f"   📊 Confidence: {confidence:.2f}")
                logger.warning(f"   ⏰ Time: {timestamp}")
                logger.warning(f"   🎯 Priority: {alert['priority']}")
                
                # Here you can add additional alert mechanisms:
                # - Send to external alert system
                # - Send email notifications
                # - Send to monitoring dashboard
                # - Store in alert database
                
        except Exception as e:
            logger.error(f"❌ Error generating alerts: {str(e)}")
    
    def start_scheduler(self):
        """
        Start the scheduled event pulling
        """
        if self.is_running:
            logger.warning("⚠️ Scheduler is already running")
            return
        
        logger.info(f"🚀 Starting event scheduler (every {self.pull_interval} minutes)")
        
        # Schedule the job
        schedule.every(self.pull_interval).minutes.do(self.pull_events_from_cloud)
        
        # Run initial pull
        logger.info("🔄 Running initial event pull...")
        self.pull_events_from_cloud()
        
        # Start scheduler in separate thread
        self.is_running = True
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Event scheduler started successfully")
    
    def stop_scheduler(self):
        """
        Stop the scheduled event pulling
        """
        if not self.is_running:
            logger.warning("⚠️ Scheduler is not running")
            return
        
        logger.info("🛑 Stopping event scheduler...")
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("✅ Event scheduler stopped")
    
    def _run_scheduler(self):
        """
        Run the scheduler loop
        """
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Wait 5 seconds before retrying
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get current scheduler status
        
        Returns:
            Dict with scheduler status information
        """
        return {
            "is_running": self.is_running,
            "pull_interval_minutes": self.pull_interval,
            "use_local_storage": self.use_local_storage,
            "moondream_api_url": self.moondream_api_url,
            "next_pull": "In progress" if self.is_running else "Not scheduled"
        }


def main():
    """
    Main function to run the scheduler standalone
    """
    print("🕐 Starting Event Scheduler")
    print("=" * 50)
    
    # Initialize scheduler (5 minutes interval)
    scheduler = EventScheduler(
        pull_interval_minutes=5,
        use_local_storage=True,
        moondream_api_url="http://localhost:2020"
    )
    
    try:
        # Start scheduler
        scheduler.start_scheduler()
        
        print("✅ Scheduler started successfully")
        print("📊 Status:", scheduler.get_scheduler_status())
        print("\n🔄 Scheduler is running... Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping scheduler...")
        scheduler.stop_scheduler()
        print("✅ Scheduler stopped")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        scheduler.stop_scheduler()


if __name__ == "__main__":
    main()
