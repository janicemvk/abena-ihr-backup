"""
Investigate Job Delay
Analyzes why a quantum job might be taking longer than expected
"""

import sys
import io
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from qiskit_ibm_runtime import QiskitRuntimeService

JOB_ID = 'd5skpr8husoc73epvu20'

def investigate_delay():
    """Investigate why the job is taking longer than expected"""
    print("="*70)
    print("🔍 ABENA IHR - Job Delay Investigation")
    print("="*70)
    
    try:
        service = QiskitRuntimeService(channel='ibm_quantum_platform')
        
        # Get job details
        print("\n📋 Analyzing job...")
        job = service.job(JOB_ID)
        status = job.status()
        status_str = str(status) if not isinstance(status, str) else status
        
        print(f"\n✅ Job found: {JOB_ID}")
        print(f"   Status: {status_str}")
        
        # Get submission time
        try:
            creation_date = job.creation_date() if callable(job.creation_date) else job.creation_date
            if isinstance(creation_date, str):
                from dateutil import parser
                creation_date = parser.parse(creation_date)
            
            now = datetime.now(creation_date.tzinfo) if hasattr(creation_date, 'tzinfo') else datetime.now()
            elapsed = now - creation_date if hasattr(creation_date, 'tzinfo') else datetime.now() - creation_date.replace(tzinfo=None)
            elapsed_min = int(elapsed.total_seconds() / 60)
            elapsed_sec = int(elapsed.total_seconds() % 60)
            
            print(f"   Submitted: {creation_date}")
            print(f"   Elapsed time: {elapsed_min} minutes {elapsed_sec} seconds")
        except Exception as e:
            print(f"   ⚠️  Could not get submission time: {e}")
        
        # Get backend info
        print("\n" + "="*70)
        print("🖥️  BACKEND ANALYSIS")
        print("="*70)
        
        backend = service.backend('ibm_fez')
        backend_status = backend.status()
        
        print(f"\nBackend: {backend.name}")
        print(f"   Total qubits: {backend.num_qubits}")
        print(f"   Status: {backend_status.status_msg}")
        print(f"   Pending jobs: {backend_status.pending_jobs}")
        
        # Check all backends for comparison
        print("\n" + "="*70)
        print("📊 COMPARATIVE ANALYSIS")
        print("="*70)
        
        all_backends = service.backends()
        operational_backends = []
        
        for b in all_backends:
            try:
                b_status = b.status()
                if b_status.status_msg.lower() == 'active':
                    operational_backends.append({
                        'name': b.name,
                        'pending': b_status.pending_jobs
                    })
            except:
                pass
        
        if operational_backends:
            operational_backends.sort(key=lambda x: x['pending'])
            print(f"\n{'Backend':<20} {'Pending Jobs':<15}")
            print("-" * 40)
            for b in operational_backends[:5]:  # Show top 5
                marker = " ← YOUR JOB" if b['name'] == 'ibm_fez' else ""
                print(f"{b['name']:<20} {b['pending']:<15}{marker}")
        
        # Analysis
        print("\n" + "="*70)
        print("🔬 DELAY ANALYSIS")
        print("="*70)
        
        if backend_status.pending_jobs > 10:
            print(f"\n⚠️  HIGH QUEUE DETECTED")
            print(f"   {backend_status.pending_jobs} jobs ahead in queue")
            print(f"   Estimated wait: ~{backend_status.pending_jobs * 3} minutes")
            print(f"   Reason: Backend is very busy")
        elif backend_status.pending_jobs > 5:
            print(f"\n⏳ MODERATE QUEUE")
            print(f"   {backend_status.pending_jobs} jobs ahead in queue")
            print(f"   Estimated wait: ~{backend_status.pending_jobs * 3} minutes")
            print(f"   Reason: Normal queue length")
        else:
            print(f"\n✅ SHORT QUEUE")
            print(f"   {backend_status.pending_jobs} jobs ahead")
            print(f"   Job should process soon")
        
        # Check if there are better alternatives
        if operational_backends:
            best_backend = operational_backends[0]
            if best_backend['name'] != 'ibm_fez' and best_backend['pending'] < backend_status.pending_jobs:
                print(f"\n💡 ALTERNATIVE AVAILABLE")
                print(f"   {best_backend['name']} has only {best_backend['pending']} jobs")
                print(f"   Consider using this backend for future jobs")
        
        # Time analysis
        print("\n" + "="*70)
        print("⏱️  TIME ANALYSIS")
        print("="*70)
        
        if elapsed_min > 60:
            print(f"\n⚠️  JOB HAS BEEN QUEUED FOR {elapsed_min} MINUTES")
            print(f"   This is longer than typical (5-20 minutes)")
            print(f"   Possible reasons:")
            print(f"   1. Very long queue ({backend_status.pending_jobs} jobs ahead)")
            print(f"   2. Backend maintenance or issues")
            print(f"   3. High system load")
        elif elapsed_min > 20:
            print(f"\n⏳ JOB HAS BEEN QUEUED FOR {elapsed_min} MINUTES")
            print(f"   This is within normal range but on the longer side")
            print(f"   Queue position: {backend_status.pending_jobs} jobs ahead")
        else:
            print(f"\n✅ JOB HAS BEEN QUEUED FOR {elapsed_min} MINUTES")
            print(f"   This is normal processing time")
        
        # Recommendations
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        if status_str.upper() == 'QUEUED':
            print("\n1. ✅ Job is still active - continue waiting")
            print("2. 🔄 Check status periodically with: python check_results.py")
            print("3. 📊 Monitor automatically with: python monitor_job.py")
            print("4. 🌐 Check IBM Quantum dashboard: https://quantum.ibm.com/jobs")
            
            if backend_status.pending_jobs > 10:
                print("\n5. ⚠️  Consider:")
                print("   - Using a backend with shorter queue for future jobs")
                print("   - Running during off-peak hours")
                print("   - Using quantum simulator for testing")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_delay()




