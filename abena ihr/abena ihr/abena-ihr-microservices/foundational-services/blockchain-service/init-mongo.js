// MongoDB initialization script for Abena IHR Blockchain Service

// Switch to the abena_ihr database
db = db.getSiblingDB('abena_ihr');

// Create collections with proper indexes
print('Creating collections and indexes...');

// Health Records Collection
db.createCollection('health_records');
db.health_records.createIndex({ "patient_id": 1 });
db.health_records.createIndex({ "provider_id": 1 });
db.health_records.createIndex({ "record_type": 1 });
db.health_records.createIndex({ "timestamp": -1 });
db.health_records.createIndex({ "blockchain_tx_id": 1 });
db.health_records.createIndex({ "data_hash": 1 });
db.health_records.createIndex({ "is_deleted": 1 });
db.health_records.createIndex({ "created_at": -1 });

// Access Audit Collection
db.createCollection('access_audit');
db.access_audit.createIndex({ "user_id": 1 });
db.access_audit.createIndex({ "timestamp": -1 });
db.access_audit.createIndex({ "action": 1 });
db.access_audit.createIndex({ "record_id": 1 });
db.access_audit.createIndex({ "ip_address": 1 });
db.access_audit.createIndex({ "consent_given": 1 });

// Consents Collection
db.createCollection('consents');
db.consents.createIndex({ "patient_id": 1 });
db.consents.createIndex({ "provider_id": 1 });
db.consents.createIndex({ "purpose": 1 });
db.consents.createIndex({ "granted": 1 });
db.consents.createIndex({ "expires_at": 1 });
db.consents.createIndex({ "created_at": -1 });

// Blockchain Transactions Collection
db.createCollection('blockchain_transactions');
db.blockchain_transactions.createIndex({ "tx_id": 1 });
db.blockchain_transactions.createIndex({ "patient_id": 1 });
db.blockchain_transactions.createIndex({ "timestamp": -1 });
db.blockchain_transactions.createIndex({ "type": 1 });
db.blockchain_transactions.createIndex({ "data_hash": 1 });

// Consensus Votes Collection
db.createCollection('consensus_votes');
db.consensus_votes.createIndex({ "tx_id": 1 });
db.consensus_votes.createIndex({ "node_id": 1 });
db.consensus_votes.createIndex({ "timestamp": -1 });
db.consensus_votes.createIndex({ "vote": 1 });

// Patient Provider Relationships Collection
db.createCollection('patient_provider_relationships');
db.patient_provider_relationships.createIndex({ "patient_id": 1 });
db.patient_provider_relationships.createIndex({ "provider_id": 1 });
db.patient_provider_relationships.createIndex({ "relationship_type": 1 });
db.patient_provider_relationships.createIndex({ "is_active": 1 });

// Data Integrity Checks Collection
db.createCollection('data_integrity_checks');
db.data_integrity_checks.createIndex({ "record_id": 1 });
db.data_integrity_checks.createIndex({ "check_type": 1 });
db.data_integrity_checks.createIndex({ "timestamp": -1 });
db.data_integrity_checks.createIndex({ "status": 1 });

// Analytics Collection
db.createCollection('analytics');
db.analytics.createIndex({ "metric_name": 1 });
db.analytics.createIndex({ "timestamp": -1 });
db.analytics.createIndex({ "patient_id": 1 });
db.analytics.createIndex({ "provider_id": 1 });

print('Collections and indexes created successfully!');

// Insert sample data for testing (optional)
print('Inserting sample data...');

// Sample consent record
db.consents.insertOne({
    "_id": "consent_001",
    "patient_id": "PAT001",
    "provider_id": "PROV001",
    "purpose": "clinical_care",
    "data_types": ["vitals", "labs", "medications"],
    "granted": true,
    "expires_at": new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year from now
    "conditions": ["emergency_access_allowed"],
    "created_at": new Date(),
    "updated_at": new Date()
});

// Sample patient-provider relationship
db.patient_provider_relationships.insertOne({
    "_id": "rel_001",
    "patient_id": "PAT001",
    "provider_id": "PROV001",
    "relationship_type": "primary",
    "established_at": new Date(),
    "is_active": true,
    "created_by": "system"
});

print('Sample data inserted successfully!');

// Create a user for the application (if not using root)
try {
    db.createUser({
        user: "abena_user",
        pwd: "abena_password",
        roles: [
            { role: "readWrite", db: "abena_ihr" }
        ]
    });
    print('Application user created successfully!');
} catch (error) {
    print('User already exists or error creating user:', error.message);
}

print('MongoDB initialization completed!'); 