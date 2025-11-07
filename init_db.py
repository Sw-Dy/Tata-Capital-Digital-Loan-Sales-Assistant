#!/usr/bin/env python3
"""
Database initialization and migration script for Tata Capital Loan Processing System
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from implementation.database import create_tables, get_db
from implementation.master_agent import MasterAgent
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database with all tables"""
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        create_tables()
        logger.info("Database tables created successfully!")
        
        # Test database connection
        db = next(get_db())
        logger.info("Database connection test successful!")
        db.close()
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing (optional)"""
    try:
        logger.info("Creating sample data...")
        
        # You can add sample users or test data here if needed
        # For now, we'll just log that the database is ready
        
        logger.info("Sample data creation completed!")
        return True
        
    except Exception as e:
        logger.error(f"Sample data creation failed: {str(e)}")
        return False

def main():
    """Main function to run database setup"""
    logger.info("Tata Capital Loan Processing System - Database Setup")
    logger.info("=" * 60)
    
    # Load environment variables
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning("No .env file found. Using default environment variables.")
    
    # Initialize database
    if initialize_database():
        logger.info("✅ Database setup completed successfully!")
        
        # Ask if user wants to create sample data
        response = input("\nWould you like to create sample data? (y/N): ").strip().lower()
        if response == 'y':
            create_sample_data()
            
        logger.info("\n🎉 Database is ready for use!")
        logger.info("\nNext steps:")
        logger.info("1. Start PostgreSQL and pgAdmin with: docker-compose up -d")
        logger.info("2. Run the backend server with: python web_app.py")
        logger.info("3. Access pgAdmin at http://localhost:5050")
        logger.info("4. Access the application at http://localhost:8000")
        
    else:
        logger.error("❌ Database setup failed!")
        logger.error("Please check your database configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()