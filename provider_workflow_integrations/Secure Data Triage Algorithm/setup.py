"""
Setup script for Abena Secure Data Triage Algorithm
"""

from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="abena-secure-data-triage",
    version="1.0.0",
    description="Secure data triage algorithm for Abena IHR blockchain storage",
    long_description="""
    A comprehensive secure data triage algorithm designed for the Abena Integrated Health Record (IHR) system.
    This algorithm implements multi-layer security and privacy-preserving techniques including:
    
    - Data sensitivity classification (PUBLIC, STATISTICAL, CLINICAL, PERSONAL, SENSITIVE)
    - PII detection and anonymization
    - Consent verification
    - Differential privacy
    - Homomorphic encryption simulation
    - HIPAA and GDPR compliance
    - Comprehensive audit logging
    """,
    author="Claude AI Assistant",
    author_email="support@abena-ihr.com",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="healthcare, privacy, security, blockchain, data-triage, HIPAA, GDPR",
    project_urls={
        "Documentation": "https://github.com/abena-ihr/secure-data-triage/docs",
        "Source": "https://github.com/abena-ihr/secure-data-triage",
        "Tracker": "https://github.com/abena-ihr/secure-data-triage/issues",
    },
    entry_points={
        "console_scripts": [
            "abena-triage=secure_data_triage_algorithm:demonstrate_triage_algorithm",
        ],
    },
) 