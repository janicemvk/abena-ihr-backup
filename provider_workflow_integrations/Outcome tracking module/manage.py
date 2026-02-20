#!/usr/bin/env python3
"""
Management script for the Outcome Tracking Module
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")
        return False


def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")


def run_migrations():
    """Run database migrations"""
    return run_command("alembic upgrade head", "Running database migrations")


def create_migration(message):
    """Create a new migration"""
    if not message:
        message = input("Enter migration message: ")
    return run_command(f'alembic revision --autogenerate -m "{message}"', "Creating migration")


def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    reload_flag = "--reload" if reload else ""
    command = f"uvicorn app.main:app --host {host} --port {port} {reload_flag}"
    return run_command(command, "Starting FastAPI server")


def run_tests():
    """Run the test suite"""
    return run_command("pytest tests/ -v", "Running tests")


def show_help():
    """Show help information"""
    help_text = """
Outcome Tracking Module Management Script

Usage: python manage.py <command> [options]

Commands:
    install          Install Python dependencies
    migrate          Run database migrations
    makemigration    Create a new migration (will prompt for message)
    server           Start the FastAPI server
    test             Run the test suite
    help             Show this help message

Examples:
    python manage.py install
    python manage.py migrate
    python manage.py makemigration "Add new outcome types"
    python manage.py server
    python manage.py test
    """
    print(help_text)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_dependencies()
    elif command == "migrate":
        run_migrations()
    elif command == "makemigration":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_migration(message)
    elif command == "server":
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        start_server(host, port)
    elif command == "test":
        run_tests()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main() 