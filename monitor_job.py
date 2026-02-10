"""
Periodic Job Monitor
Checks job status periodically and notifies when complete
"""

import sys
import io
import time
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from qiskit_ibm_runtime import QiskitRuntimeService

# Configuration
JOB_ID = 'd5skpr8husoc73epvu20'
CHECK_INTERVAL = 60  # Check every 60 seconds
MAX_CHECKS = 120  # Maximum number of checks (2 hours)

def check_job_status(service, job_id):
    """Check and display job status"""
    try:
        job = service.job(job_id)
        status = job.status()
        status_str = str(status) if not isinstance(status, str) else status
        status_upper = status_str.upper()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Status: {status_str}", end='', flush=True)
        
        # Get submission time
        try:
            creation_date = job.creation_date() if callable(job.creation_date) else job.creation_date
            if isinstance(creation_date, str):
                from dateutil import parser
                creation_date = parser.parse(creation_date)
            elapsed = datetime.now(creation_date.tzinfo) - creation_date if hasattr(creation_date, 'tzinfo') else datetime.now() - creation_date.replace(tzinfo=None)
            elapsed_min = int(elapsed.total_seconds() / 60)
            print(f" (Elapsed: {elapsed_min} minutes)", end='', flush=True)
        except:
            pass
        
        return status_upper, job
        
    except Exception as e:
        print(f"\n❌ Error checking job: {e}")
        return None, None

def get_results(job):
    """Retrieve and display results"""
    try:
        result = job.result()
        quasi_dist = result.quasi_dists[0]
        
        print("\n" + "="*70)
        print("🎉 JOB COMPLETED! RESULTS:")
        print("="*70)
        print(f"\n✅ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📊 Quasi-probability distribution:")
        print(quasi_dist)
        
        print("\n" + "="*70)
        print("🏆 TOP 5 MEASUREMENT OUTCOMES")
        print("="*70)
        sorted_outcomes = sorted(quasi_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (state, probability) in enumerate(sorted_outcomes, 1):
            binary = format(state, '04b')
            print(f"   {i}. |{binary}⟩: {probability:.4f} ({probability*100:.2f}%)")
        
        print("\n" + "="*70)
        print("📝 INTERPRETATION (ABENA Healthcare Model)")
        print("="*70)
        print("   Qubit 0: Conventional drug effectiveness")
        print("   Qubit 1: Herbal medicine compatibility")
        print("   Qubit 2: Lifestyle intervention impact")
        print("   Qubit 3: Patient genetic factors")
        print("\n   Each measurement outcome represents a treatment combination")
        print("   Higher probability = more likely optimal treatment path")
        print("="*70)
        
        return True
    except Exception as e:
        print(f"\n❌ Error retrieving results: {e}")
        return False

def main():
    print("="*70)
    print("🔍 ABENA IHR - Quantum Job Monitor")
    print("="*70)
    print(f"\n📋 Monitoring Job ID: {JOB_ID}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"🛑 Maximum checks: {MAX_CHECKS} ({MAX_CHECKS * CHECK_INTERVAL // 60} minutes)")
    print("\n" + "="*70)
    print("Starting monitoring... (Press Ctrl+C to stop)")
    print("="*70)
    
    try:
        service = QiskitRuntimeService(channel='ibm_quantum_platform')
        
        check_count = 0
        while check_count < MAX_CHECKS:
            check_count += 1
            status, job = check_job_status(service, JOB_ID)
            
            if status is None:
                print("\n⚠️  Could not check status. Retrying...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            if status == 'DONE':
                print("\n✅ Job completed!")
                if job:
                    get_results(job)
                break
            elif status == 'ERROR':
                print("\n❌ Job failed!")
                print("   Check the IBM Quantum dashboard for details")
                break
            elif status in ['QUEUED', 'RUNNING']:
                # Continue monitoring
                time.sleep(CHECK_INTERVAL)
            else:
                print(f"\n📊 Status: {status}")
                time.sleep(CHECK_INTERVAL)
        
        if check_count >= MAX_CHECKS:
            print(f"\n⏰ Maximum check limit reached ({MAX_CHECKS} checks)")
            print("   Job may still be processing. Check manually:")
            print(f"   python check_results.py")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        print(f"   Current status saved. Run 'python check_results.py' to check later")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()




