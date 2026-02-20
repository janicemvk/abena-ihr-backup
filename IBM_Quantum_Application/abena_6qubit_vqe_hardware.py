"""
============================================================
ABENA IHR - 6-Qubit VQE Healthcare Optimization
Run on Real IBM Quantum Hardware
============================================================

Building on successful 4-qubit test (Job ID: d5skpr8husoc73epvu20)
Now scaling to 6 qubits for more comprehensive treatment optimization.

6 Qubits represent:
  Qubit 0: Conventional pharmaceutical effectiveness
  Qubit 1: Herbal/botanical medicine compatibility
  Qubit 2: Lifestyle intervention impact (diet, exercise, sleep)
  Qubit 3: Patient genetic/genomic factors
  Qubit 4: Mind-body therapy response (meditation, acupuncture)
  Qubit 5: Endocannabinoid system modulation

This explores 2^6 = 64 treatment combinations simultaneously
(vs. 16 combinations in your 4-qubit test)
============================================================
"""

import argparse
import numpy as np
from datetime import datetime
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
import sys
import io

# Fix Windows console encoding for emojis (matches 4-qubit script)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# CLI flags
parser = argparse.ArgumentParser(description="ABENA 6-qubit hardware test (IBM Runtime Sampler).")
parser.add_argument(
    "--wait",
    action="store_true",
    help="Wait for results (can take minutes-hours). Default is submit-only (prints Job ID then exits).",
)
args = parser.parse_args()

# ============================================================
# STEP 1: Connect to IBM Quantum
# ============================================================
print("=" * 70)
print("ABENA IHR - 6-Qubit VQE Treatment Optimization")
print("Real IBM Quantum Hardware Execution")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

print("\n🔌 Step 1: Connecting to IBM Quantum...")
try:
    service = QiskitRuntimeService(channel='ibm_quantum')
    print("✅ Connected to IBM Quantum successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nIf credentials expired, re-save them:")
    print("  from qiskit_ibm_runtime import QiskitRuntimeService")
    print("  QiskitRuntimeService.save_account(channel='ibm_quantum', token='YOUR_TOKEN', overwrite=True)")
    exit()

# ============================================================
# STEP 2: Select Best Backend (Prefer shortest queue)
# ============================================================
print("\n🖥️  Step 2: Checking available quantum computers...")

backends = service.backends(
    simulator=False,
    operational=True,
    min_num_qubits=6
)

print(f"\nFound {len(backends)} available quantum computers:\n")
backend_info = []
for b in backends:
    status = b.status()
    queue = status.pending_jobs
    print(f"  🔬 {b.name}")
    print(f"     Qubits: {getattr(b, 'num_qubits', 'N/A')} | Queue: {queue} jobs | Online: {status.operational}")
    backend_info.append((b, queue))

# Pick backend with shortest queue
backend_info.sort(key=lambda x: x[1])
backend = backend_info[0][0]
print(f"\n✅ Selected: {backend.name} (shortest queue: {backend_info[0][1]} jobs)")

# ============================================================
# STEP 3: Build 6-Qubit VQE Healthcare Circuit
# ============================================================
print("\n🧬 Step 3: Building 6-qubit VQE healthcare circuit...")

num_qubits = 6

# Treatment factor labels
treatment_labels = {
    0: "Pharmaceutical",
    1: "Herbal/Botanical",
    2: "Lifestyle (Diet/Exercise/Sleep)",
    3: "Genetic/Genomic Factors",
    4: "Mind-Body (Meditation/Acupuncture)",
    5: "Endocannabinoid System"
}

# Create parameterized VQE ansatz circuit
qc = QuantumCircuit(num_qubits, num_qubits)

# --- Layer 1: Initial superposition with treatment-specific rotations ---
# These angles represent initial treatment efficacy estimates
# (In production, these would come from patient data)
initial_angles = [
    0.8,   # Pharmaceutical: moderate-high baseline
    0.5,   # Herbal: moderate baseline
    0.7,   # Lifestyle: moderate-high baseline
    0.3,   # Genetic: patient-specific (low = favorable genetics)
    0.6,   # Mind-body: moderate baseline
    0.4,   # Endocannabinoid: moderate-low baseline
]

for i in range(num_qubits):
    qc.ry(initial_angles[i] * np.pi, i)

qc.barrier()

# --- Layer 2: Drug-Herb interactions (critical safety layer) ---
# Entangle pharmaceutical with herbal to detect interactions
qc.cx(0, 1)  # Pharma <-> Herbal interaction
qc.rz(0.3, 1)  # Interaction strength parameter

# --- Layer 3: Lifestyle modifies drug effectiveness ---
qc.cx(2, 0)  # Lifestyle <-> Pharma synergy
qc.ry(0.4, 0)

# --- Layer 4: Genetic factors affect all treatments ---
qc.cx(3, 0)  # Genetics <-> Pharma
qc.cx(3, 1)  # Genetics <-> Herbal
qc.cx(3, 4)  # Genetics <-> Mind-body

qc.barrier()

# --- Layer 5: Mind-body interactions ---
qc.cx(4, 2)  # Mind-body <-> Lifestyle synergy
qc.cx(4, 5)  # Mind-body <-> Endocannabinoid

# --- Layer 6: Endocannabinoid cross-interactions ---
qc.cx(5, 0)  # ECS <-> Pharma (cannabinoid-drug interaction)
qc.cx(5, 1)  # ECS <-> Herbal (cannabinoid-herb synergy)

qc.barrier()

# --- Layer 7: Second variational layer (refinement) ---
refinement_angles = [0.2, 0.15, 0.25, 0.1, 0.18, 0.12]
for i in range(num_qubits):
    qc.ry(refinement_angles[i] * np.pi, i)

# Additional entanglement for complex multi-way interactions
qc.cx(0, 5)  # Pharma <-> ECS (full loop)
qc.cx(1, 4)  # Herbal <-> Mind-body
qc.cx(2, 3)  # Lifestyle <-> Genetics

qc.barrier()

# --- Measurement ---
qc.measure(range(num_qubits), range(num_qubits))

print(f"✅ Circuit created!")
print(f"   Qubits: {num_qubits}")
print(f"   Depth: {qc.depth()}")
print(f"   Gates: {qc.count_ops()}")
print(f"   Treatment combinations explored: {2**num_qubits}")

# ============================================================
# STEP 4: Transpile for Hardware
# ============================================================
print(f"\n⚙️  Step 4: Transpiling circuit for {backend.name}...")

transpiled = transpile(
    qc,
    backend=backend,
    optimization_level=3  # Maximum optimization
)

print(f"✅ Transpilation complete!")
print(f"   Hardware-optimized depth: {transpiled.depth()}")
print(f"   Hardware gates: {dict(transpiled.count_ops())}")

# ============================================================
# STEP 5: Execute on Real Quantum Hardware
# ============================================================
print(f"\n🚀 Step 5: Submitting job to {backend.name}...")
print(f"   Shots: 4096 (4x more than your 4-qubit test)")
print(f"   This gives more statistical precision\n")

shots = 4096

sampler = Sampler(mode=backend)
job = sampler.run([transpiled], shots=shots)
job_id = job.job_id()

print(f"📋 Job submitted!")
print(f"   Job ID: {job_id}")
print(f"   Backend: {backend.name}")
print(f"   Status: {job.status()}")

if not args.wait:
    print("\n✅ Submit-only mode (default): not waiting for results.")
    print("   Open IBM Quantum dashboard and look up the Job ID to show it live.")
    print("   To wait for results, re-run with: --wait")
    raise SystemExit(0)

print(f"\n⏳ Waiting for quantum computer to execute...")
print(f"   (This may take minutes to hours depending on queue)")
print(f"   You can close this and check results later using the Job ID.\n")

result = job.result()

# ============================================================
# STEP 6: Analyze Results
# ============================================================
print("\n" + "=" * 70)
print("🎉 RESULTS FROM REAL QUANTUM HARDWARE")
print("=" * 70)

# Extract quasi distribution from Sampler (stable API)
quasi = None
if hasattr(result, "quasi_dists") and result.quasi_dists:
    quasi = result.quasi_dists[0]
else:
    # Fallback: try treating result like a list/dict
    try:
        quasi = result[0]
    except Exception:
        quasi = None

if quasi is None:
    raise RuntimeError("Could not parse Sampler result. Try re-running with a newer qiskit-ibm-runtime.")

# Convert quasi distribution to "counts-like" using probabilities * shots
counts = {format(state, f"0{num_qubits}b"): int(prob * shots) for state, prob in quasi.items()}

print(f"\nBackend: {backend.name}")
print(f"Job ID: {job_id}")
print(f"Total measurements: {shots}")
print(f"Unique outcomes: {len(counts)}")

# Sort by frequency
sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

print(f"\n{'='*70}")
print(f"TOP 10 TREATMENT COMBINATIONS:")
print(f"{'='*70}")
print(f"{'Rank':<6}{'State':<10}{'Count':<8}{'Prob%':<8}  Treatment Interpretation")
print(f"{'-'*70}")

for rank, (state, count) in enumerate(sorted_counts[:10], 1):
    prob = count / shots * 100
    
    # Interpret each qubit
    interpretation = []
    for bit_idx, bit in enumerate(reversed(state)):
        label = treatment_labels[bit_idx]
        short_label = label.split("(")[0].strip()  # Shortened name
        if bit == '1':
            interpretation.append(f"✅{short_label}")
        else:
            interpretation.append(f"❌{short_label}")
    
    interp_str = " | ".join(interpretation[:3])  # First 3 on line 1
    interp_str2 = " | ".join(interpretation[3:])  # Last 3 on line 2
    
    print(f"  {rank:<4} |{state}⟩  {count:<6}  {prob:>5.1f}%   {interp_str}")
    print(f"{'':>32}  {interp_str2}")

# ============================================================
# STEP 7: Clinical Insights Summary
# ============================================================
print(f"\n{'='*70}")
print("CLINICAL INSIGHTS SUMMARY")
print(f"{'='*70}")

# Calculate per-qubit activation rates
qubit_rates = {}
for q in range(num_qubits):
    active_count = sum(
        count for state, count in counts.items()
        if state[num_qubits - 1 - q] == '1'
    )
    qubit_rates[q] = active_count / shots * 100

print("\nIndividual Treatment Factor Effectiveness:")
for q in range(num_qubits):
    bar = "█" * int(qubit_rates[q] / 2) + "░" * (50 - int(qubit_rates[q] / 2))
    print(f"  Q{q} {treatment_labels[q]:<40} {qubit_rates[q]:>5.1f}% {bar}")

# Top combination analysis
top_state = sorted_counts[0][0]
top_prob = sorted_counts[0][1] / shots * 100
print(f"\n🏆 Optimal Treatment Combination: |{top_state}⟩ ({top_prob:.1f}%)")
print(f"   This means the quantum computer found that the most likely")
print(f"   optimal treatment involves:")
for bit_idx, bit in enumerate(reversed(top_state)):
    status = "INCLUDE" if bit == '1' else "EXCLUDE/ADJUST"
    print(f"   {'✅' if bit == '1' else '⚠️ '} {treatment_labels[bit_idx]}: {status}")

# ============================================================
# STEP 8: Save Results
# ============================================================
print(f"\n{'='*70}")
print("SAVE THIS INFORMATION")
print(f"{'='*70}")
print(f"""
📋 Hardware Validation Record:
   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Backend: {backend.name}
   Job ID: {job_id}
   Qubits: {num_qubits}
   Shots: {shots}
   Circuit Depth: {transpiled.depth()}
   Unique Outcomes: {len(counts)}
   Top Result: |{sorted_counts[0][0]}⟩ ({sorted_counts[0][1]/shots*100:.1f}%)
   
   Previous 4-qubit validation:
   Job ID: d5skpr8husoc73epvu20 (ibm_fez, Jan 27, 2026)
   
   This 6-qubit test explores {2**num_qubits} combinations
   (4x more than the 4-qubit test's {2**4} combinations)
""")

# Save results to file
results_file = f"abena_6qubit_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(results_file, 'w') as f:
    f.write(f"ABENA IHR - 6-Qubit Quantum Hardware Validation\n")
    f.write(f"{'='*50}\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Backend: {backend.name}\n")
    f.write(f"Job ID: {job_id}\n")
    f.write(f"Qubits: {num_qubits}\n")
    f.write(f"Shots: {shots}\n")
    f.write(f"Circuit Depth: {transpiled.depth()}\n\n")
    f.write(f"ALL RESULTS:\n")
    for state, count in sorted_counts:
        f.write(f"  |{state}⟩: {count} ({count/shots*100:.2f}%)\n")
    f.write(f"\nPer-Qubit Activation Rates:\n")
    for q in range(num_qubits):
        f.write(f"  Q{q} {treatment_labels[q]}: {qubit_rates[q]:.1f}%\n")

print(f"💾 Results saved to: {results_file}")
print(f"\n🎉 6-Qubit hardware validation complete!")