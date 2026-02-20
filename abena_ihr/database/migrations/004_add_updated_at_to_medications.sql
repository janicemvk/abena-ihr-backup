-- Add updated_at column to medications table
ALTER TABLE medications ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to have updated_at
UPDATE medications SET updated_at = created_at WHERE updated_at IS NULL;
