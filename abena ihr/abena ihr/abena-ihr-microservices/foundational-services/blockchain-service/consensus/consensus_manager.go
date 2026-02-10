package consensus

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/hyperledger/fabric-protos-go/peer"
)

// ConsensusType represents the type of consensus algorithm
type ConsensusType string

const (
	// Raft consensus for Hyperledger Fabric
	RaftConsensus ConsensusType = "raft"
	// Practical Byzantine Fault Tolerance
	PBFT ConsensusType = "pbft"
	// Proof of Authority
	PoA ConsensusType = "poa"
	// Proof of Stake
	PoS ConsensusType = "pos"
)

// ConsensusManager manages consensus operations
type ConsensusManager struct {
	consensusType ConsensusType
	peers         map[string]*Peer
	mu            sync.RWMutex
	blockHeight   uint64
	lastBlockHash string
	config        *ConsensusConfig
}

// Peer represents a network peer
type Peer struct {
	ID       string    `json:"id"`
	Address  string    `json:"address"`
	Port     int       `json:"port"`
	PublicKey string   `json:"publicKey"`
	Stake    float64   `json:"stake"`
	IsActive bool      `json:"isActive"`
	LastSeen time.Time `json:"lastSeen"`
}

// ConsensusConfig holds consensus configuration
type ConsensusConfig struct {
	Type                    ConsensusType `json:"type"`
	BlockTime               time.Duration `json:"blockTime"`
	MaxBlockSize            int           `json:"maxBlockSize"`
	MinPeers                int           `json:"minPeers"`
	FaultToleranceThreshold int           `json:"faultToleranceThreshold"`
	StakeRequirement        float64       `json:"stakeRequirement"`
	ConsensusTimeout        time.Duration `json:"consensusTimeout"`
}

// Block represents a blockchain block
type Block struct {
	Header       *BlockHeader `json:"header"`
	Transactions []*Transaction `json:"transactions"`
	Hash         string       `json:"hash"`
	PreviousHash string       `json:"previousHash"`
	Timestamp    time.Time    `json:"timestamp"`
	MerkleRoot   string       `json:"merkleRoot"`
	Nonce        uint64       `json:"nonce"`
	Difficulty   uint64       `json:"difficulty"`
}

// BlockHeader contains block metadata
type BlockHeader struct {
	Version       int       `json:"version"`
	BlockNumber   uint64    `json:"blockNumber"`
	Timestamp     time.Time `json:"timestamp"`
	PreviousHash  string    `json:"previousHash"`
	MerkleRoot    string    `json:"merkleRoot"`
	Nonce         uint64    `json:"nonce"`
	Difficulty    uint64    `json:"difficulty"`
	ConsensusType string    `json:"consensusType"`
	Validator     string    `json:"validator"`
}

// Transaction represents a blockchain transaction
type Transaction struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`
	Data        map[string]interface{} `json:"data"`
	Hash        string                 `json:"hash"`
	Timestamp   time.Time              `json:"timestamp"`
	From        string                 `json:"from"`
	To          string                 `json:"to"`
	Signature   string                 `json:"signature"`
	PublicKey   string                 `json:"publicKey"`
	Nonce       uint64                 `json:"nonce"`
	GasLimit    uint64                 `json:"gasLimit"`
	GasPrice    uint64                 `json:"gasPrice"`
	BlockNumber uint64                 `json:"blockNumber"`
}

// ConsensusMessage represents a consensus message
type ConsensusMessage struct {
	Type      string      `json:"type"`
	Block     *Block      `json:"block,omitempty"`
	Transaction *Transaction `json:"transaction,omitempty"`
	From      string      `json:"from"`
	To        string      `json:"to"`
	Timestamp time.Time   `json:"timestamp"`
	Signature string      `json:"signature"`
	Round     uint64      `json:"round"`
	Sequence  uint64      `json:"sequence"`
}

// NewConsensusManager creates a new consensus manager
func NewConsensusManager(config *ConsensusConfig) *ConsensusManager {
	return &ConsensusManager{
		consensusType: config.Type,
		peers:         make(map[string]*Peer),
		config:        config,
		blockHeight:   0,
		lastBlockHash: "",
	}
}

// AddPeer adds a new peer to the network
func (cm *ConsensusManager) AddPeer(peer *Peer) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()
	
	if _, exists := cm.peers[peer.ID]; exists {
		return fmt.Errorf("peer %s already exists", peer.ID)
	}
	
	cm.peers[peer.ID] = peer
	return nil
}

// RemovePeer removes a peer from the network
func (cm *ConsensusManager) RemovePeer(peerID string) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()
	
	if _, exists := cm.peers[peerID]; !exists {
		return fmt.Errorf("peer %s does not exist", peerID)
	}
	
	delete(cm.peers, peerID)
	return nil
}

// GetActivePeers returns all active peers
func (cm *ConsensusManager) GetActivePeers() []*Peer {
	cm.mu.RLock()
	defer cm.mu.RUnlock()
	
	var activePeers []*Peer
	for _, peer := range cm.peers {
		if peer.IsActive {
			activePeers = append(activePeers, peer)
		}
	}
	return activePeers
}

// CreateBlock creates a new block with transactions
func (cm *ConsensusManager) CreateBlock(transactions []*Transaction, validator string) (*Block, error) {
	if len(transactions) == 0 {
		return nil, fmt.Errorf("no transactions to include in block")
	}
	
	// Calculate Merkle root
	merkleRoot := cm.calculateMerkleRoot(transactions)
	
	// Create block header
	header := &BlockHeader{
		Version:       1,
		BlockNumber:   cm.blockHeight + 1,
		Timestamp:     time.Now(),
		PreviousHash:  cm.lastBlockHash,
		MerkleRoot:    merkleRoot,
		Nonce:         0,
		Difficulty:    cm.calculateDifficulty(),
		ConsensusType: string(cm.consensusType),
		Validator:     validator,
	}
	
	// Create block
	block := &Block{
		Header:       header,
		Transactions: transactions,
		PreviousHash: cm.lastBlockHash,
		Timestamp:    time.Now(),
		MerkleRoot:   merkleRoot,
		Nonce:        0,
		Difficulty:   header.Difficulty,
	}
	
	// Calculate block hash
	block.Hash = cm.calculateBlockHash(block)
	
	return block, nil
}

// ValidateBlock validates a block according to consensus rules
func (cm *ConsensusManager) ValidateBlock(block *Block) error {
	// Verify block hash
	calculatedHash := cm.calculateBlockHash(block)
	if calculatedHash != block.Hash {
		return fmt.Errorf("invalid block hash")
	}
	
	// Verify previous hash
	if block.PreviousHash != cm.lastBlockHash {
		return fmt.Errorf("invalid previous hash")
	}
	
	// Verify block number
	if block.Header.BlockNumber != cm.blockHeight+1 {
		return fmt.Errorf("invalid block number")
	}
	
	// Verify Merkle root
	calculatedMerkleRoot := cm.calculateMerkleRoot(block.Transactions)
	if calculatedMerkleRoot != block.MerkleRoot {
		return fmt.Errorf("invalid Merkle root")
	}
	
	// Verify transactions
	for _, tx := range block.Transactions {
		if err := cm.ValidateTransaction(tx); err != nil {
			return fmt.Errorf("invalid transaction %s: %v", tx.ID, err)
		}
	}
	
	// Consensus-specific validation
	switch cm.consensusType {
	case RaftConsensus:
		return cm.validateRaftBlock(block)
	case PBFT:
		return cm.validatePBFTBlock(block)
	case PoA:
		return cm.validatePoABlock(block)
	case PoS:
		return cm.validatePoSBlock(block)
	default:
		return fmt.Errorf("unsupported consensus type: %s", cm.consensusType)
	}
}

// ValidateTransaction validates a transaction
func (cm *ConsensusManager) ValidateTransaction(tx *Transaction) error {
	// Verify transaction hash
	calculatedHash := cm.calculateTransactionHash(tx)
	if calculatedHash != tx.Hash {
		return fmt.Errorf("invalid transaction hash")
	}
	
	// Verify signature (in a real implementation, you would verify the cryptographic signature)
	if tx.Signature == "" {
		return fmt.Errorf("missing transaction signature")
	}
	
	// Verify nonce
	if tx.Nonce == 0 {
		return fmt.Errorf("invalid transaction nonce")
	}
	
	// Verify gas limit and price
	if tx.GasLimit == 0 || tx.GasPrice == 0 {
		return fmt.Errorf("invalid gas parameters")
	}
	
	return nil
}

// ProposeBlock proposes a block for consensus
func (cm *ConsensusManager) ProposeBlock(block *Block) error {
	// Validate the block first
	if err := cm.ValidateBlock(block); err != nil {
		return fmt.Errorf("block validation failed: %v", err)
	}
	
	// Send proposal to peers based on consensus type
	switch cm.consensusType {
	case RaftConsensus:
		return cm.proposeRaftBlock(block)
	case PBFT:
		return cm.proposePBFTBlock(block)
	case PoA:
		return cm.proposePoABlock(block)
	case PoS:
		return cm.proposePoSBlock(block)
	default:
		return fmt.Errorf("unsupported consensus type: %s", cm.consensusType)
	}
}

// FinalizeBlock finalizes a block and updates the blockchain state
func (cm *ConsensusManager) FinalizeBlock(block *Block) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()
	
	// Update blockchain state
	cm.blockHeight = block.Header.BlockNumber
	cm.lastBlockHash = block.Hash
	
	// Update peer states
	for _, peer := range cm.peers {
		peer.LastSeen = time.Now()
	}
	
	return nil
}

// GetBlockHeight returns the current block height
func (cm *ConsensusManager) GetBlockHeight() uint64 {
	cm.mu.RLock()
	defer cm.mu.RUnlock()
	return cm.blockHeight
}

// GetLastBlockHash returns the hash of the last block
func (cm *ConsensusManager) GetLastBlockHash() string {
	cm.mu.RLock()
	defer cm.mu.RUnlock()
	return cm.lastBlockHash
}

// calculateBlockHash calculates the hash of a block
func (cm *ConsensusManager) calculateBlockHash(block *Block) string {
	// Create a copy of the block without the hash for hashing
	blockCopy := *block
	blockCopy.Hash = ""
	
	blockData, _ := json.Marshal(blockCopy)
	hash := sha256.Sum256(blockData)
	return hex.EncodeToString(hash[:])
}

// calculateTransactionHash calculates the hash of a transaction
func (cm *ConsensusManager) calculateTransactionHash(tx *Transaction) string {
	// Create a copy of the transaction without the hash for hashing
	txCopy := *tx
	txCopy.Hash = ""
	
	txData, _ := json.Marshal(txCopy)
	hash := sha256.Sum256(txData)
	return hex.EncodeToString(hash[:])
}

// calculateMerkleRoot calculates the Merkle root of transactions
func (cm *ConsensusManager) calculateMerkleRoot(transactions []*Transaction) string {
	if len(transactions) == 0 {
		return ""
	}
	
	if len(transactions) == 1 {
		return cm.calculateTransactionHash(transactions[0])
	}
	
	// Simple Merkle tree implementation
	var hashes []string
	for _, tx := range transactions {
		hashes = append(hashes, cm.calculateTransactionHash(tx))
	}
	
	for len(hashes) > 1 {
		var newHashes []string
		for i := 0; i < len(hashes); i += 2 {
			if i+1 < len(hashes) {
				combined := hashes[i] + hashes[i+1]
				hash := sha256.Sum256([]byte(combined))
				newHashes = append(newHashes, hex.EncodeToString(hash[:]))
			} else {
				newHashes = append(newHashes, hashes[i])
			}
		}
		hashes = newHashes
	}
	
	return hashes[0]
}

// calculateDifficulty calculates the current difficulty
func (cm *ConsensusManager) calculateDifficulty() uint64 {
	// Simple difficulty calculation
	// In a real implementation, this would be more sophisticated
	baseDifficulty := uint64(1000)
	heightFactor := cm.blockHeight / 1000
	return baseDifficulty + heightFactor
}

// Consensus-specific validation methods
func (cm *ConsensusManager) validateRaftBlock(block *Block) error {
	// Raft-specific validation
	// In Raft, we mainly need to ensure the block is from the current leader
	return nil
}

func (cm *ConsensusManager) validatePBFTBlock(block *Block) error {
	// PBFT-specific validation
	// Need to ensure we have enough prepare and commit messages
	return nil
}

func (cm *ConsensusManager) validatePoABlock(block *Block) error {
	// PoA-specific validation
	// Verify the validator is authorized
	return nil
}

func (cm *ConsensusManager) validatePoSBlock(block *Block) error {
	// PoS-specific validation
	// Verify the validator has sufficient stake
	return nil
}

// Consensus-specific proposal methods
func (cm *ConsensusManager) proposeRaftBlock(block *Block) error {
	// Raft proposal logic
	return nil
}

func (cm *ConsensusManager) proposePBFTBlock(block *Block) error {
	// PBFT proposal logic
	return nil
}

func (cm *ConsensusManager) proposePoABlock(block *Block) error {
	// PoA proposal logic
	return nil
}

func (cm *ConsensusManager) proposePoSBlock(block *Block) error {
	// PoS proposal logic
	return nil
}

// GetConsensusStats returns consensus statistics
func (cm *ConsensusManager) GetConsensusStats() map[string]interface{} {
	cm.mu.RLock()
	defer cm.mu.RUnlock()
	
	activePeers := 0
	for _, peer := range cm.peers {
		if peer.IsActive {
			activePeers++
		}
	}
	
	return map[string]interface{}{
		"consensusType":    cm.consensusType,
		"blockHeight":      cm.blockHeight,
		"lastBlockHash":    cm.lastBlockHash,
		"totalPeers":       len(cm.peers),
		"activePeers":      activePeers,
		"consensusTimeout": cm.config.ConsensusTimeout,
		"blockTime":        cm.config.BlockTime,
	}
} 