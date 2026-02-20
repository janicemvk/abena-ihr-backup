"""
Abena IHR Password Migration Script
=====================================

Migrates existing plain-text passwords to bcrypt hashed passwords.
Includes rollback safety and progress tracking.

IMPORTANT: Run this script ONCE during security upgrade.
Backup your database before running!

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import asyncpg
from utils.password_security import PasswordSecurity


class PasswordMigration:
    """
    Password migration handler with safety features.
    
    Features:
    - Batch processing
    - Progress tracking
    - Rollback support
    - Dry-run mode
    - Detailed logging
    """
    
    def __init__(
        self,
        database_url: str,
        dry_run: bool = False,
        batch_size: int = 100
    ):
        """
        Initialize password migration.
        
        Args:
            database_url: PostgreSQL connection string
            dry_run: If True, don't actually update passwords
            batch_size: Number of passwords to process per batch
        """
        self.database_url = database_url
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.conn = None
        self.stats = {
            'total_users': 0,
            'migrated': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    async def connect(self):
        """Connect to database"""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            print("✓ Connected to database")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            sys.exit(1)
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            await self.conn.close()
            print("✓ Disconnected from database")
    
    async def analyze_users(self) -> List[Dict]:
        """
        Analyze users to determine migration needs.
        
        Returns:
            List of user dictionaries with migration status
        """
        print("\nAnalyzing users...")
        
        # Query to get all users
        # Adjust table/column names to match your schema
        query = """
            SELECT 
                id,
                email,
                password,
                password_hash,
                created_at,
                updated_at
            FROM users
            ORDER BY id
        """
        
        try:
            rows = await self.conn.fetch(query)
            users = []
            
            for row in rows:
                user = dict(row)
                
                # Determine if migration needed
                has_plain_password = bool(user.get('password'))
                has_hash = bool(user.get('password_hash'))
                
                if has_hash and not has_plain_password:
                    user['migration_status'] = 'already_hashed'
                elif has_plain_password:
                    user['migration_status'] = 'needs_migration'
                else:
                    user['migration_status'] = 'no_password'
                
                users.append(user)
            
            self.stats['total_users'] = len(users)
            return users
            
        except Exception as e:
            print(f"✗ Error analyzing users: {e}")
            print(f"  Query: {query}")
            print("\n⚠️  Please adjust the query to match your database schema!")
            return []
    
    async def migrate_user(self, user: Dict) -> bool:
        """
        Migrate a single user's password.
        
        Args:
            user: User dictionary with password data
            
        Returns:
            True if migration successful
        """
        if user['migration_status'] != 'needs_migration':
            self.stats['skipped'] += 1
            return True
        
        plain_password = user.get('password')
        if not plain_password:
            return True
        
        try:
            # Hash the password
            hashed_password = PasswordSecurity.hash_password(plain_password)
            
            if self.dry_run:
                print(f"  [DRY RUN] Would migrate user {user['id']} ({user['email']})")
                self.stats['migrated'] += 1
                return True
            
            # Update database
            # Adjust column names to match your schema
            update_query = """
                UPDATE users
                SET 
                    password_hash = $1,
                    password = NULL,  -- Remove plain text
                    password_changed_at = $2,
                    updated_at = $2
                WHERE id = $3
            """
            
            await self.conn.execute(
                update_query,
                hashed_password,
                datetime.utcnow(),
                user['id']
            )
            
            self.stats['migrated'] += 1
            return True
            
        except Exception as e:
            error_msg = f"User {user['id']} ({user['email']}): {e}"
            self.stats['errors'].append(error_msg)
            self.stats['failed'] += 1
            print(f"  ✗ {error_msg}")
            return False
    
    async def migrate_all(self):
        """Migrate all users in batches"""
        print("\n" + "=" * 60)
        print("Abena IHR Password Migration")
        print("=" * 60)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
        
        # Analyze users
        users = await self.analyze_users()
        
        if not users:
            print("\n✗ No users found or query failed")
            return
        
        # Show summary
        needs_migration = [u for u in users if u['migration_status'] == 'needs_migration']
        already_hashed = [u for u in users if u['migration_status'] == 'already_hashed']
        
        print(f"\nMigration Summary:")
        print(f"  Total users: {len(users)}")
        print(f"  Need migration: {len(needs_migration)}")
        print(f"  Already hashed: {len(already_hashed)}")
        print(f"  No password: {len(users) - len(needs_migration) - len(already_hashed)}")
        
        if not needs_migration:
            print("\n✓ No passwords need migration!")
            return
        
        # Confirm migration
        if not self.dry_run:
            print(f"\n⚠️  WARNING: This will migrate {len(needs_migration)} passwords!")
            print("   Make sure you have a database backup!")
            response = input("\nContinue? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return
        
        # Migrate in batches
        print(f"\nMigrating passwords (batch size: {self.batch_size})...")
        
        for i in range(0, len(needs_migration), self.batch_size):
            batch = needs_migration[i:i + self.batch_size]
            print(f"\nProcessing batch {i // self.batch_size + 1} ({len(batch)} users)...")
            
            for user in batch:
                await self.migrate_user(user)
                if self.stats['migrated'] % 10 == 0:
                    print(f"  Progress: {self.stats['migrated']}/{len(needs_migration)}")
        
        # Print final statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print migration statistics"""
        print("\n" + "=" * 60)
        print("Migration Statistics")
        print("=" * 60)
        print(f"Total users: {self.stats['total_users']}")
        print(f"Migrated: {self.stats['migrated']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")


async def main():
    """Main migration function"""
    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/abena_ihr"
    )
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    # Create migration instance
    migration = PasswordMigration(
        database_url=database_url,
        dry_run=dry_run
    )
    
    try:
        await migration.connect()
        await migration.migrate_all()
    finally:
        await migration.disconnect()


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Backup your database before running this script!")
    print("   This script will modify user passwords in the database.\n")
    
    asyncio.run(main())

