# Contributing to Lumber Estimator

Thank you for your interest in contributing to the Lumber Estimator project! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic knowledge of FastAPI, Python, and REST APIs

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/lumber-estimator.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install dev dependencies: `pip install -r requirements.txt[dev]`
7. Copy `env.example` to `.env` and configure your environment
8. Run tests: `pytest tests/`

## 📝 Code Style

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Add docstrings for all public functions and classes

### Code Formatting
We use `black` for code formatting and `flake8` for linting:
```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/
```

### Pre-commit Hooks
Consider setting up pre-commit hooks to automatically format and lint your code:
```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest tests/ -v
```

### Writing Tests
- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when appropriate
- Aim for high test coverage

## 🔄 Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Test your changes**:
   ```bash
   pytest tests/
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Commit your changes** with clear commit messages:
   ```bash
   git commit -m "feat: add new lumber estimation feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots if UI changes
   - Test results

### Commit Message Format
We use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

## 📚 Documentation

### API Documentation
- Keep API docstrings up to date
- Include examples in docstrings
- Update README.md for new features
- Maintain accurate endpoint documentation

### Code Documentation
- Add inline comments for complex logic
- Update docstrings when changing function signatures
- Keep architecture documentation current

## 🔒 Security

- Never commit API keys or sensitive data
- Follow security best practices
- Report security vulnerabilities privately
- Use environment variables for configuration

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help other contributors
- Provide constructive feedback
- Follow the project's code of conduct

## 📞 Getting Help

- Check existing issues and discussions
- Ask questions in GitHub discussions
- Join our community channels
- Review the documentation

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and improvements
- Performance optimizations
- Security enhancements
- Test coverage improvements

### Medium Priority
- New features and endpoints
- Documentation improvements
- Code refactoring
- UI/UX enhancements

### Low Priority
- Nice-to-have features
- Code style improvements
- Additional test cases
- Performance monitoring

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Lumber Estimator! 🚀 