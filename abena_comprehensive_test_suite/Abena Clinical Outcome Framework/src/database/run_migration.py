import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_CONFIG, SCHEMA_NAME

print("Loaded password:", DB_CONFIG['password'])

def run_migration():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Create database if it doesn't exist
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['database']}'")
        if not cur.fetchone():
            print(f"Creating database {DB_CONFIG['database']}...")
            cur.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print("Database created successfully.")

        # Close connection to create new one with the specific database
        cur.close()
        conn.close()

        # Connect to the specific database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cur = conn.cursor()

        # Read and execute migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '001_clinical_outcomes.sql')
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
            
        print("Running migration...")
        cur.execute(migration_sql)
        print("Migration completed successfully.")

        # Close connection
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 