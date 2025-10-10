#!/bin/bash
# ABENA Live Database Setup Script
# Run this on your live server after deploying

echo "🔧 ABENA Live Database Setup"
echo "================================"

# Configuration - UPDATE THESE FOR YOUR LIVE SERVER
LIVE_DB_HOST="your-live-db-host"  # e.g., localhost or IP address
LIVE_DB_PORT="5432"
LIVE_DB_USER="abena_user"
LIVE_DB_PASSWORD="your-secure-password"
LIVE_DB_NAME="abena_ihr"

echo ""
echo "⚠️  IMPORTANT: Update the configuration variables in this script first!"
echo ""
echo "Current Configuration:"
echo "  Host: $LIVE_DB_HOST"
echo "  Port: $LIVE_DB_PORT"
echo "  User: $LIVE_DB_USER"
echo "  Database: $LIVE_DB_NAME"
echo ""

read -p "Have you updated the configuration? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Please update the configuration first!"
    exit 1
fi

echo ""
echo "📋 Step 1: Testing database connection..."
export PGPASSWORD="$LIVE_DB_PASSWORD"
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d postgres -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Cannot connect to database. Please check:"
    echo "   - Database host: $LIVE_DB_HOST"
    echo "   - Database port: $LIVE_DB_PORT"
    echo "   - Database user: $LIVE_DB_USER"
    echo "   - Database password"
    echo "   - Firewall rules"
    exit 1
fi

echo ""
echo "📋 Step 2: Creating database (if not exists)..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d postgres -c "CREATE DATABASE $LIVE_DB_NAME;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database created!"
else
    echo "ℹ️  Database already exists or creation failed (might be ok)"
fi

echo ""
echo "📋 Step 3: Loading database schemas and data..."

# Check if SQL files exist
if [ ! -f "ABENA PATIENT DATABASE.sql" ]; then
    echo "❌ SQL files not found! Make sure you're in the project directory."
    exit 1
fi

# Load SQL files in order
echo "   Loading IHR Database schema..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -f "IHR Database.sql" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ IHR schema loaded"
else
    echo "   ⚠️  IHR schema load had issues (might be ok if already loaded)"
fi

echo "   Loading patient database..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -f "ABENA PATIENT DATABASE.sql" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Patient data loaded"
else
    echo "   ⚠️  Patient data load had issues"
fi

echo "   Loading clinical data..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -f "ABENA CLINICAL DATA.sql" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Clinical data loaded"
else
    echo "   ⚠️  Clinical data load had issues"
fi

echo "   Loading blockchain status..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -f "ABENA BLOCKCHAIN STATUS.sql" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Blockchain data loaded"
else
    echo "   ⚠️  Blockchain data load had issues"
fi

echo "   Loading ABENA IHR data..."
psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -f "ABENA IHR.sql" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ ABENA IHR data loaded"
else
    echo "   ⚠️  ABENA IHR data load had issues"
fi

echo ""
echo "📋 Step 4: Verifying data..."
PATIENT_COUNT=$(psql -h "$LIVE_DB_HOST" -p "$LIVE_DB_PORT" -U "$LIVE_DB_USER" -d "$LIVE_DB_NAME" -t -c "SELECT COUNT(*) FROM patients;" 2>/dev/null | tr -d ' ')

if [ -n "$PATIENT_COUNT" ] && [ "$PATIENT_COUNT" -gt 0 ]; then
    echo "✅ Database verification successful!"
    echo "   Found $PATIENT_COUNT patients in database"
else
    echo "⚠️  Database might be empty or verification failed"
    echo "   Patient count: $PATIENT_COUNT"
fi

echo ""
echo "📋 Step 5: Update environment variables..."
echo ""
echo "Add this to your docker-compose.yml or .env file on live server:"
echo ""
echo "DATABASE_URL=postgresql://$LIVE_DB_USER:$LIVE_DB_PASSWORD@$LIVE_DB_HOST:$LIVE_DB_PORT/$LIVE_DB_NAME"
echo ""

echo ""
echo "✅ Database setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Update docker-compose.yml with correct DATABASE_URL"
echo "   2. Restart all ABENA services: docker-compose restart"
echo "   3. Test demo orchestrator: http://your-live-server:4020"
echo ""

unset PGPASSWORD

