#!/usr/bin/env python3
"""
Main entry point for the NLP Message Processor
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config.database import engine, SessionLocal, Base
from config.settings import settings
from scripts.init_db import init_database
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Try to execute a simple query
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        from models.database_models import Node, Edge, Message, MessageNode
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("NLP Message Processor")
    print("=" * 60)
    
    # 1. Test database connection
    print("\n1. Testing database connection...")
    if not test_database_connection():
        print("   Please check your database configuration in .env file")
        return
    
    # 2. Create tables
    print("\n2. Creating database tables...")
    if not create_tables():
        print("   Failed to create tables")
        return
    
    # 3. Initialize database with any seed data
    print("\n3. Initializing database...")
    # init_database()  # Uncomment if you have seed data
    
    print("\n" + "=" * 60)
    print("✅ Database setup complete!")
    print(f"   Database: {settings.DB_NAME}")
    print(f"   Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Run the web server: python webhook/app.py")
    print("2. Or test with: python test_system.py")
    
    return True

if __name__ == "__main__":
    main()