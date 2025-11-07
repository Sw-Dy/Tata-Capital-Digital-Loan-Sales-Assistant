-- Initialize Tata Capital Loans Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by Docker)
-- Create extensions for UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE tata_capital_loans TO postgres;

-- Create schema for better organization
CREATE SCHEMA IF NOT EXISTS loan_processing;

-- Set default schema
SET search_path TO loan_processing, public;