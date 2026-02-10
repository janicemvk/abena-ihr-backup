"""
Abena IHR Security Module Setup

This module provides comprehensive security, compliance, and configuration management
for the Abena IHR (Integrated Health Records) system following Abena SDK patterns.
"""

from setuptools import setup, find_packages
import os

# Read the README file


def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements


def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []


setup(
    name="abena-ihr-security",
    version="1.0.0",
    author="Abena Development Team",
    author_email="dev@abenahealthcare.com",
    description="Security, Compliance & Configuration Management for Abena IHR",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/abenahealthcare/abena-ihr-security",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: Proprietary",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Healthcare",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "bandit>=1.7.5",
            "safety>=2.3.5",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "abena-ihr-security=abena_ihr_security.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "abena_ihr_security": [
            "config/*.json",
            "schemas/*.json",
            "templates/*.html",
        ],
    },
    keywords="healthcare security compliance hipaa encryption audit",
    project_urls={
        "Bug Reports": "https://github.com/abenahealthcare/abena-ihr-security/issues",
        "Source": "https://github.com/abenahealthcare/abena-ihr-security",
        "Documentation": "https://abena-ihr-security.readthedocs.io/",
    },
)
