"""
Check IBM Quantum Job Results
Run this script to check the status and retrieve results from a submitted quantum job
"""

import sys
import io
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from qiskit_ibm_runtime import QiskitRuntimeService

# Job ID from your submission
JOB_ID = 'd5skpr8husoc73epvu20'

print("="*70)
print("ABENA IHR - Quantum Job Status Checker")
print("="*70)

try:
    service = QiskitRuntimeService(channel='ibm_quantum_platform')
    job = service.job(JOB_ID)
    
    status = job.status()
    status_str = str(status) if not isinstance(status, str) else status
    
    print(f"\n📋 Job ID: {JOB_ID}")
    print(f"📊 Status: {status_str}")
    
    # Get job details
    try:
        creation_date = job.creation_date() if callable(job.creation_date) else job.creation_date
        print(f"📅 Submitted: {creation_date}")
    except:
        pass
    
    # Check status (handle both string and enum types)
    status_upper = status_str.upper() if isinstance(status_str, str) else str(status).upper()
    
    if status_upper == 'DONE':
        print("\n" + "="*70)
        print("🎉 JOB COMPLETED! RETRIEVING RESULTS...")
        print("="*70)
        
        result = job.result()
        
        print(f"\n✅ Results retrieved successfully!")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Handle new API format (PrimitiveResult)
        try:
            from collections import Counter
            import numpy as np
            
            pub_result = result[0]
            bit_array = pub_result.data.c
            
            # The _array contains integers directly (already converted from bits)
            # Shape is (num_shots, 1), so we just need to flatten it
            measurements = bit_array._array.flatten().tolist()
            
            # Count occurrences of each measurement outcome
            counts = Counter(measurements)
            total_shots = sum(counts.values())
            
            # Calculate probabilities
            probabilities = {state: count/total_shots for state, count in counts.items()}
            
            print(f"\n📊 Measurement results ({total_shots} shots):")
            print(f"   Total outcomes: {len(probabilities)}")
            
            # Format top results
            print("\n" + "="*70)
            print("🏆 TOP 5 MEASUREMENT OUTCOMES")
            print("="*70)
            sorted_outcomes = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:5]
            for i, (state, probability) in enumerate(sorted_outcomes, 1):
                binary = format(state, '04b')
                count = counts[state]
                print(f"   {i}. |{binary}⟩: {probability:.4f} ({probability*100:.2f}%) - {count} occurrences")
            
            # Show all outcomes
            print("\n" + "="*70)
            print("📊 ALL MEASUREMENT OUTCOMES")
            print("="*70)
            for state, probability in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
                binary = format(state, '04b')
                count = counts[state]
                print(f"   |{binary}⟩: {probability:.4f} ({probability*100:.2f}%) - {count}/{total_shots} shots")
            
        except Exception as e:
            print(f"\n⚠️  Error processing results: {e}")
            print(f"   Raw result type: {type(result)}")
            print(f"   Trying alternative method...")
            
            # Alternative: try to get counts directly
            try:
                pub_result = result[0]
                print(f"   Pub result: {pub_result}")
                print(f"   Data: {pub_result.data}")
                if hasattr(pub_result.data, 'c'):
                    print(f"   BitArray shape: {pub_result.data.c.shape}")
                    print(f"   BitArray: {pub_result.data.c}")
            except:
                pass
            
            import traceback
            traceback.print_exc()
        
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
        
    elif status_upper in ['QUEUED', 'RUNNING']:
        print(f"\n⏳ Job is {status_str.lower()}...")
        print("   Quantum jobs typically take 5-20 minutes to complete")
        print("   Run this script again in a few minutes to check status")
        
        # Show queue position if available
        try:
            if hasattr(job, 'queue_position'):
                queue_pos = job.queue_position()
                if queue_pos:
                    print(f"   Queue position: {queue_pos}")
        except:
            pass
            
    elif status_upper == 'ERROR':
        print(f"\n❌ Job failed with error status")
        print("   Check the IBM Quantum dashboard for error details")
        
    else:
        print(f"\n📊 Current status: {status_str}")
        print("   Check back later or visit IBM Quantum dashboard")
        
except Exception as e:
    print(f"\n❌ Error checking job: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Verify the job ID is correct")
    print("   2. Check your IBM Quantum credentials")
    print("   3. Ensure you have internet connectivity")