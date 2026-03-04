# abena-cli

ABENA node deployment and operations CLI.

## Install

```bash
cd cli && npm install && npm run build
```

## Usage

```bash
# Deploy node for hospital
abena-cli deploy --type=hospital --org="Mayo Clinic"

# Join consortium network
abena-cli join-network --consortium=us-healthcare --validator

# Backup chain DB
abena-cli backup --destination=/path/to/backups
abena-cli backup --destination=s3://mayo-backups/

# Restore from backup
abena-cli restore --from=snapshot-20260301
abena-cli restore --from=s3://mayo-backups/snapshot-20260301.tar.gz

# Check node status
abena-cli status
```
