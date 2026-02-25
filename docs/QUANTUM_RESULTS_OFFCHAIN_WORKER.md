# Quantum Results Off-Chain Worker

## Overview

The quantum-results pallet includes an **off-chain worker** that polls the IBM Quantum API for job completion, then submits verified attestations to the chain via **unsigned transactions**.

## Responsibilities

1. **Poll IBM Quantum API** – Every `OffchainWorkerInterval` blocks (default 10), the worker runs.
2. **Check queue** – Reads `QuantumJobQueue` for jobs with status `Pending` or `Running`.
3. **Fetch job status** – For each such job, sends `GET https://api.quantum-computing.ibm.com/api/v2/jobs/{job_id}`.
4. **Handle response**:
   - **COMPLETED**: Builds attestation (result hash from response body), submits `submit_attestation_unsigned`, removes job from queue.
   - **FAILED**: Removes job from queue (no attestation).
5. **Clean up** – Completed/failed jobs are removed from the queue.

## Workflow

1. A user calls **`enqueue_quantum_job`** with:
   - `job_id` (IBM job ID, e.g. string bytes),
   - `backend_id`,
   - and full **attestation context** (patient_pseudonym, algorithm_type, parameters_hash, execution_timestamp, circuit_depth, qubit_count, shots, linked_clinical_module).
2. The job is appended to `QuantumJobQueue` with status `Pending` and this context.
3. Every N blocks, the off-chain worker:
   - For each pending job, calls IBM API `GET /api/v2/jobs/{job_id}`.
   - If status is COMPLETED: hashes the response body as `result_hash`, builds an empty `ibm_signature` (or extend later to parse from response), and submits **`submit_attestation_unsigned`** with the stored context and this result.
   - If status is FAILED: removes the job from the queue.
4. **`submit_attestation_unsigned`** is only valid if the same `job_id_hash` is still in the queue with context (enforced by **ValidateUnsigned**). The worker then removes that job from the queue after a successful submit.

## IBM API Integration

- **Base URL**: `https://api.quantum-computing.ibm.com`
- **Endpoint**: `GET /api/v2/jobs/{job_id}`
- **Authentication**: IBM API tokens must **not** be stored on-chain. The node operator can set a token in **off-chain local storage** (e.g. key `ibm_quantum_api_token`). The current worker does not add an `Authorization` header; you can extend it to read from `sp_io::offchain::local_storage_get(StorageKind::PERSENT, b"ibm_quantum_api_token")` and use `http_request_add_header` if your Substrate version supports it.
- **Timeouts**: Request deadline is 8 seconds.
- **Rate limiting**: Worker runs at most every N blocks; process one request per job per run to avoid hammering the API.

## Security

- **No API tokens on-chain** – Credentials stay in off-chain storage or node config.
- **Unsigned tx validation** – Only calls whose `job_id_hash` is in the queue with attestation context are accepted (ValidateUnsigned).
- **Response validation** – Only 200 responses with body containing `"status":"COMPLETED"` or `"status": "COMPLETED"` trigger attestation; FAILED is handled by cleanup.

## Retry and Failures

- **Network/HTTP errors** – Job stays in queue and is retried on the next worker run.
- **FAILED status** – Job is removed from queue (no attestation).
- **Timeout** – No response within 8s leaves the job in queue for the next run.

## Configuration

- **`OffchainWorkerInterval`** (Config): Run worker every N blocks (e.g. 10). Set in runtime and mock.

## Extrinsics

| Call | Description |
|------|-------------|
| **enqueue_quantum_job** | Add a job to the queue with full attestation context; worker will poll IBM and submit attestation when completed. |
| **submit_attestation_unsigned** | Used by the worker only; validates via `ValidateUnsigned` (job must be in queue with context). |

## Optional Extensions

- **Exponential backoff**: Store per-job retry count in off-chain storage and delay retries.
- **API token header**: Read token from off-chain storage and add `Authorization: Bearer <token>` to the HTTP request.
- **Parse IBM signature**: If the API returns a signature in the response, parse it and pass as `ibm_signature` so on-chain verification can succeed.
