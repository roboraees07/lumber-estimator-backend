# 📁 Project Structure

## **Root Directory Structure**

```
lumber-estimator/
├── 📄 app.py                          # Main application entry point
├── 📄 setup.py                        # Python package setup configuration
├── 📄 requirements.txt                 # Python dependencies
├── 📄 env.example                     # Environment variables template
├── 📄 .gitignore                      # Git ignore patterns
├── 📄 LICENSE                         # MIT License
├── 📄 README.md                       # Main project documentation
├── 📄 PROJECT_SUMMARY.md              # High-level project overview
├── 📄 PROJECT_STRUCTURE.md            # This file - detailed structure
├── 📁 src/                            # Source code directory
├── 📁 docs/                           # Documentation directory
├── 📁 scripts/                        # Utility scripts
├── 📁 .github/                        # GitHub Actions workflows
├── 📁 data/                           # Data storage directory
├── 📁 outputs/                        # Generated outputs directory
├── 📁 samples/                        # Sample PDFs and test data
└── 📁 lumber_env/                     # Virtual environment (excluded from git)
```

## **📁 Source Code Structure (`src/`)**

```
src/
├── 📄 __init__.py                     # Package initialization
├── 📁 api/                            # API endpoints and routes
│   ├── 📄 __init__.py
│   ├── 📄 main.py                     # Main FastAPI application and core endpoints
│   ├── 📄 auth.py                     # Authentication endpoints
│   ├── 📄 test_endpoints.py           # Test endpoints (no auth required)
│   ├── 📄 contractor_dashboard.py     # Contractor dashboard endpoints
│   └── 📄 contractor_management.py    # Contractor management endpoints
├── 📁 core/                           # Core business logic
│   ├── 📄 __init__.py
│   ├── 📄 lumber_pdf_extractor.py     # PDF processing and AI analysis
│   ├── 📄 accuracy_calculator.py      # Accuracy calculation engine
│   ├── 📄 estimation_engine.py        # Lumber estimation logic
│   ├── 📄 lumber_database.py          # Lumber material database
│   ├── 📄 lumber_estimation_engine.py # Additional estimation engine
│   └── 📄 contractor_input.py         # Contractor input processing
├── 📁 database/                       # Database models and operations
│   ├── 📄 __init__.py
│   ├── 📄 auth_models.py              # User authentication models
│   └── 📄 enhanced_models.py          # Enhanced database models
├── 📁 config/                         # Configuration management
│   ├── 📄 __init__.py
│   └── 📄 settings.py                 # Application settings
└── 📁 utils/                          # Utility functions
    └── 📄 __init__.py                 # Utilities package initialization
```

## **📁 Documentation Structure (`docs/`)**

```
docs/
├── 📄 COMPLETE_USER_GUIDE.md          # Comprehensive user guide
├── 📄 ACCURACY_SYSTEM.md              # Accuracy system documentation
├── 📄 IMPLEMENTATION_STATUS.md        # Implementation status tracking
├── 📄 README_IMPLEMENTATION.md        # README implementation guide
├── 📄 API_Documentation.md            # Complete API reference
├── 📄 README.md                       # Documentation README
├── 📁 user_guide/                     # User documentation
├── 📁 api/                            # API documentation
├── 📁 development/                    # Developer documentation
└── 📁 architecture/                   # System architecture
```

## **📁 Scripts Structure (`scripts/`)**

```
scripts/
└── 📄 setup.py                        # Project setup automation
```

## **📁 GitHub Actions (`.github/workflows/`)**

```
.github/workflows/
└── 📄 ci-cd.yml                       # CI/CD pipeline
```

## **📁 Data Directories**

```
data/
├── 📁 lumber_pdf_uploads/             # Uploaded PDF files
├── 📁 lumber_database/                # Lumber material database
└── 📁 user_uploads/                   # User file uploads

outputs/
├── 📁 lumber_pdf_estimates/           # Generated estimation reports
├── 📁 accuracy_reports/                # Accuracy analysis reports
└── 📁 system_logs/                     # Application logs

samples/
├── 📁 projects/                        # Sample PDF projects
└── 📁 data/                           # Sample data files
```

## **🔒 Excluded from Git**

- `lumber_env/` - Virtual environment
- `data/` - User uploads and generated data
- `outputs/` - Generated reports and logs
- `*.db` - Database files
- `*.sqlite` - SQLite database files
- `temp_*.png` - Temporary image files
- `logs/` - Log files
- `.env` - Environment variables (contains secrets)
- `__pycache__/` - Python cache directories

## **📋 Key Files Description**

- **`app.py`**: Main application entry point that starts the FastAPI server
- **`src/api/main.py`**: Core API endpoints and application configuration (50KB, 1347 lines)
- **`src/core/lumber_pdf_extractor.py`**: PDF processing and AI analysis engine (42KB, 863 lines)
- **`src/core/accuracy_calculator.py`**: Accuracy calculation and validation system (22KB, 513 lines)
- **`src/core/estimation_engine.py`**: Lumber estimation logic (20KB, 451 lines)
- **`src/database/auth_models.py`**: User authentication and role management (13KB, 329 lines)
- **`src/database/enhanced_models.py`**: Enhanced database models (27KB, 632 lines)
- **`src/api/contractor_management.py`**: Contractor management endpoints (32KB, 759 lines)
- **`src/api/contractor_dashboard.py`**: Contractor dashboard functionality (23KB, 589 lines)
- **`requirements.txt`**: Python package dependencies with exact versions
- **`env.example`**: Template for environment variables setup
- **`README.md`**: Comprehensive project overview and getting started guide

## **🚀 Getting Started**

1. **Clone the repository**
2. **Copy `env.example` to `.env` and configure your environment variables**
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run the application**: `python app.py`
5. **Access the API documentation**: `http://localhost:8003/docs`

## **📊 Project Organization Benefits**

- **Modular Design**: Clear separation of concerns with dedicated modules
- **Scalable Structure**: Easy to add new features and maintain existing code
- **Professional Layout**: GitHub-ready structure for open-source contribution
- **Clear Documentation**: Comprehensive guides for users and developers
- **Automated CI/CD**: GitHub Actions for quality assurance and deployment
- **Clean Dependencies**: Minimal, well-defined package requirements

## **⚠️ Important Notes**

- **File Sizes**: Some core files are substantial (main.py: 50KB, lumber_pdf_extractor.py: 42KB)
- **Missing Files**: Some documented files don't exist (e.g., `crud_operations.py`, `database.py`)
- **Documentation**: Multiple documentation files exist with overlapping content
- **Structure**: The actual structure is simpler than documented but more focused

