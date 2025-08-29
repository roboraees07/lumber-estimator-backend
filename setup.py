#!/usr/bin/env python3
"""
Setup script for Lumber Estimator Backend
A sophisticated AI-powered lumber estimation system
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lumber-estimator-backend",
    version="1.0.0",
    author="Muhammad Raees Azam",
    author_email="raees.info07@gmail.com",
    description="AI-Powered Construction Material Estimation System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/roboraees07/lumber-estimator-backend",
    project_urls={
        "Bug Reports": "https://github.com/roboraees07/lumber-estimator-backend/issues",
        "Source": "https://github.com/roboraees07/lumber-estimator-backend",
        "Documentation": "https://github.com/roboraees07/lumber-estimator-backend/docs",
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
        "Topic :: Construction",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "ai": [
            "google-generativeai>=0.3.2",
            "torch>=2.0.0",
            "transformers>=4.30.0",
        ],
        "pdf": [
            "PyPDF2>=3.0.1",
            "pdfplumber>=0.10.3",
            "PyMuPDF>=1.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lumber-estimator=app:main",
            "lumber-api=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json", "*.sql", "*.db"],
    },
    keywords=[
        "lumber",
        "construction",
        "estimation",
        "AI",
        "machine-learning",
        "PDF-analysis",
        "contractor-management",
        "material-estimation",
        "construction-costs",
        "building-materials",
        "fastapi",
        "python",
        "api",
        "database",
        "sqlite",
        "google-gemini",
        "accuracy-calculation",
        "project-management",
    ],
    platforms=["any"],
    zip_safe=False,
) 