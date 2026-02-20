//! ABENA Blockchain CLI Tool
//!
//! A simple CLI tool to interact with the ABENA blockchain for patient identity management.

use clap::{Parser, Subcommand};
use subxt::{
    OnlineClient,
    PolkadotConfig,
};
use std::str::FromStr;

// Note: In production, you would generate the metadata from your runtime
// For now, we'll use a simplified approach with direct calls

#[derive(Parser)]
#[command(name = "abena-cli")]
#[command(about = "ABENA Blockchain CLI - Interact with patient identity pallet", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
    
    /// WebSocket URL of the node (default: ws://127.0.0.1:9944)
    #[arg(long, default_value = "ws://127.0.0.1:9944")]
    url: String,
}

#[derive(Subcommand)]
enum Commands {
    /// Register a new patient
    RegisterPatient {
        /// Patient account address (SS58 format)
        account: String,
        /// Public key (32 bytes hex string)
        #[arg(long)]
        public_key: String,
        /// Metadata hash (32 bytes hex string)
        #[arg(long)]
        metadata_hash: String,
        /// Emergency contact address (optional, SS58 format)
        #[arg(long)]
        emergency_contact: Option<String>,
    },
    
    /// Update consent for a therapeutic modality
    UpdateConsent {
        /// Patient account address
        account: String,
        /// Therapeutic modality (WesternMedicine, TCM, Ayurveda, Homeopathy, Naturopathy, Other)
        #[arg(long)]
        modality: String,
        /// Grant consent (true) or revoke (false)
        #[arg(long)]
        granted: bool,
        /// Expiration timestamp in seconds (optional)
        #[arg(long)]
        expires_at: Option<u64>,
    },
    
    /// Grant provider access to patient records
    GrantProviderAccess {
        /// Patient account address
        patient: String,
        /// Provider account address
        provider: String,
        /// Access level (Read, ReadWrite, Emergency)
        #[arg(long)]
        access_level: String,
        /// Expiration timestamp in seconds (optional)
        #[arg(long)]
        expires_at: Option<u64>,
    },
    
    /// Revoke provider access
    RevokeProviderAccess {
        /// Patient account address
        patient: String,
        /// Provider account address
        provider: String,
    },
    
    /// Query patient identity
    QueryPatient {
        /// Patient account address
        account: String,
    },
    
    /// Verify provider access
    VerifyAccess {
        /// Patient account address
        patient: String,
        /// Provider account address
        provider: String,
    },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    
    println!("🔗 Connecting to ABENA blockchain at {}...", cli.url);
    
    // Note: This is a simplified example. In production, you would:
    // 1. Generate metadata from your runtime using subxt-codegen
    // 2. Use the generated types and client
    // 3. Sign transactions with the account's private key
    
    match cli.command {
        Commands::RegisterPatient { account, public_key, metadata_hash, emergency_contact } => {
            println!("📝 Registering patient: {}", account);
            println!("   Public Key: {}", public_key);
            println!("   Metadata Hash: {}", metadata_hash);
            if let Some(contact) = emergency_contact {
                println!("   Emergency Contact: {}", contact);
            }
            println!("\n⚠️  Note: This is a template. To actually submit transactions:");
            println!("   1. Generate runtime metadata: subxt codegen --url {}", cli.url);
            println!("   2. Use the generated client to submit signed transactions");
            println!("   3. Provide the account's private key for signing");
        },
        
        Commands::UpdateConsent { account, modality, granted, expires_at } => {
            println!("📋 Updating consent for patient: {}", account);
            println!("   Modality: {}", modality);
            println!("   Granted: {}", granted);
            if let Some(exp) = expires_at {
                println!("   Expires at: {}", exp);
            }
            println!("\n⚠️  Note: This is a template. Implement actual transaction submission.");
        },
        
        Commands::GrantProviderAccess { patient, provider, access_level, expires_at } => {
            println!("🔓 Granting provider access:");
            println!("   Patient: {}", patient);
            println!("   Provider: {}", provider);
            println!("   Access Level: {}", access_level);
            if let Some(exp) = expires_at {
                println!("   Expires at: {}", exp);
            }
            println!("\n⚠️  Note: This is a template. Implement actual transaction submission.");
        },
        
        Commands::RevokeProviderAccess { patient, provider } => {
            println!("🔒 Revoking provider access:");
            println!("   Patient: {}", patient);
            println!("   Provider: {}", provider);
            println!("\n⚠️  Note: This is a template. Implement actual transaction submission.");
        },
        
        Commands::QueryPatient { account } => {
            println!("🔍 Querying patient identity: {}", account);
            println!("\n⚠️  Note: This is a template. To query actual data:");
            println!("   1. Connect to the node using subxt client");
            println!("   2. Query the PatientIdentities storage map");
            println!("   3. Display the patient DID information");
        },
        
        Commands::VerifyAccess { patient, provider } => {
            println!("✅ Verifying provider access:");
            println!("   Patient: {}", patient);
            println!("   Provider: {}", provider);
            println!("\n⚠️  Note: This is a template. To verify actual access:");
            println!("   1. Query the ProviderAccessList storage");
            println!("   2. Check if access exists and hasn't expired");
        },
    }
    
    println!("\n✅ Command completed (template mode)");
    println!("\n📚 Next steps:");
    println!("   1. Build your runtime and start the node:");
    println!("      cargo build --release");
    println!("      ./target/release/abena-node --dev --tmp");
    println!("   2. Generate runtime metadata:");
    println!("      subxt codegen --url ws://127.0.0.1:9944 > src/runtime_types.rs");
    println!("   3. Update this CLI to use the generated types");
    println!("   4. Add account management and transaction signing");
    
    Ok(())
}

