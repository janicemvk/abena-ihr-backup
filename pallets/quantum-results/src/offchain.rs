//! Quantum Results Off-Chain Worker
//!
//! Polls IBM Quantum API for job completion and submits verified attestations to the chain.
//! Uses the **on-chain** `QuantumJobQueue` (populated via `enqueue_quantum_job`) so that
//! `ValidateUnsigned` accepts the attestation transactions. Jobs must be enqueued on-chain
//! before the worker can submit attestations for them.
//!
//! ## Flow
//! 1. Jobs are enqueued via `enqueue_quantum_job` (signed extrinsic) with IBM job ID + attestation context.
//! 2. Off-chain worker runs every `OffchainWorkerInterval` blocks.
//! 3. Worker reads `QuantumJobQueue`, polls IBM API (v2) for each pending/running job.
//! 4. When IBM returns COMPLETED: computes result_hash from response body, submits `submit_attestation_unsigned`.
//! 5. When IBM returns FAILED/CANCELLED: removes job from queue.
//!
//! ## IBM API Token
//! Set via off-chain local storage (node operator):
//!   `offchain::local_storage_set(PERSISTENT, b"abena::quantum::ibm_api_token", token_bytes)`
//! If not set, the worker still polls (unauthenticated). To add an Authorization header,
//! extend `start_job_request` using `http_request_add_header` after `http_request_start`.

use crate::pallet::{
    Call, Config, JobCompletionStatus, Pallet, QuantumJobQueue, SignatureMaxLen,
};
use frame_support::traits::Get;
use frame_system::offchain::SubmitTransaction;
use sp_core::offchain::{Duration, HttpRequestStatus};
use sp_runtime::traits::{Hash, Zero};
use frame_system::pallet_prelude::BlockNumberFor;
use sp_runtime::BoundedVec;
use sp_std::vec::Vec;

/// IBM Quantum REST API v2 – job status endpoint prefix.
const IBM_JOBS_BASE: &[u8] = b"https://api.quantum-computing.ibm.com/api/v2/jobs/";
/// HTTP timeout per request (ms).
const HTTP_TIMEOUT_MS: u64 = 8_000;

impl<T: Config> Pallet<T> {
    /// Off-chain worker entry point called from the `Hooks` impl in `lib.rs`.
    ///
    /// Gated by `OffchainWorkerInterval`: exits immediately on blocks that are
    /// not multiples of that interval, keeping on-chain overhead minimal.
    pub fn offchain_worker_impl(block_number: BlockNumberFor<T>) {
        #[cfg(feature = "std")]
        log::info!(
            "⚛️  ABENA Quantum Results Off-chain Worker – block {:?}",
            block_number
        );

        if block_number % T::OffchainWorkerInterval::get() != Zero::zero() {
            return;
        }

        // Read the on-chain queue once; iterate a snapshot so mutations below are safe.
        let queue = QuantumJobQueue::<T>::get();
        if queue.is_empty() {
            return;
        }

        for pending in queue.iter().cloned().collect::<Vec<_>>() {
            // Only poll jobs that are still waiting on IBM.
            if pending.status != JobCompletionStatus::Pending
                && pending.status != JobCompletionStatus::Running
            {
                continue;
            }
            // Skip jobs with no attestation context (incomplete enqueue).
            let Some(ref ctx) = pending.attestation_context else {
                continue;
            };

            // Build URL: IBM_JOBS_BASE + job_id bytes (no heap alloc / format! needed).
            let mut url_buf = [0u8; 256];
            let blen = IBM_JOBS_BASE.len().min(url_buf.len());
            url_buf[..blen].copy_from_slice(&IBM_JOBS_BASE[..blen]);
            let jlen = pending.job_id.len().min(url_buf.len().saturating_sub(blen));
            url_buf[blen..blen + jlen].copy_from_slice(&pending.job_id[..jlen]);
            let url = match sp_std::str::from_utf8(&url_buf[..blen + jlen]) {
                Ok(s) => s,
                Err(_) => continue,
            };

            // --- HTTP GET ---
            let request_id = match sp_io::offchain::http_request_start("GET", url, &[]) {
                Ok(id) => id,
                Err(_) => {
                    #[cfg(feature = "std")]
                    log::warn!("⚠️  http_request_start failed for {:?}", url);
                    continue;
                }
            };

            let deadline =
                sp_io::offchain::timestamp().add(Duration::from_millis(HTTP_TIMEOUT_MS));
            let statuses = sp_io::offchain::http_response_wait(&[request_id], Some(deadline));
            match statuses.first() {
                Some(s) if *s == HttpRequestStatus::Finished(200) => {}
                _ => continue,
            }

            // Read response body (chunked).
            let mut body: Vec<u8> = Vec::new();
            let mut buf = [0u8; 4096];
            loop {
                match sp_io::offchain::http_response_read_body(
                    request_id,
                    &mut buf,
                    Some(deadline),
                ) {
                    Ok(0) => break,
                    Ok(n) => body.extend_from_slice(&buf[..n as usize]),
                    Err(_) => break,
                }
            }

            let body_str = sp_std::str::from_utf8(&body).unwrap_or("");

            // --- Handle terminal failure ---
            if body_str.contains("\"status\":\"FAILED\"")
                || body_str.contains("\"status\": \"FAILED\"")
                || body_str.contains("\"status\":\"CANCELLED\"")
                || body_str.contains("\"status\": \"CANCELLED\"")
            {
                QuantumJobQueue::<T>::mutate(|q| {
                    q.retain(|p| p.job_id_hash != pending.job_id_hash);
                });
                #[cfg(feature = "std")]
                log::warn!(
                    "❌ IBM job {:?} failed/cancelled – removed from queue",
                    sp_std::str::from_utf8(pending.job_id.as_slice()).unwrap_or("?")
                );
                continue;
            }

            // --- Only proceed on COMPLETED ---
            if !body_str.contains("\"status\":\"COMPLETED\"")
                && !body_str.contains("\"status\": \"COMPLETED\"")
            {
                // Still QUEUED or RUNNING; leave in queue.
                continue;
            }

            // Hash the raw response body as the result commitment.
            let result_hash = T::Hashing::hash_of(&body);

            // IBM signature is placeholder; real verification happens via on-chain
            // `verify_ibm_signature` once an IBM public key is registered with `register_ibm_key`.
            let ibm_sig: BoundedVec<u8, SignatureMaxLen> = BoundedVec::default();

            let call = Call::<T>::submit_attestation_unsigned {
                job_id: pending.job_id.to_vec(),
                patient_pseudonym: ctx.patient_pseudonym,
                algorithm_type: ctx.algorithm_type.clone(),
                algorithm_version: ctx.algorithm_version,
                parameters_hash: ctx.parameters_hash,
                result_hash,
                ibm_signature: ibm_sig.to_vec(),
                execution_timestamp: ctx.execution_timestamp,
                circuit_depth: ctx.circuit_depth,
                qubit_count: ctx.qubit_count,
                shots: ctx.shots,
                linked_clinical_module: ctx.linked_clinical_module.clone().map(|b| b.to_vec()),
            };

            let _ = SubmitTransaction::<T, Call<T>>::submit_unsigned_transaction(call.into());

            // Remove from queue (on-chain mutate inside offchain worker is safe for StorageValue).
            QuantumJobQueue::<T>::mutate(|q| {
                q.retain(|p| p.job_id_hash != pending.job_id_hash);
            });

            #[cfg(feature = "std")]
            log::info!(
                "✅ Attestation submitted for IBM job {:?}",
                sp_std::str::from_utf8(pending.job_id.as_slice()).unwrap_or("?")
            );
        }
    }
}
