"""
Test Suite for Abena IHR System

This package contains comprehensive tests for all components of the
Abena Intelligent Health Recommendation System.

Test Categories:
- Unit Tests: Individual component testing
- Integration Tests: Cross-module interactions
- End-to-End Tests: Complete workflows
- Performance Tests: Speed and scalability
- Security Tests: Data protection and compliance

Usage:
    Run all tests: pytest
    Run specific category: pytest -m unit
    Run with coverage: pytest --cov=src
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

__version__ = "1.0.0" 