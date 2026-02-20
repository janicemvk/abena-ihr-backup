#!/bin/bash

# Abena Clinical Outcomes Database Migration - Deployment Script
# This script automates the deployment of the clinical outcomes database schema

set -e  # Exit on any error

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-abena_clinical}"
DB_USER="${DB_USER:-postgres}"
SCHEMA_NAME="clinical_outcomes"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if PostgreSQL is available
check_postgres() {
    print_status "Checking PostgreSQL connection..."
    
    if ! command -v psql &> /dev/null; then
        print_error "psql command not found. Please install PostgreSQL client tools."
        exit 1
    fi
    
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
        print_error "Cannot connect to PostgreSQL database. Please check your connection parameters:"
        print_error "  Host: $DB_HOST"
        print_error "  Port: $DB_PORT"
        print_error "  Database: $DB_NAME"
        print_error "  User: $DB_USER"
        print_error ""
        print_error "You can set these using environment variables:"
        print_error "  DB_HOST, DB_PORT, DB_NAME, DB_USER"
        exit 1
    fi
    
    print_success "PostgreSQL connection successful"
}

# Function to check if required files exist
check_files() {
    print_status "Checking required files..."
    
    local required_files=(
        "abena_clinical_outcomes_migration.sql"
        "sample_data.sql"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Function to backup existing schema (if it exists)
backup_schema() {
    print_status "Checking for existing schema..."
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '$SCHEMA_NAME');" | grep -q t; then
        print_warning "Schema '$SCHEMA_NAME' already exists"
        
        if [[ "$FORCE_DEPLOY" == "true" ]]; then
            print_warning "Force deploy enabled - will drop existing schema"
            backup_file="backup_${SCHEMA_NAME}_$(date +%Y%m%d_%H%M%S).sql"
            print_status "Creating backup: $backup_file"
            
            if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -n "$SCHEMA_NAME" > "$backup_file"; then
                print_success "Backup created: $backup_file"
            else
                print_error "Failed to create backup"
                exit 1
            fi
        else
            print_error "Schema '$SCHEMA_NAME' already exists. Use FORCE_DEPLOY=true to overwrite."
            exit 1
        fi
    else
        print_status "Schema '$SCHEMA_NAME' does not exist - proceeding with fresh installation"
    fi
}

# Function to run the migration
run_migration() {
    print_status "Running database migration..."
    
    if [[ "$FORCE_DEPLOY" == "true" ]]; then
        print_status "Dropping existing schema..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA IF EXISTS $SCHEMA_NAME CASCADE;"
    fi
    
    print_status "Executing migration script..."
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "abena_clinical_outcomes_migration.sql"; then
        print_success "Migration completed successfully"
    else
        print_error "Migration failed"
        exit 1
    fi
}

# Function to insert sample data
insert_sample_data() {
    if [[ "$INSERT_SAMPLE_DATA" == "true" ]]; then
        print_status "Inserting sample data..."
        
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "sample_data.sql"; then
            print_success "Sample data inserted successfully"
        else
            print_error "Sample data insertion failed"
            exit 1
        fi
    else
        print_status "Skipping sample data insertion (set INSERT_SAMPLE_DATA=true to include)"
    fi
}

# Function to verify the installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if schema exists
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '$SCHEMA_NAME');" | grep -q t; then
        print_error "Schema verification failed - schema does not exist"
        exit 1
    fi
    
    # Check if tables were created
    local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$SCHEMA_NAME';" | tr -d ' ')
    
    if [[ "$table_count" -ge 10 ]]; then
        print_success "Schema verification successful - $table_count tables created"
    else
        print_error "Schema verification failed - expected at least 10 tables, found $table_count"
        exit 1
    fi
    
    # Check if views were created
    local view_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = '$SCHEMA_NAME';" | tr -d ' ')
    
    if [[ "$view_count" -ge 3 ]]; then
        print_success "Views verification successful - $view_count views created"
    else
        print_error "Views verification failed - expected at least 3 views, found $view_count"
        exit 1
    fi
}

# Function to display usage information
show_usage() {
    echo "Abena Clinical Outcomes Database Migration - Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help                    Show this help message"
    echo "  -f, --force                   Force deployment (drop existing schema)"
    echo "  -s, --sample-data             Include sample data insertion"
    echo "  --host HOST                   PostgreSQL host (default: localhost)"
    echo "  --port PORT                   PostgreSQL port (default: 5432)"
    echo "  --database DB                 Database name (default: abena_clinical)"
    echo "  --user USER                   Database user (default: postgres)"
    echo ""
    echo "Environment Variables:"
    echo "  DB_HOST                       PostgreSQL host"
    echo "  DB_PORT                       PostgreSQL port"
    echo "  DB_NAME                       Database name"
    echo "  DB_USER                       Database user"
    echo "  FORCE_DEPLOY                  Force deployment (true/false)"
    echo "  INSERT_SAMPLE_DATA            Include sample data (true/false)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Basic deployment"
    echo "  $0 -f -s                            # Force deploy with sample data"
    echo "  $0 --host myhost --database mydb    # Custom connection"
    echo "  FORCE_DEPLOY=true $0                 # Force deployment using env var"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -f|--force)
            FORCE_DEPLOY="true"
            shift
            ;;
        -s|--sample-data)
            INSERT_SAMPLE_DATA="true"
            shift
            ;;
        --host)
            DB_HOST="$2"
            shift 2
            ;;
        --port)
            DB_PORT="$2"
            shift 2
            ;;
        --database)
            DB_NAME="$2"
            shift 2
            ;;
        --user)
            DB_USER="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main deployment process
main() {
    echo "=========================================="
    echo "Abena Clinical Outcomes Database Migration"
    echo "=========================================="
    echo ""
    
    print_status "Starting deployment process..."
    print_status "Database: $DB_NAME@$DB_HOST:$DB_PORT"
    print_status "User: $DB_USER"
    print_status "Schema: $SCHEMA_NAME"
    echo ""
    
    # Run deployment steps
    check_files
    check_postgres
    backup_schema
    run_migration
    insert_sample_data
    verify_installation
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Review the created schema: SELECT * FROM information_schema.tables WHERE table_schema = '$SCHEMA_NAME';"
    echo "  2. Test the views: SELECT * FROM $SCHEMA_NAME.latest_assessments;"
    echo "  3. Check sample data: SELECT COUNT(*) FROM $SCHEMA_NAME.pain_assessments;"
    echo ""
    print_status "For more information, see README.md"
}

# Run main function
main "$@" 