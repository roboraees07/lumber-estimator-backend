#!/usr/bin/env python3
"""
Setup script for Lumber Estimator project
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="lumber-estimator",
    version="1.0.0",
    author="Lumber Estimator Team",
    author_email="support@lumber-estimator.com",
    description="AI-powered construction material estimation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lumber-estimator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lumber-estimator=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="lumber estimation construction AI PDF analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/lumber-estimator/issues",
        "Source": "https://github.com/yourusername/lumber-estimator",
        "Documentation": "https://github.com/yourusername/lumber-estimator/docs",
    },
) 