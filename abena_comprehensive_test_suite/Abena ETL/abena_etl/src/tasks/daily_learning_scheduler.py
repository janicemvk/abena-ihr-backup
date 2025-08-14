import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import threading
from dataclasses import dataclass

from src.integration.system_orchestrator import AbenaIntegratedSystem

@dataclass
class SchedulerConfig:
    """Configuration for the daily learning scheduler"""
    learning_time: str = "02:00"  # 2 AM daily
    timezone: str = "UTC"
    max_execution_time: int = 7200  # 2 hours max
    retry_attempts: int = 3
    retry_delay: int = 300  # 5 minutes
    notification_enabled: bool = True
    health_check_interval: int = 3600  # 1 hour

class DailyLearningScheduler:
    """Scheduler for automated daily learning tasks"""
    
    def __init__(self, config: SchedulerConfig = None):
        self.config = config or SchedulerConfig()
        self.logger = logging.getLogger(__name__)
        self.abena_system = AbenaIntegratedSystem()
        self.is_running = False
        self.current_execution = None
        self.last_execution_result = None
        self.scheduler_thread = None
        
    def start_scheduler(self):
        """Start the daily learning scheduler"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.logger.info(f"Starting daily learning scheduler for {self.config.learning_time}")
        
        # Schedule the daily learning task
        schedule.every().day.at(self.config.learning_time).do(self._schedule_daily_learning)
        
        # Schedule health checks
        schedule.every(self.config.health_check_interval).seconds.do(self._health_check)
        
        # Start scheduler in separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Daily learning scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the daily learning scheduler"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Daily learning scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _schedule_daily_learning(self):
        """Schedule daily learning execution"""
        if self.current_execution and not self.current_execution.done():
            self.logger.warning("Previous learning cycle still running, skipping this execution")
            return
        
        # Create new execution task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.current_execution = loop.create_task(self._execute_daily_learning_with_retry())
        
        try:
            # Run the learning cycle
            loop.run_until_complete(self.current_execution)
        except Exception as e:
            self.logger.error(f"Daily learning execution failed: {str(e)}")
        finally:
            loop.close()
    
    async def _execute_daily_learning_with_retry(self):
        """Execute daily learning with retry logic"""
        execution_start = datetime.now()
        
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                self.logger.info(f"Starting daily learning cycle (attempt {attempt}/{self.config.retry_attempts})")
                
                # Set execution timeout
                execution_result = await asyncio.wait_for(
                    self.abena_system.execute_daily_learning(),
                    timeout=self.config.max_execution_time
                )
                
                # Store successful result
                self.last_execution_result = {
                    'status': 'success',
                    'execution_time': execution_start.isoformat(),
                    'duration_seconds': (datetime.now() - execution_start).total_seconds(),
                    'attempt': attempt,
                    'result': execution_result
                }
                
                self.logger.info(f"Daily learning cycle completed successfully on attempt {attempt}")
                
                # Send success notification
                if self.config.notification_enabled:
                    await self._send_success_notification(self.last_execution_result)
                
                return execution_result
                
            except asyncio.TimeoutError:
                self.logger.error(f"Daily learning cycle timed out on attempt {attempt}")
                
                if attempt < self.config.retry_attempts:
                    self.logger.info(f"Retrying in {self.config.retry_delay} seconds...")
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    # Final failure
                    self.last_execution_result = {
                        'status': 'timeout',
                        'execution_time': execution_start.isoformat(),
                        'duration_seconds': (datetime.now() - execution_start).total_seconds(),
                        'attempts': self.config.retry_attempts,
                        'error': 'Execution timed out'
                    }
                    
                    if self.config.notification_enabled:
                        await self._send_failure_notification(self.last_execution_result)
            
            except Exception as e:
                self.logger.error(f"Daily learning cycle failed on attempt {attempt}: {str(e)}")
                
                if attempt < self.config.retry_attempts:
                    self.logger.info(f"Retrying in {self.config.retry_delay} seconds...")
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    # Final failure
                    self.last_execution_result = {
                        'status': 'error',
                        'execution_time': execution_start.isoformat(),
                        'duration_seconds': (datetime.now() - execution_start).total_seconds(),
                        'attempts': self.config.retry_attempts,
                        'error': str(e)
                    }
                    
                    if self.config.notification_enabled:
                        await self._send_failure_notification(self.last_execution_result)
        
        # If we get here, all attempts failed
        self.logger.error("All daily learning cycle attempts failed")
    
    def _health_check(self):
        """Perform health check on the learning system"""
        try:
            health_status = {
                'scheduler_running': self.is_running,
                'last_execution': self.last_execution_result,
                'system_status': self._check_system_health()
            }
            
            # Log health status
            if health_status['system_status']['healthy']:
                self.logger.debug("Daily learning scheduler health check: OK")
            else:
                self.logger.warning(f"Daily learning scheduler health issues: {health_status['system_status']['issues']}")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
    
    def _check_system_health(self) -> Dict:
        """Check overall system health"""
        issues = []
        
        # Check if learning system components are accessible
        try:
            if not hasattr(self.abena_system, 'continuous_learning'):
                issues.append("Continuous learning component not available")
            
            if not hasattr(self.abena_system, 'model_registry'):
                issues.append("Model registry not available")
                
            # Check if last execution was too long ago
            if self.last_execution_result:
                last_execution_time = datetime.fromisoformat(self.last_execution_result['execution_time'])
                if (datetime.now() - last_execution_time).days > 2:
                    issues.append("Last successful execution was more than 2 days ago")
            else:
                issues.append("No execution history available")
                
        except Exception as e:
            issues.append(f"System health check error: {str(e)}")
        
        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'checked_at': datetime.now().isoformat()
        }
    
    async def _send_success_notification(self, result: Dict):
        """Send success notification"""
        message = f"""
        Daily Learning Cycle Completed Successfully
        
        Execution Time: {result['execution_time']}
        Duration: {result['duration_seconds']:.0f} seconds
        Attempt: {result['attempt']}
        
        Components Executed: {len(result['result'].get('components_executed', []))}
        Insights Discovered: {len(result['result'].get('insights_discovered', []))}
        Models Updated: {len(result['result'].get('models_updated', []))}
        """
        
        self.logger.info("Daily learning success notification sent")
        # This would integrate with your notification system (email, Slack, etc.)
    
    async def _send_failure_notification(self, result: Dict):
        """Send failure notification"""
        message = f"""
        Daily Learning Cycle FAILED
        
        Status: {result['status']}
        Execution Time: {result['execution_time']}
        Duration: {result['duration_seconds']:.0f} seconds
        Attempts: {result['attempts']}
        Error: {result.get('error', 'Unknown error')}
        
        IMMEDIATE ATTENTION REQUIRED
        """
        
        self.logger.critical("Daily learning failure notification sent")
        # This would integrate with your alert system for immediate attention
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'config': {
                'learning_time': self.config.learning_time,
                'timezone': self.config.timezone,
                'max_execution_time': self.config.max_execution_time,
                'retry_attempts': self.config.retry_attempts
            },
            'last_execution_result': self.last_execution_result,
            'next_scheduled_run': self._get_next_run_time(),
            'current_execution_active': self.current_execution and not self.current_execution.done() if self.current_execution else False
        }
    
    def _get_next_run_time(self) -> str:
        """Get next scheduled run time"""
        try:
            next_job = schedule.next_run()
            return next_job.isoformat() if next_job else "Not scheduled"
        except:
            return "Unknown"
    
    def force_execution(self) -> bool:
        """Force immediate execution of daily learning"""
        if self.current_execution and not self.current_execution.done():
            self.logger.warning("Cannot force execution: another execution is already running")
            return False
        
        try:
            self.logger.info("Forcing immediate daily learning execution")
            self._schedule_daily_learning()
            return True
        except Exception as e:
            self.logger.error(f"Failed to force execution: {str(e)}")
            return False

# Standalone scheduler service
class DailyLearningService:
    """Standalone service for daily learning scheduling"""
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.scheduler = DailyLearningScheduler(self.config)
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> SchedulerConfig:
        """Load configuration from file or use defaults"""
        if config_file:
            # Load from file (JSON, YAML, etc.)
            # For now, use defaults
            pass
        
        return SchedulerConfig(
            learning_time="02:00",
            timezone="UTC", 
            max_execution_time=7200,
            retry_attempts=3,
            retry_delay=300,
            notification_enabled=True,
            health_check_interval=3600
        )
    
    def start(self):
        """Start the daily learning service"""
        self.logger.info("Starting Abena IHR Daily Learning Service")
        
        try:
            self.scheduler.start_scheduler()
            self.logger.info("Daily Learning Service started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Daily Learning Service: {str(e)}")
            return False
    
    def stop(self):
        """Stop the daily learning service"""
        self.logger.info("Stopping Abena IHR Daily Learning Service")
        
        try:
            self.scheduler.stop_scheduler()
            self.logger.info("Daily Learning Service stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping Daily Learning Service: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'service_name': 'Abena IHR Daily Learning Service',
            'service_status': 'running' if self.scheduler.is_running else 'stopped',
            'scheduler_status': self.scheduler.get_scheduler_status(),
            'timestamp': datetime.now().isoformat()
        }

# Command-line interface
def main():
    """Main entry point for the scheduler service"""
    import argparse
    import signal
    import sys
    
    parser = argparse.ArgumentParser(description='Abena IHR Daily Learning Scheduler')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--force-run', action='store_true', help='Force immediate execution')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create service
    service = DailyLearningService(args.config)
    
    if args.force_run:
        # Force immediate execution and exit
        print("Forcing immediate daily learning execution...")
        service.start()
        success = service.scheduler.force_execution()
        if success:
            print("Execution initiated successfully")
            sys.exit(0)
        else:
            print("Failed to initiate execution")
            sys.exit(1)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start service
    if service.start():
        print("Abena IHR Daily Learning Service is running...")
        print("Press Ctrl+C to stop")
        
        try:
            # Keep the service running
            while True:
                time.sleep(60)
                
                # Periodic status check
                status = service.get_status()
                if status['scheduler_status']['is_running']:
                    print(f"Service running - Next run: {status['scheduler_status']['next_scheduled_run']}")
                else:
                    print("WARNING: Scheduler is not running!")
                    
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        finally:
            service.stop()
    else:
        print("Failed to start Daily Learning Service")
        sys.exit(1)

if __name__ == "__main__":
    main()
