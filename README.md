# 🏗️ Lumber Estimator API

A sophisticated AI-powered lumber estimation system that analyzes construction PDFs and provides accurate material estimates with confidence scoring.

## ✨ Features

- **AI-Powered PDF Analysis**: Uses Google Gemini 2.0 Flash for intelligent document processing
- **Advanced Material Detection**: Automatically identifies lumber types, dimensions, and quantities
- **Confidence-Based Accuracy**: Multi-dimensional accuracy scoring system with confidence intervals
- **User Role Management**: Admin, Estimator, and Contractor roles with approval workflow
- **Intelligent Caching**: Optimized performance with result caching and cache invalidation
- **Comprehensive API**: RESTful endpoints with JWT authentication and rate limiting
- **Real-time Validation**: Built-in accuracy validation and reporting
- **Building Dimension Extraction**: Automatic calculation of length, width, height, area, and perimeter
- **Material Database Integration**: Comprehensive lumber and construction material catalog
- **Contractor Management System**: Detailed profiles with capabilities, specialties, and ratings
- **Dashboard Analytics**: System overview with user counts, project statistics, and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key
- SQLite database

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lumber-estimator.git
cd lumber-estimator
```

2. **Create virtual environment**
```bash
python -m venv lumber_env
source lumber_env/bin/activate  # On Windows: lumber_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your Gemini API key and other configurations
```

5. **Run the application**
```bash
python app.py
```

6. **Access the API**
- API Documentation: http://localhost:8003/docs
- Health Check: http://localhost:8003/health

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration (requires admin approval)
- `POST /auth/login` - User authentication
- `GET /auth/pending-approvals` - View pending approvals (Admin only)
- `POST /auth/approve-user` - Approve/reject users (Admin only)

### Estimation Endpoints
- `POST /lumber/estimate/pdf` - PDF analysis and estimation
- `GET /accuracy/summary` - Accuracy metrics summary
- `POST /accuracy/validate/{project_id}` - Validate estimation accuracy
- `POST /accuracy/validate/pdf` - Validate PDF estimation accuracy
- `GET /accuracy/report` - Generate accuracy reports

### Contractor Management
- `POST /contractors/profiles/` - Create contractor profile
- `GET /contractors/search` - Search contractors with filters
- `GET /contractors/{contractor_id}` - Get contractor details
- `PUT /contractors/{contractor_id}` - Update contractor profile

### Dashboard & Analytics
- `GET /dashboard/overview` - System overview and statistics
- `GET /dashboard/user-stats` - User statistics and activity

### Test Endpoints (No Authentication Required)
- `POST /test/upload-pdf-estimate` - Test PDF processing

## 🔐 Role-Based Capabilities & Permissions

### 👑 ADMIN Users Can:
- **Approve/Reject new user registrations** with rejection reason tracking
- **View all pending user approvals** with detailed user information
- **Access complete system dashboard** with user counts, project statistics, and system health
- **Manage all user accounts** including suspension and status changes
- **View system logs and performance metrics** for monitoring and debugging
- **Access all API endpoints** without restrictions
- **Create and manage contractor profiles** on behalf of companies
- **View accuracy reports** for all projects across the system
- **Monitor API usage and rate limiting** statistics
- **Access administrative functions** for system maintenance

### 📊 ESTIMATOR Users Can:
- **Upload PDFs for lumber estimation** with project naming and analysis
- **View detailed accuracy metrics** for their own projects
- **Access accuracy summary reports** for their estimation history
- **Validate estimation accuracy** by comparing actual vs. estimated results
- **Search and view contractor profiles** for material sourcing
- **Access dashboard overview** with their project statistics
- **View building dimensions and material breakdowns** from PDF analysis
- **Track project history** with timestamps and analysis results
- **Access estimation endpoints** for lumber calculations
- **View confidence levels and accuracy breakdowns** for their projects

### 🏢 CONTRACTOR Users Can:
- **Create and manage their company profile** with detailed business information
- **Update contact details and business licenses** for verification
- **Set specialties and capabilities** for project matching
- **Manage company address and location** information
- **Set pricing and availability** for materials and services
- **View project opportunities** and estimation requests
- **Access contractor search results** to see how they appear to others
- **Update company ratings and reviews** (if implemented)
- **Manage business credentials** and certifications
- **Access contractor-specific endpoints** for profile management

## 🏗️ Architecture

```
src/
├── api/                    # FastAPI endpoints and routers
│   ├── main.py            # Main application and core endpoints (50KB, 1347 lines)
│   ├── auth.py            # Authentication and user management
│   ├── test_endpoints.py  # Test endpoints (no auth required)
│   ├── contractor_dashboard.py     # Contractor dashboard endpoints
│   └── contractor_management.py    # Contractor management endpoints
├── core/                   # Core business logic
│   ├── accuracy_calculator.py      # Accuracy calculation engine (22KB, 513 lines)
│   ├── lumber_pdf_extractor.py     # PDF processing and AI analysis (42KB, 863 lines)
│   ├── estimation_engine.py        # Lumber estimation logic (20KB, 451 lines)
│   ├── lumber_database.py          # Lumber material database
│   ├── lumber_estimation_engine.py # Additional estimation engine
│   └── contractor_input.py         # Contractor input processing
├── database/               # Database models and management
│   ├── auth_models.py              # User authentication models (13KB, 329 lines)
│   └── enhanced_models.py          # Enhanced database models (27KB, 632 lines)
├── config/                 # Configuration management
│   └── settings.py                 # Application settings
└── utils/                  # Utility functions
    └── __init__.py                 # Utilities package initialization
```

## 🔐 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Note**: Admin account is automatically created on first run. New users (estimators/contractors) require admin approval.

## 📊 Accuracy Metrics

The system provides comprehensive accuracy scoring:
- **Overall Accuracy**: Weighted combination of all metrics
- **Material Accuracy**: Correctness of material identification by category
- **Quantity Accuracy**: Precision of quantity calculations
- **Pricing Accuracy**: Accuracy of cost estimates
- **Dimension Accuracy**: Precision of building measurements
- **Confidence Level**: Very High, High, Medium, Low, Very Low
- **Confidence Intervals**: Statistical confidence ranges for accuracy estimates
- **Validation Notes**: Detailed feedback for accuracy improvement

## 🧪 Testing

### Test Endpoints (No Authentication Required)
Use these endpoints for quick testing without setting up authentication:
```bash
# Test PDF processing
curl -X POST "http://localhost:8003/test/upload-pdf-estimate" \
  -F "file=@your_pdf_file.pdf" \
  -F "project_name=Test Project"
```

### Health Check
```bash
curl http://localhost:8003/health
```

## 📝 Environment Variables

```bash
# API Configuration
PORT=8003
HOST=0.0.0.0
DEBUG=true

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///data/lumber_estimator.db

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# File Storage
UPLOAD_DIR=data/lumber_pdf_uploads
OUTPUT_DIR=outputs/lumber_pdf_estimates

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8003"]
```

## 🚫 Access Restrictions by Role

- **Estimators CANNOT** approve other users or access admin functions
- **Contractors CANNOT** perform PDF estimations or access accuracy metrics
- **Non-admin users CANNOT** view pending approvals or system-wide statistics
- **Pending users CANNOT** access any protected endpoints until approved
- **Suspended users CANNOT** authenticate or access the system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [documentation](docs/) folder
- Review the [API documentation](http://localhost:8003/docs)
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for high-level overview
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure

## 🔄 Changelog

### v1.0.0 (2025-08-18)
- Initial release with AI-powered PDF analysis
- User authentication and role management system
- Comprehensive accuracy calculation and validation
- Contractor management and profile system
- Dashboard analytics and system monitoring
- Advanced error handling and fallback mechanisms
- Professional project structure and documentation
- GitHub Actions CI/CD pipeline setup

