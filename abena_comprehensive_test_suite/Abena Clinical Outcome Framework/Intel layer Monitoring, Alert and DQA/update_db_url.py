#!/usr/bin/env python3
"""
Update DATABASE_URL in .env file
"""

import os
import re

def update_database_url():
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update the DATABASE_URL
    old_pattern = r'DATABASE_URL=postgresql://progres:.*?@localhost:5432/abena_ihr'
    new_url = 'DATABASE_URL=postgresql://postgres:2114***Million@localhost:5432/abena_ihr'
    
    if re.search(old_pattern, content):
        new_content = re.sub(old_pattern, new_url, content)
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print("✅ DATABASE_URL updated successfully")
        print(f"   New URL: {new_url}")
        return True
    else:
        print("❌ DATABASE_URL pattern not found in .env file")
        return False

if __name__ == "__main__":
    update_database_url() 