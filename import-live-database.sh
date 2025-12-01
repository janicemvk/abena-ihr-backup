#!/bin/bash
# ABENA Database Import Script for Live Server
# Imports database dump from local system to live server

echo "🔧 ABENA Database Import Tool (Live Server)"
echo "============================================"
echo ""

# Check if SQL file is provided
if [ -z "$1" ]; then
    echo "❌ Error: No SQL file specified!"
    echo ""
    echo "Usage: $0 <database_export_file.sql>"
    echo ""
    echo "Example:"
    echo "   $0 database_exports/abena_database_full_20251010_120000.sql"
    echo ""
    echo "Available files:"
    ls -lh database_exports/*.sql 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
    exit 1
fi

SQL_FILE="$1"

# Check if file exists
if [ ! -f "$SQL_FILE" ]; then
    # Try with .gz extension
    if [ -f "$SQL_FILE.gz" ]; then
        echo "📋 Found compressed file, extracting..."
        gunzip "$SQL_FILE.gz"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to extract compressed file"
            exit 1
        fi
        echo "✅ File extracted"
    else
        echo "❌ Error: File not found: $SQL_FILE"
        exit 1
    fi
fi

echo "📋 Import Configuration:"
echo "   SQL File: $SQL_FILE"
echo "   File Size: $(ls -lh "$SQL_FILE" | awk '{print $5}')"
echo ""

# Configuration - UPDATE THESE FOR YOUR LIVE SERVER
read -p "🔧 Enter PostgreSQL host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "🔧 Enter PostgreSQL port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "🔧 Enter PostgreSQL user (default: abena_user): " DB_USER
DB_USER=${DB_USER:-abena_user}

read -s -p "🔧 Enter PostgreSQL password: " DB_PASSWORD
echo ""

read -p "🔧 Enter database name (default: abena_ihr): " DB_NAME
DB_NAME=${DB_NAME:-abena_ihr}

echo ""
echo "📋 Using Configuration:"
echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo "   User: $DB_USER"
echo "   Database: $DB_NAME"
echo ""

read -p "⚠️  Continue with import? This will REPLACE existing data! (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Import cancelled"
    exit 0
fi
echo ""

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

# Test connection
echo "📋 Step 1: Testing database connection..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Cannot connect to database!"
    echo "   Please check:"
    echo "   - Host: $DB_HOST"
    echo "   - Port: $DB_PORT"
    echo "   - User: $DB_USER"
    echo "   - Password"
    echo "   - Firewall settings"
    unset PGPASSWORD
    exit 1
fi
echo ""

# Backup existing database (if it exists)
echo "📋 Step 2: Checking if database exists..."
DB_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null | tr -d ' ')

if [ "$DB_EXISTS" = "1" ]; then
    echo "⚠️  Database $DB_NAME already exists!"
    BACKUP_FILE="backup_${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    echo "   Creating backup: $BACKUP_FILE"
    
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Backup created successfully"
        gzip "$BACKUP_FILE"
        echo "   Backup saved as: $BACKUP_FILE.gz"
    else
        echo "⚠️  Backup failed, but continuing..."
    fi
else
    echo "ℹ️  Database does not exist, will be created"
fi
echo ""

# Drop and recreate database
echo "📋 Step 3: Preparing database..."
echo "   Dropping existing database (if exists)..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" > /dev/null 2>&1

echo "   Creating fresh database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database prepared"
else
    echo "❌ Failed to prepare database"
    unset PGPASSWORD
    exit 1
fi
echo ""

# Import database
echo "📋 Step 4: Importing database (this may take several minutes)..."
echo "   Please wait..."

# Show progress
(
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE" > /tmp/import.log 2>&1
    echo $? > /tmp/import.status
) &

IMPORT_PID=$!

# Show spinner while importing
spin='-\|/'
i=0
while kill -0 $IMPORT_PID 2>/dev/null; do
    i=$(( (i+1) %4 ))
    printf "\r   Importing... ${spin:$i:1}"
    sleep 0.2
done
printf "\r   Importing... Done!\n"

# Check status
IMPORT_STATUS=$(cat /tmp/import.status)
if [ "$IMPORT_STATUS" -eq 0 ]; then
    echo "✅ Database imported successfully!"
else
    echo "❌ Import failed!"
    echo "   Check log: /tmp/import.log"
    tail -20 /tmp/import.log
    unset PGPASSWORD
    exit 1
fi
echo ""

# Verify import
echo "📋 Step 5: Verifying import..."
PATIENT_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM patients;" 2>/dev/null | tr -d ' ')
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

if [ -n "$PATIENT_COUNT" ] && [ "$PATIENT_COUNT" -gt 0 ]; then
    echo "✅ Verification successful!"
    echo "   📊 Database Statistics:"
    echo "      Tables: $TABLE_COUNT"
    echo "      Patients: $PATIENT_COUNT"
else
    echo "⚠️  Verification completed with warnings"
    echo "   Patient count: $PATIENT_COUNT"
    echo "   Table count: $TABLE_COUNT"
fi
echo ""

# Update sequences
echo "📋 Step 6: Updating sequences..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF > /dev/null 2>&1
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT 'SELECT SETVAL(' ||
               quote_literal(quote_ident(sequence_namespace.nspname) || '.' || quote_ident(class_sequence.relname)) ||
               ', COALESCE(MAX(' ||quote_ident(pg_attribute.attname)|| '), 1) ) FROM ' ||
               quote_ident(table_namespace.nspname)|| '.'||quote_ident(class_table.relname)|| ';' AS sql
        FROM pg_depend
        INNER JOIN pg_class AS class_sequence ON class_sequence.oid = pg_depend.objid
        INNER JOIN pg_class AS class_table ON class_table.oid = pg_depend.refobjid
        INNER JOIN pg_attribute ON pg_attribute.attrelid = pg_depend.refobjid AND pg_attribute.attnum = pg_depend.refobjsubid
        INNER JOIN pg_namespace as table_namespace ON table_namespace.oid = class_table.relnamespace
        INNER JOIN pg_namespace AS sequence_namespace ON sequence_namespace.oid = class_sequence.relnamespace
        WHERE pg_depend.deptype = 'a' AND class_sequence.relkind = 'S'
    LOOP
        EXECUTE r.sql;
    END LOOP;
END\$\$;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Sequences updated"
else
    echo "⚠️  Sequence update had issues (might be ok)"
fi
echo ""

# Generate DATABASE_URL
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo "📋 Step 7: Configuration for docker-compose.yml"
echo ""
echo "Add this to your docker-compose.yml environment section:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DATABASE_URL=$DATABASE_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cleanup
unset PGPASSWORD
rm -f /tmp/import.log /tmp/import.status

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ IMPORT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Database Summary:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   Tables: $TABLE_COUNT"
echo "   Patients: $PATIENT_COUNT"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Update docker-compose.yml with DATABASE_URL above"
echo ""
echo "   2. Restart ABENA services:"
echo "      docker-compose restart"
echo ""
echo "   3. Test demo orchestrator:"
echo "      http://your-server:4020"
echo ""
echo "   4. Verify health:"
echo "      curl http://your-server:4002/health"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

