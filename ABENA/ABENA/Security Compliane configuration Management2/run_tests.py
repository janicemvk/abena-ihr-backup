#!/usr/bin/env python3
"""
Test Runner for Abena IHR Security Module

This script provides a comprehensive test runner that can:
- Run unit tests
- Run integration tests
- Run examples
- Generate coverage reports
- Run security scans
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command, description, exit_on_failure=True):
    """Run a command and handle the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")

    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    end_time = time.time()

    print(f"Exit code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")

    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)

    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)

    if result.returncode != 0 and exit_on_failure:
        print(f"\n❌ {description} failed!")
        sys.exit(result.returncode)
    else:
        print(f"\n✅ {description} completed successfully!")

    return result.returncode == 0


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "black",
        "flake8",
        "mypy",
        "bandit"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    print("✅ All dependencies are installed")
    return True


def run_unit_tests():
    """Run unit tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "--cov=abena_ihr_security", "--cov-report=term-missing"],
        "Unit Tests"
    )


def run_integration_tests():
    """Run integration tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/integration/",
            "--cov=abena_ihr_security", "--cov-report=term-missing"],
        "Integration Tests"
    )


def run_all_tests():
    """Run all tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "--cov=abena_ihr_security",
            "--cov-report=term-missing", "--cov-report=html:htmlcov"],
        "All Tests"
    )


def run_code_quality_checks():
    """Run code quality checks"""
    checks = [
        (["python", "-m", "black", "--check", "abena_ihr_security/", "tests/", "examples/"], "Code Formatting (Black)"),
        (["python", "-m", "flake8", "abena_ihr_security/", "tests/", "examples/"], "Liinnting (Flake8)"),
        (["python", "-m", "mypy", "abena_ihr_security/", "tests/", "examples/"], "Type Checkg (MyPy)"),
        (["python", "-m", "bandit", "-r", "abena_ihr_security/", "-f", "json"], "Security Scanning (Bandit)")
    ]

    all_passed = True
    for command, description in checks:
        if not run_command(command, description, exit_on_failure=False):
            all_passed = False

    return all_passed


def run_examples():
    """Run example scripts"""
    examples = [
        ("examples/basic_usage.py", "Basic Usage Example"),
        ("examples/advanced_workflow.py", "Advanced Workflow Example")
    ]

    all_passed = True
    for example_path, description in examples:
        if os.path.exists(example_path):
            if not run_command(["python", example_path], description, exit_on_failure=False):
                all_passed = False
        else:
            print(f"⚠️  Example not found: {example_path}")

    return all_passed


def generate_coverage_report():
    """Generate comprehensive coverage report"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "--cov=abena_ihr_security", "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml", "--cov-report=term-missing"],
        "Coverage Report Generation"
    )


def run_performance_tests():
    """Run performance tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "-m", "performance", "-v"],
        "Performance Tests"
    )


def run_security_tests():
    """Run security tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "-m", "security", "-v"],
        "Security Tests"
    )


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Abena IHR Security Module Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--quality", action="store_true", help="Run code quality checks only")
    parser.add_argument("--examples", action="store_true", help="Run examples only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")

    args = parser.parse_args()

    print("🚀 Abena IHR Security Module Test Runner")
    print("=" * 60)

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    success = True

    if args.check_deps:
        return  # Already checked dependencies

    if args.unit:
        success = run_unit_tests() and success
    elif args.integration:
        success = run_integration_tests() and success
    elif args.quality:
        success = run_code_quality_checks() and success
    elif args.examples:
        success = run_examples() and success
    elif args.coverage:
        success = generate_coverage_report() and success
    elif args.performance:
        success = run_performance_tests() and success
    elif args.security:
        success = run_security_tests() and success
    elif args.all:
        print("\n🔍 Running comprehensive test suite...")
        success = run_code_quality_checks() and success
        success = run_unit_tests() and success
        success = run_integration_tests() and success
        success = run_security_tests() and success
        success = run_performance_tests() and success
        success = run_examples() and success
        success = generate_coverage_report() and success
    else:
        # Default: run all tests
        print("\n🔍 Running default test suite...")
        success = run_all_tests() and success
        success = run_code_quality_checks() and success
        success = run_examples() and success

    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("📊 Coverage report available in: htmlcov/index.html")
        print("📋 Test results available in: coverage.xml")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
