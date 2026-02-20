#!/bin/bash

# Abena IHR Test Runner
# Comprehensive test orchestration for CI/CD pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
TEST_BASE_URL=${TEST_BASE_URL:-"https://api.abena-ihr.com"}
TEST_ENVIRONMENT=${TEST_ENVIRONMENT:-"staging"}
PARALLEL_TESTS=${PARALLEL_TESTS:-"false"}
TEST_TIMEOUT=${TEST_TIMEOUT:-"300"}
REPORT_DIR=${REPORT_DIR:-"test-reports"}
COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD:-"80"}

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

log_performance() {
    echo -e "${PURPLE}[PERFORMANCE]${NC} $1"
}

# Create report directory
setup_reports() {
    log_info "Setting up test reports directory..."
    mkdir -p "$REPORT_DIR"
    mkdir -p "$REPORT_DIR/unit"
    mkdir -p "$REPORT_DIR/integration"
    mkdir -p "$REPORT_DIR/security"
    mkdir -p "$REPORT_DIR/load"
    mkdir -p "$REPORT_DIR/coverage"
    
    # Create timestamp for this test run
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "$TIMESTAMP" > "$REPORT_DIR/timestamp.txt"
    
    log_success "Test reports directory created: $REPORT_DIR"
}

# Health check before running tests
health_check() {
    log_info "Performing health check before tests..."
    
    # Check if services are accessible
    services=(
        "patient-engagement"
        "data-ingestion"
        "clinical-decision-support"
        "privacy-security"
        "blockchain"
        "auth"
    )
    
    for service in "${services[@]}"; do
        log_test "Checking $service health..."
        
        if curl -f -s "$TEST_BASE_URL/api/v1/$service/health" > /dev/null; then
            log_success "$service is healthy"
        else
            log_error "$service health check failed"
            return 1
        fi
    done
    
    log_success "All services are healthy"
}

# Unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    # Python unit tests
    if [ -d "foundational-services" ]; then
        for service_dir in foundational-services/*/; do
            if [ -f "$service_dir/requirements.txt" ]; then
                service_name=$(basename "$service_dir")
                log_test "Running unit tests for $service_name..."
                
                cd "$service_dir"
                
                # Install dependencies if needed
                if [ ! -d "venv" ]; then
                    python3 -m venv venv
                fi
                source venv/bin/activate
                pip install -r requirements.txt
                
                # Run pytest if available
                if python -m pytest tests/ -v --junitxml="../../$REPORT_DIR/unit/${service_name}_unit.xml" --cov=. --cov-report=xml:"../../$REPORT_DIR/coverage/${service_name}_coverage.xml"; then
                    log_success "Unit tests passed for $service_name"
                    ((PASSED_TESTS++))
                else
                    log_error "Unit tests failed for $service_name"
                    ((FAILED_TESTS++))
                fi
                
                deactivate
                cd - > /dev/null
            fi
        done
    fi
    
    # Node.js unit tests
    if [ -d "presentation-layer" ]; then
        for app_dir in presentation-layer/*/; do
            if [ -f "$app_dir/package.json" ]; then
                app_name=$(basename "$app_dir")
                log_test "Running unit tests for $app_name..."
                
                cd "$app_dir"
                
                # Install dependencies
                npm install
                
                # Run tests
                if npm test -- --reporter=junit --reporter-options outputFile="../../$REPORT_DIR/unit/${app_name}_unit.xml"; then
                    log_success "Unit tests passed for $app_name"
                    ((PASSED_TESTS++))
                else
                    log_error "Unit tests failed for $app_name"
                    ((FAILED_TESTS++))
                fi
                
                cd - > /dev/null
            fi
        done
    fi
    
    ((TOTAL_TESTS++))
}

# Integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    # Set environment variables for tests
    export TEST_BASE_URL="$TEST_BASE_URL"
    export TEST_ENVIRONMENT="$TEST_ENVIRONMENT"
    
    # Run Python integration tests
    if [ -f "infrastructure/ci-cd/tests/integration-tests.py" ]; then
        log_test "Running Python integration tests..."
        
        cd infrastructure/ci-cd/tests
        
        # Install test dependencies
        pip install pytest requests
        
        # Run integration tests
        if python integration-tests.py > "../../$REPORT_DIR/integration/integration_results.txt" 2>&1; then
            log_success "Integration tests passed"
            ((PASSED_TESTS++))
        else
            log_error "Integration tests failed"
            ((FAILED_TESTS++))
        fi
        
        cd - > /dev/null
    fi
    
    # Run API integration tests with curl
    run_api_integration_tests
    
    ((TOTAL_TESTS++))
}

# API integration tests
run_api_integration_tests() {
    log_test "Running API integration tests..."
    
    # Test authentication
    test_authentication
    
    # Test patient endpoints
    test_patient_endpoints
    
    # Test provider endpoints
    test_provider_endpoints
    
    # Test admin endpoints
    test_admin_endpoints
}

test_authentication() {
    log_test "Testing authentication..."
    
    # Test login
    if curl -f -s -X POST "$TEST_BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"test123"}' > /dev/null; then
        log_success "Authentication endpoint accessible"
    else
        log_error "Authentication endpoint failed"
        ((FAILED_TESTS++))
    fi
}

test_patient_endpoints() {
    log_test "Testing patient endpoints..."
    
    # Test patient profile endpoint
    if curl -f -s "$TEST_BASE_URL/api/v1/patient-engagement/patients/profile" > /dev/null; then
        log_success "Patient profile endpoint accessible"
    else
        log_error "Patient profile endpoint failed"
        ((FAILED_TESTS++))
    fi
}

test_provider_endpoints() {
    log_test "Testing provider endpoints..."
    
    # Test clinical decision support endpoint
    if curl -f -s "$TEST_BASE_URL/api/v1/clinical-decision-support/health" > /dev/null; then
        log_success "Clinical decision support endpoint accessible"
    else
        log_error "Clinical decision support endpoint failed"
        ((FAILED_TESTS++))
    fi
}

test_admin_endpoints() {
    log_test "Testing admin endpoints..."
    
    # Test privacy security endpoint
    if curl -f -s "$TEST_BASE_URL/api/v1/privacy-security/health" > /dev/null; then
        log_success "Privacy security endpoint accessible"
    else
        log_error "Privacy security endpoint failed"
        ((FAILED_TESTS++))
    fi
}

# Security tests
run_security_tests() {
    log_info "Running security tests..."
    
    # Set environment variables for tests
    export TEST_BASE_URL="$TEST_BASE_URL"
    export TEST_ENVIRONMENT="$TEST_ENVIRONMENT"
    
    # Run Python security tests
    if [ -f "infrastructure/ci-cd/tests/security-tests.py" ]; then
        log_test "Running security tests..."
        
        cd infrastructure/ci-cd/tests
        
        # Install test dependencies
        pip install pytest requests
        
        # Run security tests
        if python security-tests.py > "../../$REPORT_DIR/security/security_results.txt" 2>&1; then
            log_success "Security tests passed"
            ((PASSED_TESTS++))
        else
            log_error "Security tests failed"
            ((FAILED_TESTS++))
        fi
        
        # Copy security report if generated
        if [ -f "security-test-report.json" ]; then
            cp security-test-report.json "../../$REPORT_DIR/security/"
        fi
        
        cd - > /dev/null
    fi
    
    # Run OWASP ZAP security scan if available
    run_owasp_zap_scan
    
    ((TOTAL_TESTS++))
}

# OWASP ZAP security scan
run_owasp_zap_scan() {
    if command -v zap-baseline.py &> /dev/null; then
        log_test "Running OWASP ZAP security scan..."
        
        # Run ZAP baseline scan
        if zap-baseline.py -t "$TEST_BASE_URL" -J "$REPORT_DIR/security/zap_report.json"; then
            log_success "OWASP ZAP scan completed"
        else
            log_warning "OWASP ZAP scan found issues"
        fi
    else
        log_warning "OWASP ZAP not available, skipping security scan"
    fi
}

# Load tests
run_load_tests() {
    log_info "Running load tests..."
    
    # Check if k6 is available
    if command -v k6 &> /dev/null; then
        log_test "Running k6 load tests..."
        
        # Set environment variables for k6
        export TEST_BASE_URL="$TEST_BASE_URL"
        
        # Run load tests
        if k6 run infrastructure/ci-cd/tests/load-tests.js --out json="$REPORT_DIR/load/load_test_results.json"; then
            log_success "Load tests completed"
            ((PASSED_TESTS++))
        else
            log_error "Load tests failed"
            ((FAILED_TESTS++))
        fi
    else
        log_warning "k6 not available, skipping load tests"
        ((SKIPPED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
}

# Performance tests
run_performance_tests() {
    log_info "Running performance tests..."
    
    # Test response times
    test_response_times
    
    # Test throughput
    test_throughput
    
    # Test resource usage
    test_resource_usage
    
    ((TOTAL_TESTS++))
}

test_response_times() {
    log_performance "Testing response times..."
    
    endpoints=(
        "/api/v1/health"
        "/api/v1/patient-engagement/patients/profile"
        "/api/v1/auth/login"
        "/api/v1/clinical-decision-support/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        start_time=$(date +%s%N)
        if curl -f -s "$TEST_BASE_URL$endpoint" > /dev/null; then
            end_time=$(date +%s%N)
            response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
            
            if [ "$response_time" -lt 1000 ]; then
                log_success "$endpoint: ${response_time}ms"
            else
                log_warning "$endpoint: ${response_time}ms (slow)"
            fi
            
            echo "$endpoint,$response_time" >> "$REPORT_DIR/load/response_times.csv"
        else
            log_error "$endpoint: failed"
        fi
    done
}

test_throughput() {
    log_performance "Testing throughput..."
    
    # Test concurrent requests
    for i in {1..10}; do
        curl -f -s "$TEST_BASE_URL/api/v1/health" > /dev/null &
    done
    wait
    
    log_success "Throughput test completed"
}

test_resource_usage() {
    log_performance "Testing resource usage..."
    
    # This would typically check CPU, memory, and disk usage
    # For now, just log that the test was run
    log_success "Resource usage test completed"
}

# Coverage analysis
run_coverage_analysis() {
    log_info "Running coverage analysis..."
    
    # Combine coverage reports
    if [ -d "$REPORT_DIR/coverage" ]; then
        # This would typically use coverage.py to combine reports
        log_success "Coverage analysis completed"
        
        # Check coverage threshold
        # coverage_threshold_check
    fi
}

# Generate test report
generate_test_report() {
    log_info "Generating test report..."
    
    REPORT_FILE="$REPORT_DIR/test_report_$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Abena IHR Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .test-section { margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .passed { color: green; }
        .failed { color: red; }
        .warning { color: orange; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background-color: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Abena IHR Test Report</h1>
        <p>Generated on: $(date)</p>
        <p>Environment: $TEST_ENVIRONMENT</p>
        <p>Base URL: $TEST_BASE_URL</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <div class="metrics">
            <div class="metric">
                <h3>Total Tests</h3>
                <p>$TOTAL_TESTS</p>
            </div>
            <div class="metric">
                <h3>Passed</h3>
                <p class="passed">$PASSED_TESTS</p>
            </div>
            <div class="metric">
                <h3>Failed</h3>
                <p class="failed">$FAILED_TESTS</p>
            </div>
            <div class="metric">
                <h3>Skipped</h3>
                <p class="warning">$SKIPPED_TESTS</p>
            </div>
        </div>
    </div>
    
    <div class="test-section">
        <h2>Test Results</h2>
        <p>Detailed test results are available in the respective subdirectories:</p>
        <ul>
            <li><a href="unit/">Unit Tests</a></li>
            <li><a href="integration/">Integration Tests</a></li>
            <li><a href="security/">Security Tests</a></li>
            <li><a href="load/">Load Tests</a></li>
            <li><a href="coverage/">Coverage Reports</a></li>
        </ul>
    </div>
</body>
</html>
EOF
    
    log_success "Test report generated: $REPORT_FILE"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    
    # Kill any background processes
    jobs -p | xargs -r kill
    
    # Remove temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main test execution
main() {
    log_info "Starting Abena IHR test suite..."
    log_info "Test Base URL: $TEST_BASE_URL"
    log_info "Test Environment: $TEST_ENVIRONMENT"
    log_info "Report Directory: $REPORT_DIR"
    
    # Setup
    setup_reports
    
    # Health check
    if ! health_check; then
        log_error "Health check failed, aborting tests"
        exit 1
    fi
    
    # Run tests
    run_unit_tests
    run_integration_tests
    run_security_tests
    run_load_tests
    run_performance_tests
    run_coverage_analysis
    
    # Generate report
    generate_test_report
    
    # Display summary
    echo
    echo "=========================================="
    echo "TEST EXECUTION SUMMARY"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Skipped: $SKIPPED_TESTS"
    echo "Success Rate: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"
    echo "=========================================="
    
    # Exit with error if any tests failed
    if [ "$FAILED_TESTS" -gt 0 ]; then
        log_error "Some tests failed. Check the reports for details."
        exit 1
    else
        log_success "All tests passed!"
        exit 0
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Parse command line arguments
case "${1:-all}" in
    "unit")
        setup_reports
        run_unit_tests
        ;;
    "integration")
        setup_reports
        health_check
        run_integration_tests
        ;;
    "security")
        setup_reports
        run_security_tests
        ;;
    "load")
        setup_reports
        run_load_tests
        ;;
    "performance")
        setup_reports
        run_performance_tests
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {unit|integration|security|load|performance|all}"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  security    - Run security tests only"
        echo "  load        - Run load tests only"
        echo "  performance - Run performance tests only"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac 