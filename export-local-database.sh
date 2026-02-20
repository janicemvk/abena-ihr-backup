#!/bin/bash
# ABENA Database Export Script
# Exports entire local database with all data from Docker container

echo "🔧 ABENA Database Export Tool"
echo "================================"
echo ""

# Configuration
CONTAINER_NAME="abena-postgres"
DB_USER="abena_user"
DB_NAME="abena_ihr"
EXPORT_DIR="./database_exports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_FILE="abena_database_full_${TIMESTAMP}.sql"

echo "📋 Export Configuration:"
echo "   Container: $CONTAINER_NAME"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Export Directory: $EXPORT_DIR"
echo "   Export File: $EXPORT_FILE"
echo ""

# Create export directory if it doesn't exist
mkdir -p "$EXPORT_DIR"

# Check if container is running
echo "📋 Step 1: Checking if PostgreSQL container is running..."
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running!"
    echo "   Please start your ABENA system first: docker-compose up -d"
    exit 1
fi
echo "✅ Container is running"
echo ""

# Check database connection
echo "📋 Step 2: Testing database connection..."
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Cannot connect to database"
    exit 1
fi
echo ""

# Get database statistics
echo "📋 Step 3: Checking database contents..."
PATIENT_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM patients;" 2>/dev/null | tr -d ' ')
TABLE_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

echo "   📊 Database Statistics:"
echo "      Tables: $TABLE_COUNT"
echo "      Patients: $PATIENT_COUNT"
echo ""

# Export database with all data
echo "📋 Step 4: Exporting database (this may take a moment)..."
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-privileges \
    --clean \
    --if-exists \
    --create \
    > "$EXPORT_DIR/$EXPORT_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database exported successfully!"
else
    echo "❌ Export failed!"
    exit 1
fi
echo ""

# Get file size
FILE_SIZE=$(ls -lh "$EXPORT_DIR/$EXPORT_FILE" | awk '{print $5}')
echo "📋 Step 5: Export complete!"
echo "   📁 File: $EXPORT_DIR/$EXPORT_FILE"
echo "   📦 Size: $FILE_SIZE"
echo ""

# Create a compressed version
echo "📋 Step 6: Creating compressed version..."
gzip -c "$EXPORT_DIR/$EXPORT_FILE" > "$EXPORT_DIR/$EXPORT_FILE.gz"
if [ $? -eq 0 ]; then
    COMPRESSED_SIZE=$(ls -lh "$EXPORT_DIR/$EXPORT_FILE.gz" | awk '{print $5}')
    echo "✅ Compressed version created!"
    echo "   📁 File: $EXPORT_DIR/$EXPORT_FILE.gz"
    echo "   📦 Size: $COMPRESSED_SIZE"
else
    echo "⚠️  Compression failed (not critical)"
fi
echo ""

# Export additional databases if they exist
echo "📋 Step 7: Checking for additional databases..."
EXTRA_DBS=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -t -c "SELECT datname FROM pg_database WHERE datname IN ('abena_patients', 'abena_clinical', 'abena_blockchain');" 2>/dev/null | tr -d ' ')

if [ -n "$EXTRA_DBS" ]; then
    echo "   Found additional databases, exporting..."
    for db in $EXTRA_DBS; do
        echo "   Exporting: $db"
        docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$db" \
            --format=plain \
            --no-owner \
            --no-privileges \
            --clean \
            --if-exists \
            --create \
            > "$EXPORT_DIR/abena_${db}_${TIMESTAMP}.sql" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "   ✅ $db exported"
            gzip "$EXPORT_DIR/abena_${db}_${TIMESTAMP}.sql" 2>/dev/null
        else
            echo "   ⚠️  $db export failed (might not exist)"
        fi
    done
else
    echo "   ℹ️  No additional databases found (this is normal)"
fi
echo ""

# Create a manifest file
echo "📋 Step 8: Creating manifest file..."
MANIFEST_FILE="$EXPORT_DIR/export_manifest_${TIMESTAMP}.txt"
cat > "$MANIFEST_FILE" << EOF
ABENA Database Export Manifest
================================
Export Date: $(date)
Hostname: $(hostname)
Docker Container: $CONTAINER_NAME

Database Information:
- Database Name: $DB_NAME
- Database User: $DB_USER
- Tables Count: $TABLE_COUNT
- Patients Count: $PATIENT_COUNT

Exported Files:
- Main Database: $EXPORT_FILE
- Compressed: $EXPORT_FILE.gz
$([ -n "$EXTRA_DBS" ] && echo "- Additional DBs: $EXTRA_DBS")

File Sizes:
- Uncompressed: $FILE_SIZE
- Compressed: $COMPRESSED_SIZE

Import Instructions:
====================
1. Copy files to live server:
   scp $EXPORT_DIR/$EXPORT_FILE.gz user@live-server:/path/to/abena/

2. On live server, extract and import:
   gunzip $EXPORT_FILE.gz
   ./import-live-database.sh $EXPORT_FILE

3. Restart ABENA services:
   docker-compose restart

Notes:
- This export includes schema, data, and sequences
- Export is compatible with PostgreSQL 15+
- Use the import-live-database.sh script for importing
EOF

echo "✅ Manifest created: $MANIFEST_FILE"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ EXPORT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Exported Files:"
echo "   1. $EXPORT_DIR/$EXPORT_FILE ($FILE_SIZE)"
echo "   2. $EXPORT_DIR/$EXPORT_FILE.gz ($COMPRESSED_SIZE)"
echo "   3. $MANIFEST_FILE"
echo ""
echo "📋 Database Contents:"
echo "   - $TABLE_COUNT tables"
echo "   - $PATIENT_COUNT patients"
echo "   - All data, schemas, and sequences included"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Transfer to live server:"
echo "      scp $EXPORT_DIR/$EXPORT_FILE.gz user@live-server:/path/to/abena/"
echo ""
echo "   2. Also transfer the import script:"
echo "      scp import-live-database.sh user@live-server:/path/to/abena/"
echo ""
echo "   3. On live server, run:"
echo "      ./import-live-database.sh $EXPORT_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

