#!/usr/bin/env python3
"""
Database setup script for the Outcome Tracking Module
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, Base
from app.models.outcome import PatientOutcome
from app.models.episode import TreatmentEpisode
from app.config import settings


def setup_database():
    """Create database tables"""
    print("Setting up database...")
    print(f"Database URL: {settings.DATABASEV_URL}")  
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Check if database file exists (for SQLite)
        if settings.DATABASE_URL.startswith("sqlite"):
            db_file = settings.DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_file):
                print(f"✅ SQLite database file created: {db_file}")
            else:
                print(f"⚠️  SQLite database file not found: {db_file}")
        
        print("\n🎉 Database setup complete!")
        print("You can now run the application with: python manage.py server")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True


def check_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Outcome Tracking Module - Database Setup")
    print("=" * 50)
    
    # Check connection first
    if check_database_connection():
        # Setup database
        setup_database()
    else:
        print("\nPlease check your database configuration:")
        print(f"1. Database URL: {settings.DATABASE_URL}")
        print("2. For SQLite: No additional setup needed")
        print("3. For PostgreSQL: Ensure PostgreSQL is running and database exists")
        print("\nTo create PostgreSQL database:")
        print("   createdb outcome_tracking")
        print("   # or")
        print("   psql -c 'CREATE DATABASE outcome_tracking;'") 