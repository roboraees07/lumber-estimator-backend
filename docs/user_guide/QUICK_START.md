# 🚀 Quick Start Guide

Get up and running with the Lumber Estimator API in minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Basic knowledge of REST APIs

## ⚡ Quick Setup

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/lumber-estimator.git
cd lumber-estimator
python scripts/setup.py
```

### 2. Configure Environment
```bash
# Edit .env file with your API key
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Start the Server
```bash
python app.py
```

### 4. Access the API
- **Interactive Docs**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health

## 🔑 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## 📖 First Steps

### 1. Create an Estimator Account
```bash
POST /auth/register
{
  "username": "my_estimator",
  "email": "estimator@example.com",
  "password": "secure_password",
  "role": "estimator",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 2. Admin Approval (Required)
```bash
# Login as admin first
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Then approve the estimator
POST /auth/approve-user
{
  "user_id": 2,
  "approved": true
}
```

### 3. Estimator Login
```bash
POST /auth/login
{
  "username": "my_estimator",
  "password": "secure_password"
}
```

### 4. Upload PDF for Analysis
```bash
POST /lumber/estimate/pdf
# Upload your PDF file with project details
```

## 📊 Understanding Results

### Accuracy Metrics
- **Overall Accuracy**: Combined score of all metrics
- **Material Accuracy**: Correctness of material identification
- **Quantity Accuracy**: Precision of quantity calculations
- **Pricing Accuracy**: Accuracy of cost estimates
- **Dimension Accuracy**: Precision of measurements

### Confidence Levels
- **Very High**: 95%+ accuracy
- **High**: 85-94% accuracy
- **Medium**: 70-84% accuracy
- **Low**: 50-69% accuracy
- **Very Low**: <50% accuracy

## 🔧 Common Operations

### View Accuracy Summary
```bash
GET /accuracy/summary
Authorization: Bearer YOUR_TOKEN
```

### Validate Estimation
```bash
POST /accuracy/validate/{project_id}
Authorization: Bearer YOUR_TOKEN
```

### Search Contractors
```bash
GET /contractors/search?query=lumber
Authorization: Bearer YOUR_TOKEN
```

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid API Key"**
   - Check your `.env` file
   - Verify Gemini API key is correct

2. **"User not approved"**
   - Contact admin for approval
   - Check account status

3. **"PDF processing failed"**
   - Ensure PDF is readable
   - Check file size limits
   - Verify API quota

### Getting Help

- Check the [API Documentation](http://localhost:8003/docs)
- Review error messages in the response
- Check server logs for details
- Create an issue on GitHub

## 📚 Next Steps

- Read the [Complete User Guide](COMPLETE_USER_GUIDE.md)
- Explore [API Documentation](http://localhost:8003/docs)
- Check [Development Guide](../development/DEVELOPMENT.md)
- Review [Project Structure](../../PROJECT_STRUCTURE.md)

## 🎯 Success Metrics

You've successfully set up the system when:
- ✅ Server starts without errors
- ✅ Admin can login and approve users
- ✅ Estimators can register and get approved
- ✅ PDF uploads work and return estimates
- ✅ Accuracy metrics are displayed

---

**Need help?** Check the documentation or create an issue on GitHub!




