-- Create the mm_customer database if it doesn't exist
CREATE DATABASE mm_customer;
-- Connect to the mm_customer database
\connect mm_customer;

-- Create a table for customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    addressid VARCHAR(255),  -- Soft reference to an address in the mm-address service (e.g., ViaCEP address ID)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optionally, add indexes for commonly queried columns
CREATE INDEX IF NOT EXISTS idx_customers_cpf ON customers(cpf);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
