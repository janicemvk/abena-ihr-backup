#!/usr/bin/env python3
"""
Migration Script: Convert Existing Modules to Abena SDK

This script helps migrate existing modules to use the Abena SDK
following the Universal Integration Pattern instead of implementing
their own authentication, authorization, and data handling.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any


class SDKMigrationHelper:
    """Helper class for migrating modules to Abena SDK"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.sdk_import = "from abena_sdk import AbenaClient"
        self.sdk_initialization = """
# Initialize Abena SDK (Universal Integration Pattern)
self.abena = AbenaClient({
    'api_base_url': 'https://api.abena.com',
    'client_id': os.getenv('ABENA_CLIENT_ID'),
    'client_secret': os.getenv('ABENA_CLIENT_SECRET')
})
"""
    
    def find_modules_to_migrate(self) -> List[Path]:
        """Find Python modules that need migration"""
        modules = []
        
        # Common patterns that indicate custom auth/data handling
        patterns = [
            r'class.*Auth',
            r'class.*Database',
            r'class.*Session',
            r'def.*authenticate',
            r'def.*login',
            r'def.*check_permission',
            r'import.*sqlalchemy',
            r'import.*psycopg2',
            r'import.*redis',
            r'import.*jwt',
            r'from.*auth',
            r'from.*database',
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            if "abena_sdk" in str(py_file):
                continue  # Skip SDK files
            
            content = py_file.read_text()
            
            # Check if file contains patterns indicating custom auth/data
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    modules.append(py_file)
                    break
        
        return modules
    
    def analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """Analyze a module to understand its current structure"""
        content = module_path.read_text()
        
        analysis = {
            'path': module_path,
            'has_custom_auth': False,
            'has_custom_database': False,
            'has_custom_session': False,
            'auth_methods': [],
            'database_methods': [],
            'imports_to_remove': [],
            'imports_to_add': [],
            'classes_to_modify': []
        }
        
        # Check for custom authentication
        if re.search(r'class.*Auth', content):
            analysis['has_custom_auth'] = True
            analysis['auth_methods'] = re.findall(r'def\s+(\w+)\s*\(.*\):', content)
        
        # Check for custom database handling
        if re.search(r'class.*Database|import.*sqlalchemy|import.*psycopg2', content):
            analysis['has_custom_database'] = True
            analysis['database_methods'] = re.findall(r'def\s+(\w+)\s*\(.*\):', content)
        
        # Check for custom session handling
        if re.search(r'class.*Session|sessionmaker|create_session', content):
            analysis['has_custom_session'] = True
        
        # Find imports to remove
        imports_to_remove = [
            'sqlalchemy', 'psycopg2', 'redis', 'jwt', 'requests',
            'from sqlalchemy', 'from psycopg2', 'from redis', 'import jwt'
        ]
        
        for imp in imports_to_remove:
            if imp in content:
                analysis['imports_to_remove'].append(imp)
        
        # Find classes that need modification
        class_pattern = r'class\s+(\w+)\s*[:\(]'
        classes = re.findall(class_pattern, content)
        analysis['classes_to_modify'] = classes
        
        return analysis
    
    def generate_migration_plan(self, module_path: Path) -> str:
        """Generate a migration plan for a module"""
        analysis = self.analyze_module(module_path)
        
        plan = f"""
# Migration Plan for {module_path.name}
# ======================================

## Current State Analysis:
- Has custom auth: {analysis['has_custom_auth']}
- Has custom database: {analysis['has_custom_database']}
- Has custom session: {analysis['has_custom_session']}
- Classes to modify: {', '.join(analysis['classes_to_modify'])}

## Migration Steps:

### 1. Add Abena SDK Import
Add this import at the top of the file:
```python
from abena_sdk import AbenaClient
import os
```

### 2. Remove Custom Imports
Remove these imports:
{chr(10).join(f"- {imp}" for imp in analysis['imports_to_remove'])}

### 3. Replace Constructor
Replace the constructor in each class with:
```python
def __init__(self, ...):
    # Initialize Abena SDK (Universal Integration Pattern)
    self.abena = AbenaClient({
        'api_base_url': 'https://api.abena.com',
        'client_id': os.getenv('ABENA_CLIENT_ID'),
        'client_secret': os.getenv('ABENA_CLIENT_SECRET')
    })
    # ... rest of your initialization
```

### 4. Replace Data Access Methods
Replace custom data access with SDK methods:

BEFORE:
```python
def get_patient_data(self, patient_id):
    # Custom database query
    session = self.database.create_session()
    patient = session.query(Patient).filter_by(id=patient_id).first()
    return patient
```

AFTER:
```python
def get_patient_data(self, patient_id, user_id):
    # Auto-handled auth & permissions
    patient_data = self.abena.get_patient_data(patient_id, user_id, 'module_purpose')
    return patient_data.data
```

### 5. Replace Authentication Methods
Replace custom auth with SDK methods:

BEFORE:
```python
def authenticate_user(self, username, password):
    # Custom authentication logic
    return self.auth_system.authenticate(username, password)
```

AFTER:
```python
def authenticate_user(self, username, password):
    # Use SDK authentication
    token = self.abena.authenticate()
    return token
```

### 6. Replace Permission Checks
Replace custom permission checks with SDK methods:

BEFORE:
```python
def check_permission(self, user_id, permission):
    # Custom permission logic
    return self.auth_system.check_permission(user_id, permission)
```

AFTER:
```python
def check_permission(self, user_id, permission):
    # Use SDK permission checking
    return self.abena.check_permission(user_id, permission)
```

## Benefits:
- Automatic authentication and authorization
- Centralized data handling with privacy and encryption
- Automatic audit logging
- Focus on business logic instead of infrastructure
"""
        
        return plan
    
    def create_migration_example(self, module_path: Path) -> str:
        """Create a migration example for a module"""
        analysis = self.analyze_module(module_path)
        content = module_path.read_text()
        
        # Create before/after example
        example = f"""
# Migration Example for {module_path.name}
# =======================================

## BEFORE (❌ Custom Implementation):
```python
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import jwt
import redis

class SomeModule:
    def __init__(self):
        # Custom database connection
        self.engine = sqlalchemy.create_engine('postgresql://...')
        self.Session = sessionmaker(bind=self.engine)
        
        # Custom authentication
        self.auth_system = CustomAuth()
        
        # Custom cache
        self.cache = redis.Redis()
    
    def get_patient_data(self, patient_id):
        # Manual permission check
        if not self.auth_system.check_permission(user_id, 'read:patient'):
            raise PermissionError()
        
        # Manual database query
        session = self.Session()
        patient = session.query(Patient).filter_by(id=patient_id).first()
        session.close()
        
        return patient
    
    def authenticate_user(self, username, password):
        # Custom authentication
        return self.auth_system.authenticate(username, password)
```

## AFTER (✅ Abena SDK):
```python
from abena_sdk import AbenaClient
import os

class SomeModule:
    def __init__(self):
        # Initialize Abena SDK (Universal Integration Pattern)
        self.abena = AbenaClient({{
            'api_base_url': 'https://api.abena.com',
            'client_id': os.getenv('ABENA_CLIENT_ID'),
            'client_secret': os.getenv('ABENA_CLIENT_SECRET')
        }})
    
    def get_patient_data(self, patient_id, user_id):
        # 1. Auto-handled auth & permissions
        # 2. Auto-handled privacy & encryption
        # 3. Auto-handled audit logging
        patient_data = self.abena.get_patient_data(patient_id, user_id, 'module_purpose')
        
        # 4. Focus on your business logic
        return self.process_data(patient_data.data)
    
    def authenticate_user(self, username, password):
        # Use SDK authentication
        token = self.abena.authenticate()
        return token
```
"""
        
        return example


def main():
    """Main migration script"""
    print("🔄 Abena SDK Migration Helper")
    print("=" * 50)
    
    # Get project root
    project_root = input("Enter project root path (or press Enter for current directory): ").strip()
    if not project_root:
        project_root = os.getcwd()
    
    helper = SDKMigrationHelper(project_root)
    
    # Find modules to migrate
    print(f"\n🔍 Scanning for modules to migrate in: {project_root}")
    modules = helper.find_modules_to_migrate()
    
    if not modules:
        print("✅ No modules found that need migration!")
        return
    
    print(f"\n📋 Found {len(modules)} modules that may need migration:")
    for i, module in enumerate(modules, 1):
        print(f"  {i}. {module.relative_to(project_root)}")
    
    # Generate migration plans
    print(f"\n📝 Generating migration plans...")
    
    for module in modules:
        print(f"\n{'='*60}")
        print(f"Module: {module.relative_to(project_root)}")
        print(f"{'='*60}")
        
        plan = helper.generate_migration_plan(module)
        print(plan)
        
        example = helper.create_migration_example(module)
        print(example)
    
    print(f"\n✅ Migration analysis complete!")
    print(f"\n📚 Next steps:")
    print(f"1. Review the migration plans above")
    print(f"2. Update your environment variables with Abena SDK credentials")
    print(f"3. Migrate modules one by one following the Universal Integration Pattern")
    print(f"4. Test each migrated module thoroughly")
    print(f"5. Remove old custom authentication and data handling code")


if __name__ == "__main__":
    main() 