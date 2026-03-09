//! Shim crate: the w3f/fflonk repository publishes as `w3f-pcs`, but
//! bandersnatch_vrfs (used by sp-core) expects a crate named `fflonk`.
//! This crate re-exports w3f-pcs to satisfy that dependency.

#![cfg_attr(not(feature = "std"), no_std)]

pub use w3f_pcs::*;
