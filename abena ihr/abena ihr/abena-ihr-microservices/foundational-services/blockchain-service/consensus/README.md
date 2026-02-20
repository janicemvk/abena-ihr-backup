# Consensus

This directory contains consensus mechanisms for the Abena IHR blockchain service, ensuring data consistency and agreement across the distributed network.

## Overview

The consensus manager provides multiple consensus algorithms to ensure that all nodes in the blockchain network agree on the state of the ledger. This is crucial for maintaining data integrity and preventing double-spending or data inconsistencies.

## Supported Consensus Algorithms

### 1. Raft Consensus (Default)
- **Type**: `raft`
- **Use Case**: Hyperledger Fabric networks
- **Features**:
  - Leader-based consensus
  - Crash fault tolerance
  - Fast finality
  - Suitable for permissioned networks

### 2. Practical Byzantine Fault Tolerance (PBFT)
- **Type**: `pbft`
- **Use Case**: High-security healthcare networks
- **Features**:
  - Byzantine fault tolerance
  - Immediate finality
  - High security guarantees
  - Suitable for critical healthcare applications

### 3. Proof of Authority (PoA)
- **Type**: `poa`
- **Use Case**: Healthcare consortium networks
- **Features**:
  - Authority-based validation
  - Fast block times
  - Low energy consumption
  - Suitable for trusted validator networks

### 4. Proof of Stake (PoS)
- **Type**: `pos`
- **Use Case**: Public healthcare networks
- **Features**:
  - Stake-based validation
  - Energy efficient
  - Economic incentives
  - Suitable for public healthcare blockchains

## Files

### `consensus_manager.go`

The main consensus manager that handles different consensus algorithms and ensures network agreement.

#### Key Features

- **Multi-Algorithm Support**: Support for Raft, PBFT, PoA, and PoS
- **Peer Management**: Add, remove, and monitor network peers
- **Block Validation**: Validate blocks according to consensus rules
- **Transaction Processing**: Process and validate transactions
- **Network Synchronization**: Keep all nodes in sync
- **Fault Tolerance**: Handle network failures and malicious nodes

#### Core Functions

- **Block Management**:
  - `CreateBlock`: Create new blocks with transactions
  - `ValidateBlock`: Validate blocks according to consensus rules
  - `ProposeBlock`: Propose blocks for consensus
  - `FinalizeBlock`: Finalize blocks and update state

- **Transaction Management**:
  - `ValidateTransaction`: Validate individual transactions
  - Transaction hash calculation and verification
  - Gas limit and price validation

- **Peer Management**:
  - `AddPeer`: Add new peers to the network
  - `RemovePeer`: Remove peers from the network
  - `GetActivePeers`: Get all active peers

- **Consensus Operations**:
  - `GetBlockHeight`: Get current block height
  - `GetLastBlockHash`: Get hash of last block
  - `GetConsensusStats`: Get consensus statistics

## Configuration

### Consensus Configuration

```go
config := &ConsensusConfig{
    Type:                    consensus.RaftConsensus,
    BlockTime:               2 * time.Second,
    MaxBlockSize:            1000,
    MinPeers:                3,
    FaultToleranceThreshold: 1,
    StakeRequirement:        1000.0,
    ConsensusTimeout:        30 * time.Second,
}
```

### Algorithm-Specific Settings

#### Raft Consensus
```go
raftConfig := &RaftConfig{
    ElectionTimeout:  1000 * time.Millisecond,
    HeartbeatTimeout: 100 * time.Millisecond,
    MaxLogEntries:    1000,
}
```

#### PBFT Consensus
```go
pbftConfig := &PBFTConfig{
    ViewChangeTimeout: 10 * time.Second,
    RequestTimeout:    5 * time.Second,
    BatchSize:         100,
    BatchTimeout:      2 * time.Second,
}
```

#### PoA Consensus
```go
poaConfig := &PoAConfig{
    ValidatorAddresses: []string{"validator1", "validator2", "validator3"},
    BlockReward:        0,
    GasLimit:           8000000,
}
```

#### PoS Consensus
```go
posConfig := &PoSConfig{
    MinimumStake:      1000.0,
    StakeLockPeriod:   30 * 24 * time.Hour, // 30 days
    RewardRate:        0.05, // 5% annual
    SlashingPenalty:   0.5,  // 50% penalty
}
```

## Usage

### Initializing Consensus Manager

```go
// Create consensus configuration
config := &ConsensusConfig{
    Type:         consensus.RaftConsensus,
    BlockTime:    2 * time.Second,
    MinPeers:     3,
    ConsensusTimeout: 30 * time.Second,
}

// Create consensus manager
consensusManager := consensus.NewConsensusManager(config)

// Add peers
peer1 := &consensus.Peer{
    ID:       "peer1",
    Address:  "192.168.1.10",
    Port:     7051,
    IsActive: true,
}
consensusManager.AddPeer(peer1)
```

### Creating and Validating Blocks

```go
// Create transactions
transactions := []*consensus.Transaction{
    {
        ID:        "tx1",
        Type:      "health_record",
        Data:      map[string]interface{}{"patient_id": "123"},
        From:      "provider1",
        To:        "patient1",
        Timestamp: time.Now(),
    },
}

// Create block
block, err := consensusManager.CreateBlock(transactions, "validator1")
if err != nil {
    log.Printf("Error creating block: %v", err)
}

// Validate block
err = consensusManager.ValidateBlock(block)
if err != nil {
    log.Printf("Block validation failed: %v", err)
}

// Propose block for consensus
err = consensusManager.ProposeBlock(block)
if err != nil {
    log.Printf("Block proposal failed: %v", err)
}

// Finalize block
err = consensusManager.FinalizeBlock(block)
if err != nil {
    log.Printf("Block finalization failed: %v", err)
}
```

### Monitoring Consensus

```go
// Get consensus statistics
stats := consensusManager.GetConsensusStats()
log.Printf("Block height: %d", stats["blockHeight"])
log.Printf("Active peers: %d", stats["activePeers"])
log.Printf("Consensus type: %s", stats["consensusType"])
```

## Security Features

### Cryptographic Integrity
- SHA-256 hashing for blocks and transactions
- Merkle tree construction for transaction verification
- Digital signatures for transaction authentication

### Fault Tolerance
- Crash fault tolerance (Raft)
- Byzantine fault tolerance (PBFT)
- Network partition handling
- Automatic recovery mechanisms

### Access Control
- Validator authorization (PoA)
- Stake-based validation (PoS)
- Role-based permissions
- Network membership control

## Performance Considerations

### Block Time Optimization
- Adjust block time based on network requirements
- Balance between finality and throughput
- Consider network latency and bandwidth

### Scalability
- Horizontal scaling with additional peers
- Vertical scaling with improved hardware
- Sharding for large networks
- Off-chain solutions for high throughput

### Resource Management
- Memory usage optimization
- CPU utilization monitoring
- Network bandwidth management
- Storage optimization

## Monitoring and Metrics

### Key Metrics
- Block height and hash
- Transaction throughput
- Consensus latency
- Peer connectivity
- Network health

### Health Checks
```go
// Check consensus health
isHealthy := consensusManager.IsHealthy()
if !isHealthy {
    log.Println("Consensus health check failed")
}

// Get detailed health status
healthStatus := consensusManager.GetHealthStatus()
log.Printf("Health status: %+v", healthStatus)
```

## Troubleshooting

### Common Issues

1. **Consensus Failures**:
   - Check peer connectivity
   - Verify network configuration
   - Review consensus parameters

2. **Block Validation Errors**:
   - Verify transaction signatures
   - Check block structure
   - Validate Merkle roots

3. **Network Partitioning**:
   - Monitor peer status
   - Check network connectivity
   - Review fault tolerance settings

4. **Performance Issues**:
   - Optimize block size
   - Adjust consensus timeouts
   - Monitor resource usage

### Debugging

Enable debug logging:

```go
// Enable debug mode
consensusManager.SetDebugMode(true)

// Get detailed logs
logs := consensusManager.GetDebugLogs()
for _, log := range logs {
    fmt.Println(log)
}
```

## Best Practices

### Configuration
- Choose appropriate consensus algorithm for use case
- Configure timeouts based on network characteristics
- Set proper fault tolerance thresholds
- Monitor and adjust parameters as needed

### Security
- Use strong cryptographic algorithms
- Implement proper key management
- Regular security audits
- Monitor for suspicious activity

### Performance
- Optimize block size and frequency
- Monitor resource usage
- Implement caching where appropriate
- Use efficient data structures

### Maintenance
- Regular health checks
- Monitor consensus statistics
- Update consensus parameters
- Backup critical data

## Support

For issues and questions:

1. Check the main blockchain service documentation
2. Review consensus algorithm documentation
3. Contact the development team
4. Submit issues through the project repository 