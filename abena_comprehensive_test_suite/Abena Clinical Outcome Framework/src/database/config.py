from typing import Dict
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
from pathlib import Path

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

print("Current working directory:", os.getcwd())
print("Looking for .env at:", os.path.join(os.getcwd(), '.env'))

# Database configuration
DB_CONFIG: Dict[str, str] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'abena_ihr'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Schema configuration
SCHEMA_NAME = 'clinical_outcomes'

# Database URLs
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}" 