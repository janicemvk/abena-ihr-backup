-- Create pharmacies table
CREATE TABLE IF NOT EXISTS pharmacies (
    id SERIAL PRIMARY KEY,
    pharmacy_name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    contact_person VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample pharmacy data
INSERT INTO pharmacies (pharmacy_name, address, phone, email, contact_person) VALUES
('CVS Pharmacy - Downtown', '123 Main St, Downtown, CA 90210', '(555) 123-4567', 'downtown@cvs.com', 'Dr. Sarah Johnson'),
('Walgreens - Medical Center', '456 Health Ave, Medical District, CA 90211', '(555) 234-5678', 'medical@walgreens.com', 'Dr. Michael Chen'),
('Rite Aid - Westside', '789 West Blvd, Westside, CA 90212', '(555) 345-6789', 'westside@riteaid.com', 'Dr. Emily Davis'),
('Local Pharmacy Plus', '321 Community Dr, Local Area, CA 90213', '(555) 456-7890', 'info@localpharmacy.com', 'Dr. Robert Wilson'),
('Express Scripts Pharmacy', '654 Fast Lane, Express District, CA 90214', '(555) 567-8901', 'orders@expressscripts.com', 'Dr. Lisa Thompson');

-- Add pharmacy_id column to medications table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medications' AND column_name = 'pharmacy_id') THEN
        ALTER TABLE medications ADD COLUMN pharmacy_id INTEGER REFERENCES pharmacies(id);
    END IF;
END $$;
