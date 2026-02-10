package smart_contracts

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// HealthRecordContract represents the smart contract for managing health records
type HealthRecordContract struct {
	contractapi.Contract
}

// HealthRecord represents a health record entry
type HealthRecord struct {
	ID              string            `json:"id"`
	PatientID       string            `json:"patientId"`
	ProviderID      string            `json:"providerId"`
	RecordType      string            `json:"recordType"`
	Data            string            `json:"data"` // Encrypted data
	Hash            string            `json:"hash"`
	Timestamp       time.Time         `json:"timestamp"`
	ConsentGranted  bool              `json:"consentGranted"`
	AccessControl   map[string]bool   `json:"accessControl"`
	Metadata        map[string]string `json:"metadata"`
	Version         int               `json:"version"`
	PreviousHash    string            `json:"previousHash"`
	BlockNumber     uint64            `json:"blockNumber"`
	TransactionID   string            `json:"transactionId"`
}

// ConsentRecord represents a consent record
type ConsentRecord struct {
	ID              string    `json:"id"`
	PatientID       string    `json:"patientId"`
	ProviderID      string    `json:"providerId"`
	ConsentType     string    `json:"consentType"`
	Granted         bool      `json:"granted"`
	Timestamp       time.Time `json:"timestamp"`
	ExpiryDate      time.Time `json:"expiryDate"`
	Scope           string    `json:"scope"`
	Revoked         bool      `json:"revoked"`
	RevokedAt       time.Time `json:"revokedAt"`
	RevokedBy       string    `json:"revokedBy"`
	TransactionID   string    `json:"transactionId"`
}

// AuditLog represents an audit log entry
type AuditLog struct {
	ID            string    `json:"id"`
	Action        string    `json:"action"`
	UserID        string    `json:"userId"`
	ResourceID    string    `json:"resourceId"`
	ResourceType  string    `json:"resourceType"`
	Timestamp     time.Time `json:"timestamp"`
	Details       string    `json:"details"`
	IPAddress     string    `json:"ipAddress"`
	UserAgent     string    `json:"userAgent"`
	TransactionID string    `json:"transactionId"`
}

// CreateHealthRecord creates a new health record
func (c *HealthRecordContract) CreateHealthRecord(ctx contractapi.TransactionContextInterface, 
	patientID, providerID, recordType, data, hash string, consentGranted bool, metadata map[string]string) error {
	
	// Get transaction details
	txID := ctx.GetStub().GetTxID()
	timestamp := time.Now()
	
	// Create health record
	record := HealthRecord{
		ID:             fmt.Sprintf("HR_%s_%d", patientID, timestamp.Unix()),
		PatientID:      patientID,
		ProviderID:     providerID,
		RecordType:     recordType,
		Data:           data,
		Hash:           hash,
		Timestamp:      timestamp,
		ConsentGranted: consentGranted,
		AccessControl:  make(map[string]bool),
		Metadata:       metadata,
		Version:        1,
		TransactionID:  txID,
	}
	
	// Get previous record for chain linking
	prevRecord, err := c.GetLatestHealthRecord(ctx, patientID, recordType)
	if err == nil && prevRecord != nil {
		record.PreviousHash = prevRecord.Hash
		record.Version = prevRecord.Version + 1
	}
	
	// Store the record
	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal health record: %v", err)
	}
	
	err = ctx.GetStub().PutState(record.ID, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to store health record: %v", err)
	}
	
	// Create audit log
	auditLog := AuditLog{
		ID:            fmt.Sprintf("AUDIT_%s", txID),
		Action:        "CREATE_HEALTH_RECORD",
		UserID:        providerID,
		ResourceID:    record.ID,
		ResourceType:  "HEALTH_RECORD",
		Timestamp:     timestamp,
		Details:       fmt.Sprintf("Created health record for patient %s, type: %s", patientID, recordType),
		TransactionID: txID,
	}
	
	auditJSON, err := json.Marshal(auditLog)
	if err != nil {
		return fmt.Errorf("failed to marshal audit log: %v", err)
	}
	
	err = ctx.GetStub().PutState(auditLog.ID, auditJSON)
	if err != nil {
		return fmt.Errorf("failed to store audit log: %v", err)
	}
	
	return nil
}

// GetHealthRecord retrieves a health record by ID
func (c *HealthRecordContract) GetHealthRecord(ctx contractapi.TransactionContextInterface, recordID string) (*HealthRecord, error) {
	recordJSON, err := ctx.GetStub().GetState(recordID)
	if err != nil {
		return nil, fmt.Errorf("failed to read health record: %v", err)
	}
	if recordJSON == nil {
		return nil, fmt.Errorf("health record not found: %s", recordID)
	}
	
	var record HealthRecord
	err = json.Unmarshal(recordJSON, &record)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal health record: %v", err)
	}
	
	return &record, nil
}

// GetLatestHealthRecord gets the latest health record for a patient and record type
func (c *HealthRecordContract) GetLatestHealthRecord(ctx contractapi.TransactionContextInterface, patientID, recordType string) (*HealthRecord, error) {
	// This would typically use a composite key or query
	// For simplicity, we'll return nil for now
	return nil, nil
}

// UpdateHealthRecord updates an existing health record
func (c *HealthRecordContract) UpdateHealthRecord(ctx contractapi.TransactionContextInterface, 
	recordID, data, hash string, metadata map[string]string) error {
	
	// Get existing record
	record, err := c.GetHealthRecord(ctx, recordID)
	if err != nil {
		return err
	}
	
	// Update record
	record.Data = data
	record.Hash = hash
	record.Timestamp = time.Now()
	record.Version++
	record.TransactionID = ctx.GetStub().GetTxID()
	
	if metadata != nil {
		record.Metadata = metadata
	}
	
	// Store updated record
	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal updated health record: %v", err)
	}
	
	err = ctx.GetStub().PutState(recordID, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to update health record: %v", err)
	}
	
	// Create audit log
	auditLog := AuditLog{
		ID:            fmt.Sprintf("AUDIT_%s", ctx.GetStub().GetTxID()),
		Action:        "UPDATE_HEALTH_RECORD",
		UserID:        record.ProviderID,
		ResourceID:    recordID,
		ResourceType:  "HEALTH_RECORD",
		Timestamp:     time.Now(),
		Details:       fmt.Sprintf("Updated health record %s, version: %d", recordID, record.Version),
		TransactionID: ctx.GetStub().GetTxID(),
	}
	
	auditJSON, err := json.Marshal(auditLog)
	if err != nil {
		return fmt.Errorf("failed to marshal audit log: %v", err)
	}
	
	err = ctx.GetStub().PutState(auditLog.ID, auditJSON)
	if err != nil {
		return fmt.Errorf("failed to store audit log: %v", err)
	}
	
	return nil
}

// GrantConsent grants consent for a health record
func (c *HealthRecordContract) GrantConsent(ctx contractapi.TransactionContextInterface, 
	patientID, providerID, consentType, scope string, expiryDate time.Time) error {
	
	consentRecord := ConsentRecord{
		ID:            fmt.Sprintf("CONSENT_%s_%s_%d", patientID, providerID, time.Now().Unix()),
		PatientID:     patientID,
		ProviderID:    providerID,
		ConsentType:   consentType,
		Granted:       true,
		Timestamp:     time.Now(),
		ExpiryDate:    expiryDate,
		Scope:         scope,
		Revoked:       false,
		TransactionID: ctx.GetStub().GetTxID(),
	}
	
	consentJSON, err := json.Marshal(consentRecord)
	if err != nil {
		return fmt.Errorf("failed to marshal consent record: %v", err)
	}
	
	err = ctx.GetStub().PutState(consentRecord.ID, consentJSON)
	if err != nil {
		return fmt.Errorf("failed to store consent record: %v", err)
	}
	
	// Create audit log
	auditLog := AuditLog{
		ID:            fmt.Sprintf("AUDIT_%s", ctx.GetStub().GetTxID()),
		Action:        "GRANT_CONSENT",
		UserID:        patientID,
		ResourceID:    consentRecord.ID,
		ResourceType:  "CONSENT",
		Timestamp:     time.Now(),
		Details:       fmt.Sprintf("Granted consent to provider %s for scope: %s", providerID, scope),
		TransactionID: ctx.GetStub().GetTxID(),
	}
	
	auditJSON, err := json.Marshal(auditLog)
	if err != nil {
		return fmt.Errorf("failed to marshal audit log: %v", err)
	}
	
	err = ctx.GetStub().PutState(auditLog.ID, auditJSON)
	if err != nil {
		return fmt.Errorf("failed to store audit log: %v", err)
	}
	
	return nil
}

// RevokeConsent revokes consent for a health record
func (c *HealthRecordContract) RevokeConsent(ctx contractapi.TransactionContextInterface, consentID, revokedBy string) error {
	consentJSON, err := ctx.GetStub().GetState(consentID)
	if err != nil {
		return fmt.Errorf("failed to read consent record: %v", err)
	}
	if consentJSON == nil {
		return fmt.Errorf("consent record not found: %s", consentID)
	}
	
	var consent ConsentRecord
	err = json.Unmarshal(consentJSON, &consent)
	if err != nil {
		return fmt.Errorf("failed to unmarshal consent record: %v", err)
	}
	
	consent.Revoked = true
	consent.RevokedAt = time.Now()
	consent.RevokedBy = revokedBy
	
	consentJSON, err = json.Marshal(consent)
	if err != nil {
		return fmt.Errorf("failed to marshal updated consent record: %v", err)
	}
	
	err = ctx.GetStub().PutState(consentID, consentJSON)
	if err != nil {
		return fmt.Errorf("failed to update consent record: %v", err)
	}
	
	// Create audit log
	auditLog := AuditLog{
		ID:            fmt.Sprintf("AUDIT_%s", ctx.GetStub().GetTxID()),
		Action:        "REVOKE_CONSENT",
		UserID:        revokedBy,
		ResourceID:    consentID,
		ResourceType:  "CONSENT",
		Timestamp:     time.Now(),
		Details:       fmt.Sprintf("Revoked consent %s by %s", consentID, revokedBy),
		TransactionID: ctx.GetStub().GetTxID(),
	}
	
	auditJSON, err := json.Marshal(auditLog)
	if err != nil {
		return fmt.Errorf("failed to marshal audit log: %v", err)
	}
	
	err = ctx.GetStub().PutState(auditLog.ID, auditJSON)
	if err != nil {
		return fmt.Errorf("failed to store audit log: %v", err)
	}
	
	return nil
}

// VerifyDataIntegrity verifies the integrity of a health record
func (c *HealthRecordContract) VerifyDataIntegrity(ctx contractapi.TransactionContextInterface, recordID string) (bool, error) {
	record, err := c.GetHealthRecord(ctx, recordID)
	if err != nil {
		return false, err
	}
	
	// In a real implementation, you would verify the hash against the data
	// For now, we'll return true if the record exists
	return record != nil, nil
}

// GetAuditTrail retrieves the audit trail for a resource
func (c *HealthRecordContract) GetAuditTrail(ctx contractapi.TransactionContextInterface, resourceID string) ([]AuditLog, error) {
	// This would typically use a query to get all audit logs for a resource
	// For simplicity, we'll return an empty slice
	return []AuditLog{}, nil
}

// GetConsentStatus checks if consent is granted for a patient-provider pair
func (c *HealthRecordContract) GetConsentStatus(ctx contractapi.TransactionContextInterface, patientID, providerID string) (bool, error) {
	// This would typically query consent records
	// For simplicity, we'll return true
	return true, nil
} 