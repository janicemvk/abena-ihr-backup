-- Add payment fields to appointments table
ALTER TABLE appointments 
ADD COLUMN payment_intent_id VARCHAR(255),
ADD COLUMN payment_amount DECIMAL(10,2),
ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending';

-- Add index for payment queries
CREATE INDEX idx_appointments_payment_intent ON appointments(payment_intent_id);
CREATE INDEX idx_appointments_payment_status ON appointments(payment_status);

-- Add comments
COMMENT ON COLUMN appointments.payment_intent_id IS 'Stripe payment intent ID';
COMMENT ON COLUMN appointments.payment_amount IS 'Payment amount in USD';
COMMENT ON COLUMN appointments.payment_status IS 'Payment status: pending, succeeded, failed, cancelled';
