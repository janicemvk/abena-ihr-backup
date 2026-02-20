#!/usr/bin/env python3
"""
Abena IHR System - Test Runner

This script provides an easy way to run different categories of tests
with proper configuration and reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --performance      # Run performance tests only
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --fast             # Run fast tests only (exclude slow)
    python run_tests.py --verbose          # Verbose output
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle output"""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: pytest not found. Please install: pip install pytest pytest-cov")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Abena IHR System Tests")
    
    # Test category options
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--security', action='store_true', help='Run security tests only')
    parser.add_argument('--clinical', action='store_true', help='Run clinical validation tests only')
    
    # Test execution options
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--fast', action='store_true', help='Exclude slow tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--parallel', '-n', type=int, help='Run tests in parallel (requires pytest-xdist)')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML coverage report')
    
    # File/directory options
    parser.add_argument('--file', help='Run specific test file')
    parser.add_argument('--function', help='Run specific test function')
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Add coverage options
    if args.coverage or args.html_report:
        cmd.extend(['--cov=src', '--cov-report=term-missing'])
        if args.html_report:
            cmd.append('--cov-report=html')
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(['-n', str(args.parallel)])
    
    # Add test filters
    test_markers = []
    test_paths = []
    
    if args.unit:
        test_markers.append('unit')
        test_paths.append('tests/unit/')
    elif args.integration:
        test_markers.append('integration')
        test_paths.append('tests/integration/')
    elif args.e2e:
        test_markers.append('e2e')
        test_paths.append('tests/e2e/')
    elif args.performance:
        test_markers.append('performance')
        test_paths.append('tests/performance/')
    elif args.security:
        test_markers.append('security')
        test_paths.append('tests/security/')
    elif args.clinical:
        test_markers.append('clinical')
    
    # Add fast filter
    if args.fast:
        test_markers.append('not slow')
    
    # Add marker filters
    if test_markers:
        cmd.extend(['-m', ' and '.join(test_markers)])
    
    # Add specific file or function
    if args.file:
        if args.function:
            cmd.append(f"{args.file}::{args.function}")
        else:
            cmd.append(args.file)
    elif args.function:
        cmd.extend(['-k', args.function])
    elif test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append('tests/')
    
    # Display test configuration
    print("🧪 Abena IHR System - Test Runner")
    print("=" * 50)
    print(f"Project Directory: {project_dir}")
    print(f"Test Command: {' '.join(cmd)}")
    
    if test_markers:
        print(f"Test Markers: {', '.join(test_markers)}")
    if test_paths:
        print(f"Test Paths: {', '.join(test_paths)}")
    
    print()
    
    # Check if pytest is available
    try:
        subprocess.run(['python', '-m', 'pytest', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest not found. Installing required packages...")
        install_cmd = [sys.executable, '-m', 'pip', 'install', 
                      'pytest', 'pytest-cov', 'pytest-mock']
        if args.parallel:
            install_cmd.append('pytest-xdist')
        
        subprocess.run(install_cmd, check=True)
        print("✅ Test dependencies installed")
    
    # Run the tests
    success = run_command(cmd, "Running Abena IHR Tests")
    
    # Generate summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        if args.coverage or args.html_report:
            print("📊 Coverage report generated")
            if args.html_report:
                print("📄 HTML report: htmlcov/index.html")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
    
    # Show additional information
    print("\n📋 Test Categories Available:")
    print("  --unit          : Individual component tests")
    print("  --integration   : Cross-module interaction tests")
    print("  --e2e          : End-to-end workflow tests")
    print("  --performance  : Speed and load tests")
    print("  --security     : Security and compliance tests")
    print("  --clinical     : Clinical accuracy validation")
    print("\n📊 Coverage and Reporting:")
    print("  --coverage     : Generate coverage report")
    print("  --html-report  : Generate HTML coverage report")
    print("\n⚡ Performance Options:")
    print("  --fast         : Exclude slow tests")
    print("  --parallel N   : Run tests in parallel")


if __name__ == "__main__":
    main() 