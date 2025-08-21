# 🛠️ Development Guide

Guide for developers contributing to the Lumber Estimator project.

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/lumber-estimator.git
cd lumber-estimator

# Create virtual environment
python -m venv lumber_env
source lumber_env/bin/activate  # On Windows: lumber_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Setup environment
cp env.example .env
# Edit .env with your configuration

# Run setup script
python scripts/setup.py
```

## 📁 Project Structure

### Core Components
- **`src/api/`**: FastAPI endpoints and routers
- **`src/core/`**: Business logic and AI integration
- **`src/database/`**: Database models and management
- **`src/config/`**: Configuration management
- **`src/utils/`**: Utility functions

### Key Files
- **`app.py`**: Application entry point
- **`src/api/main.py`**: Main API router
- **`src/core/lumber_pdf_extractor.py`**: PDF processing logic
- **`src/core/accuracy_calculator.py`**: Accuracy calculation

## 🔧 Development Workflow

### 1. Code Style
- Use **Black** for code formatting
- Follow **PEP 8** guidelines
- Use **type hints** where possible
- Write **docstrings** for all functions

### 2. Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=src tests/

# Run with verbose output
python -m pytest -v tests/
```

### 3. Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking (if using mypy)
mypy src/
```

## 🧪 Testing Guidelines

### Test Structure
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test API endpoints
- **End-to-End Tests**: Test complete workflows

### Test Naming
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Example Test
```python
def test_user_registration():
    """Test user registration endpoint"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "estimator"
    })
    
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

## 🚀 Adding New Features

### 1. Create Feature Branch
```bash
git checkout -b feature/new-feature-name
```

### 2. Implement Feature
- Add code in appropriate module
- Write tests for new functionality
- Update documentation

### 3. Test Changes
```bash
python -m pytest tests/ -v
python app.py  # Test manually
```

### 4. Commit and Push
```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/new-feature-name
```

### 5. Create Pull Request
- Describe the feature
- Include test results
- Reference any issues

## 🔍 Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Information message")
logger.error("Error message")
logger.debug("Debug message")
```

### Debug Mode
```bash
# Set debug mode
export DEBUG=true
# or edit .env file

# Run with debug logging
python app.py
```

### Common Debug Points
- Check `.env` configuration
- Verify database connections
- Check API key validity
- Review server logs

## 📊 Performance Considerations

### Database
- Use indexes for frequently queried fields
- Implement connection pooling for production
- Consider query optimization

### API
- Implement caching where appropriate
- Use async operations for I/O
- Consider rate limiting

### File Processing
- Implement file size limits
- Use streaming for large files
- Clean up temporary files

## 🔒 Security Guidelines

### Authentication
- Always validate JWT tokens
- Implement proper role-based access
- Use secure password hashing

### Input Validation
- Validate all user inputs
- Sanitize file uploads
- Implement rate limiting

### Environment Variables
- Never commit sensitive data
- Use strong secret keys
- Rotate keys regularly

## 📚 Documentation

### Code Documentation
- Write clear docstrings
- Include examples in docstrings
- Document complex algorithms

### API Documentation
- Update endpoint descriptions
- Include request/response examples
- Document error codes

### User Documentation
- Update user guides
- Include screenshots where helpful
- Provide troubleshooting steps

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database optimized
- [ ] Logging configured
- [ ] CORS settings updated
- [ ] Security headers added
- [ ] Monitoring setup

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🤝 Contributing

### Before Contributing
1. Read the project documentation
2. Check existing issues and PRs
3. Discuss major changes in issues first

### Pull Request Guidelines
- Clear description of changes
- Include tests for new features
- Update documentation
- Follow commit message conventions

### Commit Message Format
```
type(scope): description

feat(auth): add user approval workflow
fix(api): resolve PDF processing error
docs(readme): update installation steps
```

## 🆘 Getting Help

- Check existing documentation
- Review GitHub issues
- Ask questions in discussions
- Contact maintainers

---

**Happy coding! 🚀**




