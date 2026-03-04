//! ABENA FHIR REST API Service
//!
//! Off-chain bridge between HL7 FHIR clients and the ABENA blockchain.
//! Queries blockchain state, fetches from IPFS, and returns FHIR-compliant JSON.
//!
//! Endpoints:
//! - GET  /fhir/Patient/{id}           → Query blockchain, return FHIR Patient JSON
//! - POST /fhir/Observation            → Store on blockchain, emit event
//! - GET  /fhir/DiagnosticReport/{id}  → Fetch from IPFS, verify hash on-chain

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use std::sync::Arc;
use tower_http::cors::{Any, CorsLayer};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

const DEFAULT_HTTP_PORT: u16 = 3000;
const DEFAULT_WS_URL: &str = "ws://127.0.0.1:9944";

/// Application state shared across handlers
#[derive(Clone)]
struct AppState {
    /// Substrate node WebSocket URL for RPC
    ws_url: String,
    /// IPFS gateway URL (for fetching by CID)
    ipfs_gateway: String,
}

/// FHIR Patient resource (HL7 FHIR R4 subset)
#[derive(Debug, Serialize, Deserialize)]
struct FHIRPatient {
    resource_type: String,
    id: String,
    identifier: Vec<Identifier>,
    name: Option<Vec<HumanName>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    meta: Option<Meta>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Identifier {
    system: Option<String>,
    value: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct HumanName {
    family: Option<String>,
    given: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Meta {
    /// Blockchain hash for integrity verification
    #[serde(rename = "extension")]
    extension: Option<Vec<MetaExtension>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct MetaExtension {
    url: String,
    value_string: Option<String>,
}

/// Convert blockchain PatientIdentity to FHIR Patient JSON.
/// Called by GET /fhir/Patient/{id}.
async fn to_fhir_patient(patient_id: &str, _state: &AppState) -> Result<FHIRPatient, String> {
    // TODO: 1. RPC call to chain: PatientIdentity::patient_identity(account_id)
    // TODO: 2. If found, fetch metadata from IPFS via patient.metadata_hash
    // TODO: 3. Decrypt metadata (requires key management integration)
    // TODO: 4. Build FHIR Patient from decrypted data + identifiers
    //
    // Stub: return minimal FHIR Patient for scaffold
    Ok(FHIRPatient {
        resource_type: "Patient".to_string(),
        id: patient_id.to_string(),
        identifier: vec![Identifier {
            system: Some("urn:abena:blockchain".to_string()),
            value: patient_id.to_string(),
        }],
        name: None, // Populated from decrypt_from_ipfs(metadata_hash) in production
        meta: Some(Meta {
            extension: Some(vec![MetaExtension {
                url: "urn:abena:blockchain-hash".to_string(),
                value_string: Some("pending-rpc-integration".to_string()),
            }]),
        }),
    })
}

/// GET /fhir/Patient/{id} - Query blockchain, return FHIR Patient JSON
async fn get_patient(
    State(state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    match to_fhir_patient(&id, &state).await {
        Ok(patient) => (StatusCode::OK, Json(patient)).into_response(),
        Err(e) => (
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({ "error": e })),
        )
            .into_response(),
    }
}

/// POST /fhir/Observation - Store on blockchain, emit event
async fn post_observation(
    State(state): State<Arc<AppState>>,
    Json(body): Json<serde_json::Value>,
) -> impl IntoResponse {
    // TODO: 1. Validate FHIR Observation structure
    // TODO: 2. Compute hash of observation JSON
    // TODO: 3. Store payload in IPFS (or external storage), get CID
    // TODO: 4. Submit extrinsic: Interoperability::map_fhir_resource(
    //          patient, FHIRResourceType::Observation, hash, cid, DataStandard::HL7_FHIR_R4)
    // TODO: 5. Return 201 with Location header + FHIR Observation with id
    tracing::info!(body = ?body, "POST /fhir/Observation received");
    (
        StatusCode::CREATED,
        Json(serde_json::json!({
            "resourceType": "Observation",
            "id": "obs-pending-tx",
            "meta": { "extension": [{ "url": "urn:abena:blockchain", "valueString": "extrinsic-pending" }] }
        })),
    )
        .into_response()
}

/// GET /fhir/DiagnosticReport/{id} - Fetch from IPFS, verify hash on-chain
async fn get_diagnostic_report(
    State(state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    // TODO: 1. Resolve id to (patient_id, blockchain_record_id/CID) - may need index
    // TODO: 2. Fetch content from IPFS: ipfs_gateway/ipfs/{cid}
    // TODO: 3. Compute hash of fetched content
    // TODO: 4. RPC: FHIRResources::get(patient_id, DiagnosticReport) - verify hash matches
    // TODO: 5. Return FHIR DiagnosticReport JSON
    tracing::info!(id = %id, "GET /fhir/DiagnosticReport requested");
    (
        StatusCode::OK,
        Json(serde_json::json!({
            "resourceType": "DiagnosticReport",
            "id": id,
            "meta": {
                "extension": [{ "url": "urn:abena:verified", "valueBoolean": false }]
            }
        })),
    )
        .into_response()
}

/// Health check
async fn health() -> impl IntoResponse {
    (StatusCode::OK, Json(serde_json::json!({ "status": "ok" })))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let ws_url = std::env::var("ABENA_WS_URL").unwrap_or_else(|_| DEFAULT_WS_URL.to_string());
    let ipfs_gateway =
        std::env::var("IPFS_GATEWAY").unwrap_or_else(|_| "https://ipfs.io/ipfs/".to_string());
    let port: u16 = std::env::var("FHIR_API_PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(DEFAULT_HTTP_PORT);

    let state = Arc::new(AppState {
        ws_url: ws_url.clone(),
        ipfs_gateway,
    });

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/fhir/Patient/:id", get(get_patient))
        .route("/fhir/Observation", post(post_observation))
        .route("/fhir/DiagnosticReport/:id", get(get_diagnostic_report))
        .route("/health", get(health))
        .layer(cors)
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    tracing::info!("FHIR API listening on http://{}", addr);
    tracing::info!("Configure chain at ABENA_WS_URL={}", ws_url);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
