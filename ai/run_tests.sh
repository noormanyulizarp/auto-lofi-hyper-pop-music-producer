#!/bin/bash

# Test Runner Script for Auto Music Producer AI
# This script runs all unit tests, integration tests, and generates reports

set -e  # Exit on any error

# Color definitions for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
PROJECT_ROOT="/root/auto-music-producer/ai"
TEST_DIR="$PROJECT_ROOT/tests"
REPORT_DIR="$PROJECT_ROOT/test-reports"
COVERAGE_DIR="$PROJECT_ROOT/coverage"
PYTHON_PATH="/usr/bin/python3"
PYTEST_CMD="pytest"

# Test categories
UNIT_TESTS="unit"
INTEGRATION_TESTS="integration"
API_TESTS="api"
PERFORMANCE_TESTS="performance"

# Create necessary directories
mkdir -p "$REPORT_DIR"
mkdir -p "$COVERAGE_DIR"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Function to display help
show_help() {
    echo "Test Runner Script for Auto Music Producer AI"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -u, --unit              Run unit tests only"
    echo "  -i, --integration       Run integration tests only"
    echo "  -a, --api               Run API tests only"
    echo "  -p, --performance       Run performance tests only"
    echo "  -c, --coverage          Generate coverage report"
    echo "  -v, --verbose           Verbose output"
    echo "  -x, --xdist             Run tests in parallel"
    echo "  -b, --benchmark         Include benchmark tests"
    echo "  -s, --slow              Include slow tests"
    echo "  -r, --report DIR        Custom report directory"
    echo "  -j, --jobs N            Number of parallel jobs (default: auto)"
    echo "  -f, --failfast          Stop on first failure"
    echo "  --all                  Run all tests (default)"
    echo ""
    echo "Examples:"
    echo "  $0 --all                Run all tests with default settings"
    echo "  $0 -u -c                Run unit tests with coverage"
    echo "  $0 -i -x -j 4           Run integration tests in parallel with 4 jobs"
    echo "  $0 -a -v                Run API tests with verbose output"
    echo ""
}

# Parse command line arguments
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_API=false
RUN_PERFORMANCE=false
RUN_ALL=true
GENERATE_COVERAGE=false
VERBOSE=false
USE_XDIST=false
INCLUDE_BENCHMARK=false
INCLUDE_SLOW=false
FAILFAST=false
JOBS="auto"
CUSTOM_REPORT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--unit)
            RUN_UNIT=true
            RUN_ALL=false
            shift
            ;;
        -i|--integration)
            RUN_INTEGRATION=true
            RUN_ALL=false
            shift
            ;;
        -a|--api)
            RUN_API=true
            RUN_ALL=false
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=true
            RUN_ALL=false
            shift
            ;;
        -c|--coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -x|--xdist)
            USE_XDIST=true
            shift
            ;;
        -b|--benchmark)
            INCLUDE_BENCHMARK=true
            shift
            ;;
        -s|--slow)
            INCLUDE_SLOW=true
            shift
            ;;
        -r|--report)
            CUSTOM_REPORT_DIR="$2"
            shift 2
            ;;
        -j|--jobs)
            JOBS="$2"
            shift 2
            ;;
        -f|--failfast)
            FAILFAST=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set custom report directory if provided
if [[ -n "$CUSTOM_REPORT_DIR" ]]; then
    REPORT_DIR="$CUSTOM_REPORT_DIR"
    mkdir -p "$REPORT_DIR"
fi

# Build pytest command
PYTEST_ARGS=()

# Add verbosity
if [[ "$VERBOSE" == true ]]; then
    PYTEST_ARGS+=("-v")
fi

# Add coverage
if [[ "$GENERATE_COVERAGE" == true ]]; then
    PYTEST_ARGS+=("--cov=ai")
    PYTEST_ARGS+=("--cov-report=html:$COVERAGE_DIR")
    PYTEST_ARGS+=("--cov-report=term-missing")
    PYTEST_ARGS+=("--cov-fail-under=80")
fi

# Add xdist for parallel execution
if [[ "$USE_XDIST" == true ]]; then
    PYTEST_ARGS+=("-n")
    PYTEST_ARGS+=("$JOBS")
fi

# Add failfast
if [[ "$FAILFAST" == true ]]; then
    PYTEST_ARGS+=("--failfast")
fi

# Add markers
MARKERS=()

if [[ "$INCLUDE_BENCHMARK" == true ]]; then
    MARKERS+=("benchmark")
fi

if [[ "$INCLUDE_SLOW" != true ]]; then
    MARKERS+=("not slow")
fi

# Add markers to pytest args if any
if [[ ${#MARKERS[@]} -gt 0 ]]; then
    MARKER_STR=$(IFS=" and "; echo "${MARKERS[*]}")
    PYTEST_ARGS+=("-m")
    PYTEST_ARGS+=("$MARKER_STR")
fi

# Add report directory
PYTEST_ARGS+=("--html=$REPORT_DIR/report.html")
PYTEST_ARGS+=("--self-contained-html")
PYTEST_ARGS+=("--json-report")
PYTEST_ARGS+=("--json-report-file=$REPORT_DIR/report.json")

# Function to run tests
run_tests() {
    local test_type="$1"
    local marker="$2"
    local description="$3"
    
    log "Running $description..."
    
    # Create test-specific report directory
    local test_report_dir="$REPORT_DIR/$test_type"
    mkdir -p "$test_report_dir"
    
    # Build pytest command for this test type
    local test_cmd=("$PYTEST_CMD")
    test_cmd+=("${PYTEST_ARGS[@]}")
    test_cmd+=("--html=$test_report_dir/report.html")
    test_cmd+=("--json-report-file=$test_report_dir/report.json")
    
    if [[ -n "$marker" ]]; then
        test_cmd+=("-m")
        test_cmd+=("$marker")
    fi
    
    # Run tests
    local exit_code=0
    if [[ "$VERBOSE" == true ]]; then
        "${test_cmd[@]}" || exit_code=$?
    else
        "${test_cmd[@]}" > /dev/null 2>&1 || exit_code=$?
    fi
    
    if [[ $exit_code -eq 0 ]]; then
        log "$description completed successfully"
    else
        error "$description failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Function to generate summary report
generate_summary_report() {
    log "Generating summary report..."
    
    local summary_file="$REPORT_DIR/summary.md"
    
    echo "# Test Execution Summary" > "$summary_file"
    echo "" >> "$summary_file"
    echo "Generated on: $(date)" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Add overall status
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local skipped_tests=0
    
    if [[ "$RUN_ALL" == true || "$RUN_UNIT" == true ]]; then
        if [[ -f "$REPORT_DIR/unit/report.json" ]]; then
            local unit_tests=$(jq '.summary.total' "$REPORT_DIR/unit/report.json" 2>/dev/null || echo "0")
            local unit_passed=$(jq '.summary.passed' "$REPORT_DIR/unit/report.json" 2>/dev/null || echo "0")
            local unit_failed=$(jq '.summary.failed' "$REPORT_DIR/unit/report.json" 2>/dev/null || echo "0")
            local unit_skipped=$(jq '.summary.skipped' "$REPORT_DIR/unit/report.json" 2>/dev/null || echo "0")
            
            echo "## Unit Tests" >> "$summary_file"
            echo "- Total: $unit_tests" >> "$summary_file"
            echo "- Passed: $unit_passed" >> "$summary_file"
            echo "- Failed: $unit_failed" >> "$summary_file"
            echo "- Skipped: $unit_skipped" >> "$summary_file"
            echo "" >> "$summary_file"
            
            total_tests=$((total_tests + unit_tests))
            passed_tests=$((passed_tests + unit_passed))
            failed_tests=$((failed_tests + unit_failed))
            skipped_tests=$((skipped_tests + unit_skipped))
        fi
    fi
    
    if [[ "$RUN_ALL" == true || "$RUN_INTEGRATION" == true ]]; then
        if [[ -f "$REPORT_DIR/integration/report.json" ]]; then
            local integration_tests=$(jq '.summary.total' "$REPORT_DIR/integration/report.json" 2>/dev/null || echo "0")
            local integration_passed=$(jq '.summary.passed' "$REPORT_DIR/integration/report.json" 2>/dev/null || echo "0")
            local integration_failed=$(jq '.summary.failed' "$REPORT_DIR/integration/report.json" 2>/dev/null || echo "0")
            local integration_skipped=$(jq '.summary.skipped' "$REPORT_DIR/integration/report.json" 2>/dev/null || echo "0")
            
            echo "## Integration Tests" >> "$summary_file"
            echo "- Total: $integration_tests" >> "$summary_file"
            echo "- Passed: $integration_passed" >> "$summary_file"
            echo "- Failed: $integration_failed" >> "$summary_file"
            echo "- Skipped: $integration_skipped" >> "$summary_file"
            echo "" >> "$summary_file"
            
            total_tests=$((total_tests + integration_tests))
            passed_tests=$((passed_tests + integration_passed))
            failed_tests=$((failed_tests + integration_failed))
            skipped_tests=$((skipped_tests + integration_skipped))
        fi
    fi
    
    if [[ "$RUN_ALL" == true || "$RUN_API" == true ]]; then
        if [[ -f "$REPORT_DIR/api/report.json" ]]; then
            local api_tests=$(jq '.summary.total' "$REPORT_DIR/api/report.json" 2>/dev/null || echo "0")
            local api_passed=$(jq '.summary.passed' "$REPORT_DIR/api/report.json" 2>/dev/null || echo "0")
            local api_failed=$(jq '.summary.failed' "$REPORT_DIR/api/report.json" 2>/dev/null || echo "0")
            local api_skipped=$(jq '.summary.skipped' "$REPORT_DIR/api/report.json" 2>/dev/null || echo "0")
            
            echo "## API Tests" >> "$summary_file"
            echo "- Total: $api_tests" >> "$summary_file"
            echo "- Passed: $api_passed" >> "$summary_file"
            echo "- Failed: $api_failed" >> "$summary_file"
            echo "- Skipped: $api_skipped" >> "$summary_file"
            echo "" >> "$summary_file"
            
            total_tests=$((total_tests + api_tests))
            passed_tests=$((passed_tests + api_passed))
            failed_tests=$((failed_tests + api_failed))
            skipped_tests=$((skipped_tests + api_skipped))
        fi
    fi
    
    if [[ "$RUN_ALL" == true || "$RUN_PERFORMANCE" == true ]]; then
        if [[ -f "$REPORT_DIR/performance/report.json" ]]; then
            local performance_tests=$(jq '.summary.total' "$REPORT_DIR/performance/report.json" 2>/dev/null || echo "0")
            local performance_passed=$(jq '.summary.passed' "$REPORT_DIR/performance/report.json" 2>/dev/null || echo "0")
            local performance_failed=$(jq '.summary.failed' "$REPORT_DIR/performance/report.json" 2>/dev/null || echo "0")
            local performance_skipped=$(jq '.summary.skipped' "$REPORT_DIR/performance/report.json" 2>/dev/null || echo "0")
            
            echo "## Performance Tests" >> "$summary_file"
            echo "- Total: $performance_tests" >> "$summary_file"
            echo "- Passed: $performance_passed" >> "$summary_file"
            echo "- Failed: $performance_failed" >> "$summary_file"
            echo "- Skipped: $performance_skipped" >> "$summary_file"
            echo "" >> "$summary_file"
            
            total_tests=$((total_tests + performance_tests))
            passed_tests=$((passed_tests + performance_passed))
            failed_tests=$((failed_tests + performance_failed))
            skipped_tests=$((skipped_tests + performance_skipped))
        fi
    fi
    
    # Add overall summary
    echo "## Overall Summary" >> "$summary_file"
    echo "- Total Tests: $total_tests" >> "$summary_file"
    echo "- Passed: $passed_tests" >> "$summary_file"
    echo "- Failed: $failed_tests" >> "$summary_file"
    echo "- Skipped: $skipped_tests" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Calculate pass rate
    if [[ $total_tests -gt 0 ]]; then
        local pass_rate=$((passed_tests * 100 / total_tests))
        echo "- Pass Rate: $pass_rate%" >> "$summary_file"
        echo "" >> "$summary_file"
    fi
    
    # Add coverage information if available
    if [[ "$GENERATE_COVERAGE" == true && -f "$COVERAGE_DIR/index.html" ]]; then
        echo "## Coverage Report" >> "$summary_file"
        echo "- Coverage report generated at: $COVERAGE_DIR/index.html" >> "$summary_file"
        echo "" >> "$summary_file"
    fi
    
    # Add links to detailed reports
    echo "## Detailed Reports" >> "$summary_file"
    echo "" >> "$summary_file"
    
    if [[ -f "$REPORT_DIR/unit/report.html" ]]; then
        echo "- [Unit Tests](unit/report.html)" >> "$summary_file"
    fi
    
    if [[ -f "$REPORT_DIR/integration/report.html" ]]; then
        echo "- [Integration Tests](integration/report.html)" >> "$summary_file"
    fi
    
    if [[ -f "$REPORT_DIR/api/report.html" ]]; then
        echo "- [API Tests](api/report.html)" >> "$summary_file"
    fi
    
    if [[ -f "$REPORT_DIR/performance/report.html" ]]; then
        echo "- [Performance Tests](performance/report.html)" >> "$summary_file"
    fi
    
    if [[ -f "$COVERAGE_DIR/index.html" ]]; then
        echo "- [Coverage Report](../coverage/index.html)" >> "$summary_file"
    fi
    
    echo "" >> "$summary_file"
    echo "*Report generated by Auto Music Producer AI Test Runner*" >> "$summary_file"
    
    log "Summary report generated at: $summary_file"
}

# Main execution
log "Starting test execution..."
log "Project root: $PROJECT_ROOT"
log "Test directory: $TEST_DIR"
log "Report directory: $REPORT_DIR"

# Change to project directory
cd "$PROJECT_ROOT"

# Install test dependencies if needed
if [[ ! -f "$PROJECT_ROOT/test-requirements.txt" ]]; then
    warn "test-requirements.txt not found. Installing test dependencies..."
    # Create basic test requirements
    cat > "$PROJECT_ROOT/test-requirements.txt" << EOF
pytest >= 7.4.3
pytest-asyncio >= 0.21.1
pytest-cov >= 4.1.0
pytest-mock >= 3.12.0
pytest-xdist >= 3.5.0
pytest-benchmark >= 4.0.0
httpx >= 0.25.2
respx >= 0.20.2
pytest-html >= 4.1.1
pytest-json-report >= 1.5.0
EOF
fi

# Install dependencies
log "Installing test dependencies..."
if [[ "$VERBOSE" == true ]]; then
    $PYTHON_PATH -m pip install -r "$PROJECT_ROOT/test-requirements.txt"
else
    $PYTHON_PATH -m pip install -r "$PROJECT_ROOT/test-requirements.txt" > /dev/null 2>&1
fi

# Initialize test execution
OVERALL_EXIT_CODE=0

# Run unit tests
if [[ "$RUN_ALL" == true || "$RUN_UNIT" == true ]]; then
    log "=== Running Unit Tests ==="
    run_tests "unit" "$UNIT_TESTS" "Unit Tests" || OVERALL_EXIT_CODE=$?
fi

# Run integration tests
if [[ "$RUN_ALL" == true || "$RUN_INTEGRATION" == true ]]; then
    log "=== Running Integration Tests ==="
    run_tests "integration" "$INTEGRATION_TESTS" "Integration Tests" || OVERALL_EXIT_CODE=$?
fi

# Run API tests
if [[ "$RUN_ALL" == true || "$RUN_API" == true ]]; then
    log "=== Running API Tests ==="
    run_tests "api" "$API_TESTS" "API Tests" || OVERALL_EXIT_CODE=$?
fi

# Run performance tests
if [[ "$RUN_ALL" == true || "$RUN_PERFORMANCE" == true ]]; then
    log "=== Running Performance Tests ==="
    run_tests "performance" "$PERFORMANCE_TESTS" "Performance Tests" || OVERALL_EXIT_CODE=$?
fi

# Generate summary report
generate_summary_report

# Final status
if [[ $OVERALL_EXIT_CODE -eq 0 ]]; then
    log "=== All tests completed successfully! ==="
    echo ""
    echo "📊 Test Reports:"
    echo "   - Summary: $REPORT_DIR/summary.md"
    echo "   - HTML Reports: $REPORT_DIR/"
    if [[ "$GENERATE_COVERAGE" == true ]]; then
        echo "   - Coverage: $COVERAGE_DIR/index.html"
    fi
    echo ""
    echo "✨ Test execution completed successfully!"
else
    error "=== Some tests failed! ==="
    echo ""
    echo "📊 Test Reports:"
    echo "   - Summary: $REPORT_DIR/summary.md"
    echo "   - HTML Reports: $REPORT_DIR/"
    if [[ "$GENERATE_COVERAGE" == true ]]; then
        echo "   - Coverage: $COVERAGE_DIR/index.html"
    fi
    echo ""
    echo "❌ Test execution completed with failures!"
fi

exit $OVERALL_EXIT_CODE