from setuptools import setup, find_packages
import os

# Read requirements.txt for dependencies
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='abena-ihr-etl',
    version='1.0.0',
    description='Abena IHR - Data Transformation Layer (ETL) with Spark, FHIR, and unit conversion',
    long_description='ETL system for healthcare data transformation, mapping, and FHIR conversion for Abena IHR.',
    author='Abena IHR Development Team',
    author_email='info@abena-ihr.org',
    url='https://github.com/abena-ihr',
    py_modules=['abena_etl'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'abena-etl=abena_etl:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
