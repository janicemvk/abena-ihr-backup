//! Shim crate: the w3f/ring-proof repository publishes as `w3f-ring-proof`, but
//! bandersnatch_vrfs (used by sp-core) expects a crate named `ring`.
//! This crate re-exports w3f-ring-proof to satisfy that dependency.

#![cfg_attr(not(feature = "std"), no_std)]

pub use w3f_ring_proof::*;
