# Fixing Dependency Tags

The project is currently using tags that don't exist. We need to update to valid Substrate/Polkadot SDK tags.

## Current Issue
- Tag `polkadot-v1.0.0` doesn't exist
- Need to find and use valid tags

## Solution Options

### Option 1: Use Latest Stable Branch
Change all `tag = "polkadot-v1.0.0"` to `branch = "master"` or `branch = "polkadot-v1.0"`

### Option 2: Use Valid Tags
Find actual tags from:
- https://github.com/paritytech/substrate/tags
- https://github.com/paritytech/polkadot-sdk/tags

### Option 3: Use Substrate Node Template Approach
Clone the substrate-node-template and copy its dependency versions.

## Recommended Fix

For now, let's use the master branch which should have the latest stable code:

Replace in all Cargo.toml files:
- `tag = "polkadot-v1.0.0"` → `branch = "master"`

Or use a known working tag like:
- `tag = "polkadot-v1.11.0"` (if it exists)
- `tag = "polkadot-v1.10.0"` (if it exists)

