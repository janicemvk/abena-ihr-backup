#!/usr/bin/env python3
"""
Database migration script for Abena IHR
Handles database setup and migrations
"""

import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    return os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/abena_ihr')

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    db_url = get_database_url()
    
    # Parse the URL to get database name
    if 'postgresql://' in db_url:
        # Extract database name from URL
        db_name = db_url.split('/')[-1]
        base_url = '/'.join(db_url.split('/')[:-1])
        
        try:
            # Connect to postgres database to create our database
            engine = create_engine(base_url + '/postgres')
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if not result.fetchone():
                    logger.info(f"Creating database: {db_name}")
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    conn.commit()
                    logger.info(f"Database {db_name} created successfully")
                else:
                    logger.info(f"Database {db_name} already exists")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    return True

def run_migrations():
    """Run SQL migration files"""
    migrations_dir = Path(__file__).parent.parent / 'migrations'
    
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # Get all SQL files sorted by name
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        logger.warning("No migration files found")
        return True
    
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Create migrations table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            
            # Run each migration file
            for migration_file in migration_files:
                filename = migration_file.name
                
                # Check if migration already executed
                result = conn.execute(text("SELECT 1 FROM migrations WHERE filename = :filename"), 
                                    {"filename": filename})
                
                if result.fetchone():
                    logger.info(f"Migration {filename} already executed, skipping")
                    continue
                
                logger.info(f"Running migration: {filename}")
                
                # Read and execute migration file
                with open(migration_file, 'r') as f:
                    sql_content = f.read()
                
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                
                # Record migration as executed
                conn.execute(text("INSERT INTO migrations (filename) VALUES (:filename)"), 
                           {"filename": filename})
                conn.commit()
                
                logger.info(f"Migration {filename} completed successfully")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error running migrations: {e}")
        return False

def setup_initial_data():
    """Set up initial data if needed"""
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if we have any outcome definitions
            result = conn.execute(text("SELECT COUNT(*) FROM outcome_definitions"))
            count = result.fetchone()[0]
            
            if count == 0:
                logger.info("Setting up initial outcome definitions...")
                
                # Insert sample outcome definitions
                conn.execute(text("""
                    INSERT INTO outcome_definitions (name, description, outcome_type, measurement_scale, unit_of_measurement, min_value, max_value, created_at, updated_at)
                    VALUES 
                    ('pain_reduction', 'Reduction in pain score from baseline', 'primary', 'ratio', 'points', 0, 10, NOW(), NOW()),
                    ('functional_improvement', 'Improvement in functional ability', 'secondary', 'ordinal', NULL, NULL, NULL, NOW(), NOW()),
                    ('adverse_events', 'Number of adverse events', 'safety', 'ratio', 'events', 0, 100, NOW(), NOW())
                """))
                conn.commit()
                logger.info("Initial outcome definitions created")
            else:
                logger.info(f"Found {count} existing outcome definitions")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error setting up initial data: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("Starting Abena IHR database migration...")
    
    # Step 1: Create database if it doesn't exist
    if not create_database_if_not_exists():
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        logger.error("Failed to run migrations")
        sys.exit(1)
    
    # Step 3: Set up initial data
    if not setup_initial_data():
        logger.error("Failed to set up initial data")
        sys.exit(1)
    
    logger.info("Database migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 