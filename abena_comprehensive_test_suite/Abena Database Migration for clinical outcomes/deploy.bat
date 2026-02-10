@echo off
REM Abena Clinical Outcomes Database Migration - Windows Deployment Script
REM This script automates the deployment of the clinical outcomes database schema

setlocal enabledelayedexpansion

REM Configuration
if "%DB_HOST%"=="" set DB_HOST=localhost
if "%DB_PORT%"=="" set DB_PORT=5432
if "%DB_NAME%"=="" set DB_NAME=abena_clinical
if "%DB_USER%"=="" set DB_USER=postgres
set SCHEMA_NAME=clinical_outcomes

echo ==========================================
echo Abena Clinical Outcomes Database Migration
echo ==========================================
echo.

echo [INFO] Starting deployment process...
echo [INFO] Database: %DB_NAME%@%DB_HOST%:%DB_PORT%
echo [INFO] User: %DB_USER%
echo [INFO] Schema: %SCHEMA_NAME%
echo.

REM Check if required files exist
echo [INFO] Checking required files...
if not exist "abena_clinical_outcomes_migration.sql" (
    echo [ERROR] Required file not found: abena_clinical_outcomes_migration.sql
    exit /b 1
)
if not exist "sample_data.sql" (
    echo [ERROR] Required file not found: sample_data.sql
    exit /b 1
)
echo [SUCCESS] All required files found

REM Check if PostgreSQL is available
echo [INFO] Checking PostgreSQL connection...
psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot connect to PostgreSQL database. Please check your connection parameters:
    echo [ERROR]   Host: %DB_HOST%
    echo [ERROR]   Port: %DB_PORT%
    echo [ERROR]   Database: %DB_NAME%
    echo [ERROR]   User: %DB_USER%
    echo.
    echo [ERROR] You can set these using environment variables:
    echo [ERROR]   DB_HOST, DB_PORT, DB_NAME, DB_USER
    exit /b 1
)
echo [SUCCESS] PostgreSQL connection successful

REM Check for existing schema
echo [INFO] Checking for existing schema...
psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '%SCHEMA_NAME%');" | findstr "t" >nul
if not errorlevel 1 (
    echo [WARNING] Schema '%SCHEMA_NAME%' already exists
    if "%FORCE_DEPLOY%"=="true" (
        echo [WARNING] Force deploy enabled - will drop existing schema
        set backup_file=backup_%SCHEMA_NAME%_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
        set backup_file=!backup_file: =0!
        echo [INFO] Creating backup: !backup_file!
        pg_dump -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -n "%SCHEMA_NAME%" > "!backup_file!"
        if errorlevel 1 (
            echo [ERROR] Failed to create backup
            exit /b 1
        )
        echo [SUCCESS] Backup created: !backup_file!
    ) else (
        echo [ERROR] Schema '%SCHEMA_NAME%' already exists. Use FORCE_DEPLOY=true to overwrite.
        exit /b 1
    )
) else (
    echo [INFO] Schema '%SCHEMA_NAME%' does not exist - proceeding with fresh installation
)

REM Run the migration
echo [INFO] Running database migration...
if "%FORCE_DEPLOY%"=="true" (
    echo [INFO] Dropping existing schema...
    psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -c "DROP SCHEMA IF EXISTS %SCHEMA_NAME% CASCADE;"
)

echo [INFO] Executing migration script...
psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -f "abena_clinical_outcomes_migration.sql"
if errorlevel 1 (
    echo [ERROR] Migration failed
    exit /b 1
)
echo [SUCCESS] Migration completed successfully

REM Insert sample data
if "%INSERT_SAMPLE_DATA%"=="true" (
    echo [INFO] Inserting sample data...
    psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -f "sample_data.sql"
    if errorlevel 1 (
        echo [ERROR] Sample data insertion failed
        exit /b 1
    )
    echo [SUCCESS] Sample data inserted successfully
) else (
    echo [INFO] Skipping sample data insertion (set INSERT_SAMPLE_DATA=true to include)
)

REM Verify the installation
echo [INFO] Verifying installation...

REM Check if schema exists
psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '%SCHEMA_NAME%');" | findstr "t" >nul
if errorlevel 1 (
    echo [ERROR] Schema verification failed - schema does not exist
    exit /b 1
)

REM Check if tables were created
for /f "tokens=*" %%i in ('psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '%SCHEMA_NAME%';"') do set table_count=%%i
set table_count=!table_count: =!
if !table_count! lss 10 (
    echo [ERROR] Schema verification failed - expected at least 10 tables, found !table_count!
    exit /b 1
)
echo [SUCCESS] Schema verification successful - !table_count! tables created

REM Check if views were created
for /f "tokens=*" %%i in ('psql -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = '%SCHEMA_NAME%';"') do set view_count=%%i
set view_count=!view_count: =!
if !view_count! lss 3 (
    echo [ERROR] Views verification failed - expected at least 3 views, found !view_count!
    exit /b 1
)
echo [SUCCESS] Views verification successful - !view_count! views created

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo [INFO] Next steps:
echo   1. Review the created schema: SELECT * FROM information_schema.tables WHERE table_schema = '%SCHEMA_NAME%';
echo   2. Test the views: SELECT * FROM %SCHEMA_NAME%.latest_assessments;
echo   3. Check sample data: SELECT COUNT(*) FROM %SCHEMA_NAME%.pain_assessments;
echo.
echo [INFO] For more information, see README.md

endlocal 