# Abena Clinical Outcomes Database - System Test Script
# This script tests the database deployment and functionality

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Abena Clinical Outcomes Database Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PGPASSWORD = "2114***Million"
$env:DB_NAME = "abena_clinical_data"

Write-Host "[INFO] Testing database connection..." -ForegroundColor Yellow

# Test 1: Check if schema exists
Write-Host "[TEST 1] Checking if clinical_outcomes schema exists..." -ForegroundColor Green
try {
    $result = psql -U postgres -d abena_clinical_data -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'clinical_outcomes');" 2>$null
    if ($result -match "t") {
        Write-Host "[SUCCESS] Schema 'clinical_outcomes' exists" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Schema 'clinical_outcomes' does not exist" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to check schema: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Check if tables were created
Write-Host "[TEST 2] Checking if tables were created..." -ForegroundColor Green
try {
    $tables = @(
        "pain_assessments",
        "womac_assessments", 
        "odi_assessments",
        "medication_usage",
        "healthcare_utilization",
        "quality_of_life",
        "weekly_symptom_tracking",
        "treatment_satisfaction",
        "assessment_schedules",
        "outcome_changes"
    )
    
    $missing_tables = @()
    foreach ($table in $tables) {
        $result = psql -U postgres -d abena_clinical_data -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'clinical_outcomes' AND table_name = '$table');" 2>$null
        if ($result -notmatch "t") {
            $missing_tables += $table
        }
    }
    
    if ($missing_tables.Count -eq 0) {
        Write-Host "[SUCCESS] All expected tables exist" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Missing tables: $($missing_tables -join ', ')" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Failed to check tables: $_" -ForegroundColor Red
}

# Test 3: Check if views were created
Write-Host "[TEST 3] Checking if views were created..." -ForegroundColor Green
try {
    $views = @(
        "latest_assessments",
        "baseline_assessments", 
        "data_quality_summary"
    )
    
    $missing_views = @()
    foreach ($view in $views) {
        $result = psql -U postgres -d abena_clinical_data -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.views WHERE table_schema = 'clinical_outcomes' AND table_name = '$view');" 2>$null
        if ($result -notmatch "t") {
            $missing_views += $view
        }
    }
    
    if ($missing_views.Count -eq 0) {
        Write-Host "[SUCCESS] All expected views exist" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Missing views: $($missing_views -join ', ')" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Failed to check views: $_" -ForegroundColor Red
}

# Test 4: Check if sample data was inserted
Write-Host "[TEST 4] Checking if sample data was inserted..." -ForegroundColor Green
try {
    $result = psql -U postgres -d abena_clinical_data -t -c "SELECT COUNT(*) FROM clinical_outcomes.pain_assessments;" 2>$null
    $count = $result.Trim()
    if ($count -gt 0) {
        Write-Host "[SUCCESS] Sample data found: $count pain assessment records" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] No sample data found in pain_assessments" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Failed to check sample data: $_" -ForegroundColor Red
}

# Test 5: Test a simple query
Write-Host "[TEST 5] Testing a simple query..." -ForegroundColor Green
try {
    $result = psql -U postgres -d abena_clinical_data -c "SELECT patient_id, assessment_date, pain_score FROM clinical_outcomes.pain_assessments LIMIT 3;" 2>$null
    Write-Host "[SUCCESS] Query executed successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to execute test query: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan 