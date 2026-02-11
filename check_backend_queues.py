"""
Check Backend Queue Status
Shows queue lengths for all available quantum backends
"""

import sys
import io
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from qiskit_ibm_runtime import QiskitRuntimeService

def check_backend_queues():
    """Check queue status for all available backends"""
    print("="*70)
    print("🖥️  ABENA IHR - Quantum Backend Queue Status")
    print("="*70)
    
    try:
        service = QiskitRuntimeService(channel='ibm_quantum_platform')
        
        print("\n📡 Fetching available backends...")
        backends = service.backends()
        
        if not backends:
            print("❌ No backends available")
            return
        
        print(f"\n✅ Found {len(backends)} backend(s)")
        print("\n" + "="*70)
        print("BACKEND QUEUE STATUS")
        print("="*70)
        
        backend_info = []
        
        for backend in backends:
            try:
                status = backend.status()
                pending_jobs = status.pending_jobs
                status_msg = status.status_msg
                
                backend_info.append({
                    'name': backend.name,
                    'qubits': backend.num_qubits,
                    'pending': pending_jobs,
                    'status': status_msg,
                    'operational': status_msg.lower() == 'active'
                })
            except Exception as e:
                print(f"⚠️  Error checking {backend.name}: {e}")
        
        # Sort by pending jobs (ascending)
        backend_info.sort(key=lambda x: x['pending'])
        
        print(f"\n{'Backend Name':<20} {'Qubits':<10} {'Pending Jobs':<15} {'Status':<15}")
        print("-" * 70)
        
        for info in backend_info:
            status_icon = "✅" if info['operational'] else "⚠️"
            print(f"{status_icon} {info['name']:<18} {info['qubits']:<10} {info['pending']:<15} {info['status']:<15}")
        
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        # Find backends with shortest queues
        operational_backends = [b for b in backend_info if b['operational']]
        
        if operational_backends:
            shortest_queue = min(operational_backends, key=lambda x: x['pending'])
            print(f"\n✅ Best option: {shortest_queue['name']}")
            print(f"   Pending jobs: {shortest_queue['pending']}")
            print(f"   Qubits: {shortest_queue['qubits']}")
            
            if shortest_queue['pending'] < 5:
                print("   ⭐ Low queue - good choice for new jobs!")
            elif shortest_queue['pending'] < 10:
                print("   ⚡ Moderate queue - reasonable wait time")
            else:
                print("   ⏳ Long queue - consider waiting or using simulator")
        else:
            print("\n⚠️  No operational backends found")
        
        # Show current job's backend
        print("\n" + "="*70)
        print("📋 CURRENT JOB INFO")
        print("="*70)
        print("   Job ID: d5skpr8husoc73epvu20")
        print("   Backend: ibm_fez")
        
        ibm_fez_info = next((b for b in backend_info if b['name'] == 'ibm_fez'), None)
        if ibm_fez_info:
            print(f"   Current queue position: {ibm_fez_info['pending']} jobs")
            if ibm_fez_info['pending'] > 10:
                print("   ⚠️  Long queue detected - this explains the wait time")
            elif ibm_fez_info['pending'] > 5:
                print("   ⏳ Moderate queue - job should complete soon")
            else:
                print("   ✅ Short queue - job processing normally")
        
        print("\n" + "="*70)
        print("⏱️  ESTIMATED WAIT TIMES")
        print("="*70)
        print("   Average job processing time: 2-5 minutes")
        print("   Queue wait time: ~2-5 minutes per job ahead")
        
        if ibm_fez_info:
            estimated_wait = ibm_fez_info['pending'] * 3  # ~3 min per job
            print(f"   Estimated wait for your job: ~{estimated_wait} minutes")
            print(f"   (Based on {ibm_fez_info['pending']} jobs ahead)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify IBM Quantum credentials")
        print("   3. Try again in a few moments")

if __name__ == "__main__":
    check_backend_queues()





