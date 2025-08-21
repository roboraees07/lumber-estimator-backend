#!/usr/bin/env python3
"""
Setup script for Lumber Estimator API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="lumber-estimator",
    version="1.0.0",
    author="Lumber Estimator Team",
    author_email="team@lumber-estimator.com",
    description="AI-powered lumber estimation system with advanced accuracy scoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lumber-estimator",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/lumber-estimator/issues",
        "Source": "https://github.com/yourusername/lumber-estimator",
        "Documentation": "https://github.com/yourusername/lumber-estimator/docs",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Construction Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocstrings>=0.23.0",
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
    keywords="lumber, construction, estimation, AI, machine learning, PDF analysis, building materials",
    platforms=["any"],
    zip_safe=False,
)




