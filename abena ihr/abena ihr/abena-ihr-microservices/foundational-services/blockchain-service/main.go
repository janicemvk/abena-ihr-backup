package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/gateway"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"github.com/redis/go-redis/v9"
	"github.com/golang-jwt/jwt/v5"
)

// Configuration
type Config struct {
	Port             string
	MongoURL         string
	RedisURL         string
	AuthServiceURL   string
	FabricConfigPath string
	ChannelName      string
	ChaincodeName    string
	Organization     string
	UserName         string
}

// Health record structure
type HealthRecord struct {
	ID                string                 `json:"id" bson:"_id"`
	PatientID         string                 `json:"patient_id" bson:"patient_id"`
	ProviderID        string                 `json:"provider_id" bson:"provider_id"`
	RecordType        string                 `json:"record_type" bson:"record_type"`
	DataHash          string                 `json:"data_hash" bson:"data_hash"`
	Timestamp         time.Time              `json:"timestamp" bson:"timestamp"`
	BlockchainTxID    string                 `json:"blockchain_tx_id" bson:"blockchain_tx_id"`
	ConsentHash       string                 `json:"consent_hash" bson:"consent_hash"`
	AccessLog         []AccessLogEntry       `json:"access_log" bson:"access_log"`
	Metadata          map[string]interface{} `json:"metadata" bson:"metadata"`
	Version           int                    `json:"version" bson:"version"`
	PreviousHash      string                 `json:"previous_hash" bson:"previous_hash"`
	IsDeleted         bool                   `json:"is_deleted" bson:"is_deleted"`
	CreatedAt         time.Time              `json:"created_at" bson:"created_at"`
	UpdatedAt         time.Time              `json:"updated_at" bson:"updated_at"`
}

// Access log entry
type AccessLogEntry struct {
	UserID         string                 `json:"user_id" bson:"user_id"`
	Action         string                 `json:"action" bson:"action"`
	Timestamp      time.Time              `json:"timestamp" bson:"timestamp"`
	IPAddress      string                 `json:"ip_address" bson:"ip_address"`
	ConsentGiven   bool                   `json:"consent_given" bson:"consent_given"`
	Purpose        string                 `json:"purpose" bson:"purpose"`
	DataAccessed   []string               `json:"data_accessed" bson:"data_accessed"`
	AdditionalData map[string]interface{} `json:"additional_data" bson:"additional_data"`
}

// Smart contract transaction
type Transaction struct {
	ID           string                 `json:"id"`
	Type         string                 `json:"type"`
	PatientID    string                 `json:"patient_id"`
	ProviderID   string                 `json:"provider_id"`
	DataHash     string                 `json:"data_hash"`
	ConsentHash  string                 `json:"consent_hash"`
	Timestamp    time.Time              `json:"timestamp"`
	Signature    string                 `json:"signature"`
	Metadata     map[string]interface{} `json:"metadata"`
	PreviousHash string                 `json:"previous_hash"`
	Nonce        int64                  `json:"nonce"`
}

// Consensus vote
type ConsensusVote struct {
	NodeID      string    `json:"node_id"`
	TxID        string    `json:"tx_id"`
	Vote        bool      `json:"vote"`
	Timestamp   time.Time `json:"timestamp"`
	Signature   string    `json:"signature"`
	Reasoning   string    `json:"reasoning"`
}

// Smart contract interface
type SmartContract struct {
	gateway  *gateway.Gateway
	network  *gateway.Network
	contract *gateway.Contract
}

// Service structure
type BlockchainService struct {
	config       *Config
	router       *gin.Engine
	mongoClient  *mongo.Client
	redisClient  *redis.Client
	smartContract *SmartContract
}

// Request/Response structures
type CreateRecordRequest struct {
	PatientID   string                 `json:"patient_id" binding:"required"`
	ProviderID  string                 `json:"provider_id" binding:"required"`
	RecordType  string                 `json:"record_type" binding:"required"`
	DataHash    string                 `json:"data_hash" binding:"required"`
	ConsentHash string                 `json:"consent_hash" binding:"required"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type UpdateRecordRequest struct {
	DataHash    string                 `json:"data_hash" binding:"required"`
	ConsentHash string                 `json:"consent_hash"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type AccessRecordRequest struct {
	Purpose      string   `json:"purpose" binding:"required"`
	DataFields   []string `json:"data_fields"`
	Emergency    bool     `json:"emergency"`
	ConsentToken string   `json:"consent_token"`
}

type ConsentRequest struct {
	PatientID    string    `json:"patient_id" binding:"required"`
	ProviderID   string    `json:"provider_id" binding:"required"`
	Purpose      string    `json:"purpose" binding:"required"`
	DataTypes    []string  `json:"data_types" binding:"required"`
	Granted      bool      `json:"granted" binding:"required"`
	ExpiresAt    time.Time `json:"expires_at"`
	Conditions   []string  `json:"conditions"`
}

// Initialize configuration
func loadConfig() *Config {
	return &Config{
		Port:             getEnv("PORT", "8003"),
		MongoURL:         getEnv("MONGO_URL", "mongodb://localhost:27017"),
		RedisURL:         getEnv("REDIS_URL", "redis://localhost:6379"),
		AuthServiceURL:   getEnv("AUTH_SERVICE_URL", "http://localhost:3001"),
		FabricConfigPath: getEnv("FABRIC_CONFIG_PATH", "./config/connection.yaml"),
		ChannelName:      getEnv("CHANNEL_NAME", "healthchannel"),
		ChaincodeName:    getEnv("CHAINCODE_NAME", "healthrecords"),
		Organization:     getEnv("ORGANIZATION", "Org1MSP"),
		UserName:         getEnv("USER_NAME", "User1"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Initialize blockchain service
func NewBlockchainService(config *Config) (*BlockchainService, error) {
	service := &BlockchainService{
		config: config,
		router: gin.Default(),
	}

	// Initialize MongoDB
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(config.MongoURL))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %v", err)
	}
	service.mongoClient = client

	// Initialize Redis
	opt, err := redis.ParseURL(config.RedisURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse Redis URL: %v", err)
	}
	service.redisClient = redis.NewClient(opt)

	// Test Redis connection
	_, err = service.redisClient.Ping(context.Background()).Result()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %v", err)
	}

	// Initialize Hyperledger Fabric connection
	err = service.initFabricConnection()
	if err != nil {
		log.Printf("Warning: Failed to initialize Fabric connection: %v", err)
		// Continue without Fabric for development
	}

	// Setup routes
	service.setupRoutes()

	return service, nil
}

// Initialize Hyperledger Fabric connection
func (s *BlockchainService) initFabricConnection() error {
	// Load connection profile
	gw, err := gateway.Connect(
		gateway.WithConfig(config.FromFile(s.config.FabricConfigPath)),
		gateway.WithIdentity(s.config.UserName),
	)
	if err != nil {
		return fmt.Errorf("failed to connect to gateway: %v", err)
	}

	network, err := gw.GetNetwork(s.config.ChannelName)
	if err != nil {
		return fmt.Errorf("failed to get network: %v", err)
	}

	contract := network.GetContract(s.config.ChaincodeName)

	s.smartContract = &SmartContract{
		gateway:  gw,
		network:  network,
		contract: contract,
	}

	log.Println("Successfully connected to Hyperledger Fabric network")
	return nil
}

// Setup API routes
func (s *BlockchainService) setupRoutes() {
	// Middleware
	s.router.Use(s.corsMiddleware())
	s.router.Use(gin.Logger())
	s.router.Use(gin.Recovery())

	// Health check
	s.router.GET("/health", s.healthCheck)

	// Authentication middleware for protected routes
	protected := s.router.Group("/")
	protected.Use(s.authMiddleware())

	// Health records endpoints
	protected.POST("/records", s.createRecord)
	protected.GET("/records/:id", s.getRecord)
	protected.PUT("/records/:id", s.updateRecord)
	protected.DELETE("/records/:id", s.deleteRecord)
	protected.POST("/records/:id/access", s.accessRecord)

	// Patient records
	protected.GET("/patients/:patient_id/records", s.getPatientRecords)
	protected.GET("/patients/:patient_id/audit", s.getPatientAudit)

	// Consent management
	protected.POST("/consent", s.createConsent)
	protected.GET("/consent/:patient_id/:provider_id", s.getConsent)
	protected.PUT("/consent/:id", s.updateConsent)

	// Blockchain operations
	protected.GET("/blockchain/verify/:tx_id", s.verifyTransaction)
	protected.GET("/blockchain/audit/:record_id", s.getBlockchainAudit)
	protected.POST("/blockchain/consensus", s.submitConsensusVote)

	// Analytics and reporting
	protected.GET("/analytics/usage", s.getUsageAnalytics)
	protected.GET("/analytics/compliance", s.getComplianceReport)
}

// Middleware functions
func (s *BlockchainService) corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func (s *BlockchainService) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(401, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		// Extract token from "Bearer <token>"
		if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
			c.JSON(401, gin.H{"error": "Invalid authorization header format"})
			c.Abort()
			return
		}

		tokenString := authHeader[7:]

		// Verify token with auth service (simplified for demo)
		user, err := s.verifyTokenWithAuthService(tokenString)
		if err != nil {
			c.JSON(401, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		// Set user context
		c.Set("user", user)
		c.Next()
	}
}

// Health check endpoint
func (s *BlockchainService) healthCheck(c *gin.Context) {
	status := gin.H{
		"status":    "healthy",
		"service":   "Abena IHR Blockchain Service",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"version":   "1.0.0",
	}

	// Check database connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	err := s.mongoClient.Ping(ctx, nil)
	if err != nil {
		status["mongodb"] = "unhealthy"
		status["status"] = "degraded"
	} else {
		status["mongodb"] = "healthy"
	}

	// Check Redis connection
	_, err = s.redisClient.Ping(context.Background()).Result()
	if err != nil {
		status["redis"] = "unhealthy"
		status["status"] = "degraded"
	} else {
		status["redis"] = "healthy"
	}

	// Check Fabric connection
	if s.smartContract != nil {
		status["fabric"] = "healthy"
	} else {
		status["fabric"] = "unavailable"
	}

	c.JSON(200, status)
}

// Create health record
func (s *BlockchainService) createRecord(c *gin.Context) {
	var req CreateRecordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	user := s.getUserFromContext(c)
	if user == nil {
		c.JSON(401, gin.H{"error": "User not found in context"})
		return
	}

	// Check if user has permission to create records for this patient
	if !s.hasPatientAccess(user["id"].(string), req.PatientID, "create") {
		c.JSON(403, gin.H{"error": "Insufficient permissions"})
		return
	}

	// Create health record
	record := &HealthRecord{
		ID:            generateID(),
		PatientID:     req.PatientID,
		ProviderID:    req.ProviderID,
		RecordType:    req.RecordType,
		DataHash:      req.DataHash,
		Timestamp:     time.Now().UTC(),
		ConsentHash:   req.ConsentHash,
		AccessLog:     []AccessLogEntry{},
		Metadata:      req.Metadata,
		Version:       1,
		PreviousHash:  "",
		IsDeleted:     false,
		CreatedAt:     time.Now().UTC(),
		UpdatedAt:     time.Now().UTC(),
	}

	// Calculate previous hash
	previousRecord, err := s.getLatestRecordForPatient(req.PatientID)
	if err == nil && previousRecord != nil {
		record.PreviousHash = previousRecord.DataHash
	}

	// Submit to blockchain
	txID, err := s.submitToBlockchain(record)
	if err != nil {
		log.Printf("Failed to submit to blockchain: %v", err)
		// Continue without blockchain for development
	} else {
		record.BlockchainTxID = txID
	}

	// Store in MongoDB
	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, err = collection.InsertOne(ctx, record)
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to store record"})
		return
	}

	// Log access
	s.logAccess(record.ID, user["id"].(string), "CREATE", c.ClientIP(), true, "Record creation", []string{})

	c.JSON(201, gin.H{
		"record_id":       record.ID,
		"blockchain_tx_id": record.BlockchainTxID,
		"timestamp":       record.Timestamp,
		"success":         true,
	})
}

// Get health record
func (s *BlockchainService) getRecord(c *gin.Context) {
	recordID := c.Param("id")
	user := s.getUserFromContext(c)
	if user == nil {
		c.JSON(401, gin.H{"error": "User not found in context"})
		return
	}

	// Get record from database
	record, err := s.getRecordByID(recordID)
	if err != nil {
		c.JSON(404, gin.H{"error": "Record not found"})
		return
	}

	// Check access permissions
	if !s.hasPatientAccess(user["id"].(string), record.PatientID, "read") {
		c.JSON(403, gin.H{"error": "Insufficient permissions"})
		return
	}

	// Log access
	s.logAccess(recordID, user["id"].(string), "READ", c.ClientIP(), true, "Record retrieval", []string{})

	// Verify blockchain integrity
	isValid := true
	if record.BlockchainTxID != "" {
		isValid, err = s.verifyBlockchainIntegrity(record.BlockchainTxID, record.DataHash)
		if err != nil {
			log.Printf("Failed to verify blockchain integrity: %v", err)
		}
	}

	c.JSON(200, gin.H{
		"record":           record,
		"blockchain_valid": isValid,
		"success":          true,
	})
}

// Update health record
func (s *BlockchainService) updateRecord(c *gin.Context) {
	recordID := c.Param("id")
	var req UpdateRecordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	user := s.getUserFromContext(c)
	if user == nil {
		c.JSON(401, gin.H{"error": "User not found in context"})
		return
	}

	// Get existing record
	record, err := s.getRecordByID(recordID)
	if err != nil {
		c.JSON(404, gin.H{"error": "Record not found"})
		return
	}

	// Check permissions
	if !s.hasPatientAccess(user["id"].(string), record.PatientID, "update") {
		c.JSON(403, gin.H{"error": "Insufficient permissions"})
		return
	}

	// Update record
	record.DataHash = req.DataHash
	if req.ConsentHash != "" {
		record.ConsentHash = req.ConsentHash
	}
	if req.Metadata != nil {
		record.Metadata = req.Metadata
	}
	record.Version++
	record.UpdatedAt = time.Now().UTC()

	// Submit update to blockchain
	txID, err := s.submitToBlockchain(record)
	if err != nil {
		log.Printf("Failed to submit update to blockchain: %v", err)
	} else {
		record.BlockchainTxID = txID
	}

	// Update in database
	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	filter := bson.M{"_id": recordID}
	update := bson.M{"$set": record}
	_, err = collection.UpdateOne(ctx, filter, update)
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to update record"})
		return
	}

	// Log access
	s.logAccess(recordID, user["id"].(string), "UPDATE", c.ClientIP(), true, "Record update", []string{})

	c.JSON(200, gin.H{
		"record_id":        record.ID,
		"blockchain_tx_id": record.BlockchainTxID,
		"version":          record.Version,
		"success":          true,
	})
}

// Access record (with detailed logging)
func (s *BlockchainService) accessRecord(c *gin.Context) {
	recordID := c.Param("id")
	var req AccessRecordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	user := s.getUserFromContext(c)
	if user == nil {
		c.JSON(401, gin.H{"error": "User not found in context"})
		return
	}

	// Get record
	record, err := s.getRecordByID(recordID)
	if err != nil {
		c.JSON(404, gin.H{"error": "Record not found"})
		return
	}

	// Check consent
	hasConsent := true
	if !req.Emergency {
		hasConsent, err = s.checkConsent(record.PatientID, user["id"].(string), req.Purpose)
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to check consent"})
			return
		}
	}

	if !hasConsent && !req.Emergency {
		c.JSON(403, gin.H{"error": "Patient consent required"})
		return
	}

	// Log detailed access
	accessEntry := AccessLogEntry{
		UserID:       user["id"].(string),
		Action:       "ACCESS",
		Timestamp:    time.Now().UTC(),
		IPAddress:    c.ClientIP(),
		ConsentGiven: hasConsent,
		Purpose:      req.Purpose,
		DataAccessed: req.DataFields,
		AdditionalData: map[string]interface{}{
			"emergency": req.Emergency,
			"user_role": user["role"],
		},
	}

	// Add to record's access log
	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	filter := bson.M{"_id": recordID}
	update := bson.M{"$push": bson.M{"access_log": accessEntry}}
	_, err = collection.UpdateOne(ctx, filter, update)
	if err != nil {
		log.Printf("Failed to update access log: %v", err)
	}

	c.JSON(200, gin.H{
		"access_granted": true,
		"consent_given":  hasConsent,
		"emergency":      req.Emergency,
		"timestamp":      accessEntry.Timestamp,
		"success":        true,
	})
}

// Helper functions
func (s *BlockchainService) getUserFromContext(c *gin.Context) map[string]interface{} {
	user, exists := c.Get("user")
	if !exists {
		return nil
	}
	return user.(map[string]interface{})
}

func (s *BlockchainService) hasPatientAccess(userID, patientID, action string) bool {
	// Simplified access check - in production, this would check the auth service
	// For now, assume all authenticated users have access
	return true
}

func (s *BlockchainService) getRecordByID(recordID string) (*HealthRecord, error) {
	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var record HealthRecord
	err := collection.FindOne(ctx, bson.M{"_id": recordID}).Decode(&record)
	if err != nil {
		return nil, err
	}
	return &record, nil
}

func (s *BlockchainService) getLatestRecordForPatient(patientID string) (*HealthRecord, error) {
	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	opts := options.FindOne().SetSort(bson.D{{"created_at", -1}})
	var record HealthRecord
	err := collection.FindOne(ctx, bson.M{"patient_id": patientID}, opts).Decode(&record)
	if err != nil {
		return nil, err
	}
	return &record, nil
}

func (s *BlockchainService) submitToBlockchain(record *HealthRecord) (string, error) {
	if s.smartContract == nil {
		return "", fmt.Errorf("blockchain connection not available")
	}

	// Create transaction for smart contract
	tx := &Transaction{
		ID:           record.ID,
		Type:         "HEALTH_RECORD",
		PatientID:    record.PatientID,
		ProviderID:   record.ProviderID,
		DataHash:     record.DataHash,
		ConsentHash:  record.ConsentHash,
		Timestamp:    record.Timestamp,
		PreviousHash: record.PreviousHash,
		Metadata:     record.Metadata,
		Nonce:        time.Now().UnixNano(),
	}

	// Convert to JSON
	txJSON, err := json.Marshal(tx)
	if err != nil {
		return "", err
	}

	// Submit transaction to chaincode
	result, err := s.smartContract.contract.SubmitTransaction("CreateHealthRecord", string(txJSON))
	if err != nil {
		return "", err
	}

	return string(result), nil
}

func (s *BlockchainService) verifyBlockchainIntegrity(txID, dataHash string) (bool, error) {
	if s.smartContract == nil {
		return false, fmt.Errorf("blockchain connection not available")
	}

	// Query blockchain for transaction
	result, err := s.smartContract.contract.EvaluateTransaction("GetTransaction", txID)
	if err != nil {
		return false, err
	}

	var storedTx Transaction
	err = json.Unmarshal(result, &storedTx)
	if err != nil {
		return false, err
	}

	// Verify data hash matches
	return storedTx.DataHash == dataHash, nil
}

func (s *BlockchainService) checkConsent(patientID, providerID, purpose string) (bool, error) {
	// Check consent in database or blockchain
	collection := s.mongoClient.Database("abena_ihr").Collection("consents")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	filter := bson.M{
		"patient_id":  patientID,
		"provider_id": providerID,
		"purpose":     purpose,
		"granted":     true,
		"expires_at":  bson.M{"$gt": time.Now().UTC()},
	}

	count, err := collection.CountDocuments(ctx, filter)
	if err != nil {
		return false, err
	}

	return count > 0, nil
}

func (s *BlockchainService) logAccess(recordID, userID, action, ipAddress string, success bool, purpose string, dataFields []string) {
	// Log to access audit collection
	collection := s.mongoClient.Database("abena_ihr").Collection("access_audit")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	logEntry := AccessLogEntry{
		UserID:       userID,
		Action:       action,
		Timestamp:    time.Now().UTC(),
		IPAddress:    ipAddress,
		ConsentGiven: success,
		Purpose:      purpose,
		DataAccessed: dataFields,
		AdditionalData: map[string]interface{}{
			"record_id": recordID,
			"success":   success,
		},
	}

	_, err := collection.InsertOne(ctx, logEntry)
	if err != nil {
		log.Printf("Failed to log access: %v", err)
	}
}

func (s *BlockchainService) verifyTokenWithAuthService(token string) (map[string]interface{}, error) {
	// Simplified token verification - in production, this would call the auth service
	// For now, just parse the JWT token (assuming it's valid)
	claims := jwt.MapClaims{}
	_, err := jwt.ParseWithClaims(token, claims, func(token *jwt.Token) (interface{}, error) {
		return []byte("your-secret-key"), nil // This should match the auth service secret
	})
	
	if err != nil {
		return nil, err
	}

	user := map[string]interface{}{
		"id":    claims["userId"],
		"email": claims["email"],
		"role":  claims["role"],
	}

	return user, nil
}

// Additional endpoints
func (s *BlockchainService) getPatientRecords(c *gin.Context) {
	patientID := c.Param("patient_id")
	user := s.getUserFromContext(c)
	
	if !s.hasPatientAccess(user["id"].(string), patientID, "read") {
		c.JSON(403, gin.H{"error": "Insufficient permissions"})
		return
	}

	collection := s.mongoClient.Database("abena_ihr").Collection("health_records")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	cursor, err := collection.Find(ctx, bson.M{"patient_id": patientID, "is_deleted": false})
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to retrieve records"})
		return
	}
	defer cursor.Close(ctx)

	var records []HealthRecord
	if err = cursor.All(ctx, &records); err != nil {
		c.JSON(500, gin.H{"error": "Failed to decode records"})
		return
	}

	c.JSON(200, gin.H{
		"records": records,
		"count":   len(records),
		"success": true,
	})
}

func (s *BlockchainService) createConsent(c *gin.Context) {
	var req ConsentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	consent := bson.M{
		"_id":        generateID(),
		"patient_id": req.PatientID,
		"provider_id": req.ProviderID,
		"purpose":    req.Purpose,
		"data_types": req.DataTypes,
		"granted":    req.Granted,
		"expires_at": req.ExpiresAt,
		"conditions": req.Conditions,
		"created_at": time.Now().UTC(),
		"updated_at": time.Now().UTC(),
	}

	collection := s.mongoClient.Database("abena_ihr").Collection("consents")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, err := collection.InsertOne(ctx, consent)
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to create consent"})
		return
	}

	c.JSON(201, gin.H{
		"consent_id": consent["_id"],
		"success":    true,
	})
}

func (s *BlockchainService) verifyTransaction(c *gin.Context) {
	txID := c.Param("tx_id")

	if s.smartContract == nil {
		c.JSON(503, gin.H{"error": "Blockchain service unavailable"})
		return
	}

	result, err := s.smartContract.contract.EvaluateTransaction("GetTransaction", txID)
	if err != nil {
		c.JSON(404, gin.H{"error": "Transaction not found"})
		return
	}

	var tx Transaction
	err = json.Unmarshal(result, &tx)
	if err != nil {
		c.JSON(500, gin.H{"error": "Failed to parse transaction"})
		return
	}

	c.JSON(200, gin.H{
		"transaction": tx,
		"verified":    true,
		"success":     true,
	})
}

// Utility functions
func generateID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}

func hashString(data string) string {
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])
}

// Additional endpoints would be implemented here...

// Main function
func main() {
	config := loadConfig()
	
	service, err := NewBlockchainService(config)
	if err != nil {
		log.Fatalf("Failed to initialize blockchain service: %v", err)
	}

	log.Printf("🔗 Abena IHR Blockchain Service starting on port %s", config.Port)
	
	if err := service.router.Run(":" + config.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
} 