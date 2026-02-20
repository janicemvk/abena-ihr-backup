# ABENA Blockchain

A Substrate-based blockchain platform for healthcare data management with quantum-resistant encryption, native token gamification, and quantum computing integration.

## Features

- **Patient Health Records**: Secure, quantum-resistant encrypted health records
- **ABENA Coin**: Native token for gamification and rewards
- **Quantum Computing Integration**: Integration points for quantum computing results

## Project Structure

```
.
├── node/                    # Node implementation
├── runtime/                 # Runtime configuration
└── pallets/                 # Custom pallets
    ├── patient-health-records/  # Health records pallet
    ├── abena-coin/             # Native token pallet
    └── quantum-computing/       # Quantum computing pallet
```

## Building

```bash
cargo build --release
```

## Running

```bash
./target/release/abena-node --dev
```

## Development

This project uses Substrate v1.0.0 (Polkadot SDK).

