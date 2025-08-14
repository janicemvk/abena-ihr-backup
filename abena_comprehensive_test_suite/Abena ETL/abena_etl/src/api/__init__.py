"""
Abena IHR System - API Package

This package contains the REST API endpoints and web service interfaces
for the Abena IHR System.

Components:
    main: FastAPI application setup and main endpoints
    routers: API route handlers for different functional areas
    middleware: Authentication, logging, and security middleware
"""

from .main import app

__all__ = [
    'app',
    'main',
    'routers',
    'middleware'
] 