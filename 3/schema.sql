CREATE DATABASE IF NOT EXISTS company_enrichment;
USE company_enrichment;

CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cin VARCHAR(21) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    address TEXT,
    state VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Active',
    website VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    enrichment_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed data for testing the pipeline
INSERT INTO companies (cin, company_name, address, state) VALUES
('U72200MH2002PTC135542', 'Tata Consultancy Services', 'TCS House, Raveline Street', 'Maharashtra'),
('L31300KA1981PLC004413', 'Infosys Limited', 'Electronics City, Hosur Road', 'Karnataka'),
('L32102MH1945PLC020969', 'Wipro Limited', 'Doddakannelli, Sarjapur Road', 'Karnataka');