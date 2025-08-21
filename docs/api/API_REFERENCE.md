# 📚 API Reference

Complete API documentation for the Lumber Estimator system.

## 🔐 Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## 📋 Endpoints Overview

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/pending-approvals` - View pending approvals (Admin)
- `POST /auth/approve-user` - Approve/reject users (Admin)

### Estimation
- `POST /lumber/estimate/pdf` - PDF analysis and estimation
- `GET /accuracy/summary` - Accuracy metrics summary
- `POST /accuracy/validate/{project_id}` - Validate estimation accuracy
- `POST /accuracy/validate/pdf` - Validate PDF estimation
- `GET /accuracy/report` - Generate accuracy report

### Contractor Management
- `POST /contractors/profiles/` - Create contractor profile
- `GET /contractors/search` - Search contractors

### Dashboard
- `GET /dashboard/overview` - System overview and statistics

### System
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🔐 Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "role": "estimator|contractor|admin",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "company_name": "string",
  "business_license": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string"
}
```

**Response:**
```json
{
  "message": "User registered successfully. Pending admin approval.",
  "user_id": 2,
  "username": "estimator_john",
  "role": "estimator",
  "account_status": "pending"
}
```

**Status Codes:**
- `200` - Registration successful
- `400` - Invalid input data
- `409` - Username/email already exists

### POST /auth/login

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "account_status": "approved"
  }
}
```

**Status Codes:**
- `200` - Login successful
- `401` - Invalid credentials
- `403` - Account not approved

### GET /auth/pending-approvals

View all pending user approvals (Admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "id": 2,
    "username": "estimator_john",
    "email": "john@example.com",
    "role": "estimator",
    "account_status": "pending",
    "first_name": "John",
    "last_name": "Estimator",
    "company_name": "John's Construction Co",
    "created_at": "2025-08-18T14:30:00"
  }
]
```

### POST /auth/approve-user

Approve or reject a pending user (Admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "user_id": 2,
  "approved": true,
  "rejection_reason": null
}
```

**Response:**
```json
{
  "message": "User estimator_john approved successfully",
  "user_id": 2,
  "account_status": "approved"
}
```

## 🏗️ Estimation Endpoints

### POST /lumber/estimate/pdf

Analyze PDF and generate lumber estimation.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Form Data:**
- `file`: PDF file (required)
- `project_name`: string (required)
- `force_fresh_analysis`: boolean (optional, default: false)

**Response:**
```json
{
  "project_id": "test_project_20250818_143000",
  "project_name": "Test Project",
  "pdf_filename": "construction_plan.pdf",
  "analysis_timestamp": "2025-08-18T14:30:00",
  "building_dimensions": {
    "length_feet": 80,
    "width_feet": 60,
    "height_feet": 8,
    "area_sqft": 4800,
    "perimeter_feet": 280
  },
  "materials": [
    {
      "type": "2x4 Lumber",
      "quantity": 120,
      "unit": "pieces",
      "dimensions": "2\" x 4\" x 8'",
      "estimated_price": 480.00,
      "confidence": 0.95
    }
  ],
  "total_estimate": 12500.00,
  "accuracy_metrics": {
    "overall_accuracy": 0.85,
    "confidence_level": "HIGH",
    "material_accuracy": 0.90,
    "quantity_accuracy": 0.80,
    "pricing_accuracy": 0.85,
    "dimension_accuracy": 0.95,
    "confidence_interval": 0.82,
    "validation_notes": "High confidence in material identification"
  }
}
```

**Status Codes:**
- `200` - Analysis successful
- `400` - Invalid file or parameters
- `401` - Unauthorized
- `500` - Processing error

### GET /accuracy/summary

Get accuracy metrics summary for all projects.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Response:**
```json
{
  "total_projects": 15,
  "average_accuracy": 0.87,
  "accuracy_distribution": {
    "very_high": 5,
    "high": 7,
    "medium": 2,
    "low": 1,
    "very_low": 0
  },
  "recent_projects": [
    {
      "project_id": "project_001",
      "accuracy": 0.92,
      "confidence_level": "VERY_HIGH"
    }
  ]
}
```

### POST /accuracy/validate/{project_id}

Validate accuracy for a specific project.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Request Body:**
```json
{
  "actual_materials": [
    {
      "type": "2x4 Lumber",
      "actual_quantity": 125,
      "actual_price": 500.00
    }
  ],
  "actual_total": 13000.00
}
```

**Response:**
```json
{
  "project_id": "project_001",
  "validation_result": {
    "overall_accuracy": 0.88,
    "material_accuracy": 0.90,
    "quantity_accuracy": 0.84,
    "pricing_accuracy": 0.86,
    "improvement_suggestions": [
      "Consider seasonal price variations",
      "Verify material specifications"
    ]
  }
}
```

## 🏢 Contractor Management

### POST /contractors/profiles/

Create a new contractor profile.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Request Body:**
```json
{
  "company_name": "ABC Construction",
  "contact_person": "John Smith",
  "email": "john@abc-construction.com",
  "phone": "+1-555-0123",
  "address": "123 Construction Ave",
  "city": "Buildertown",
  "state": "CA",
  "zip_code": "90210",
  "business_license": "LIC123456",
  "specialties": ["residential", "commercial"],
  "rating": 4.5
}
```

### GET /contractors/search

Search contractors by various criteria.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Query Parameters:**
- `query`: Search term
- `specialty`: Contractor specialty
- `rating_min`: Minimum rating
- `city`: City location

**Response:**
```json
[
  {
    "id": 1,
    "company_name": "ABC Construction",
    "contact_person": "John Smith",
    "rating": 4.5,
    "specialties": ["residential", "commercial"],
    "city": "Buildertown"
  }
]
```

## 📊 Dashboard Endpoints

### GET /dashboard/overview

Get system overview and statistics.

**Headers:**
```
Authorization: Bearer <user_token>
```

**Response:**
```json
{
  "total_users": 25,
  "total_projects": 150,
  "total_contractors": 12,
  "system_health": "healthy",
  "recent_activity": [
    {
      "type": "project_created",
      "description": "New project: Office Building",
      "timestamp": "2025-08-18T14:30:00"
    }
  ]
}
```

## 🚨 Error Responses

### Standard Error Format
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-08-18T14:30:00"
}
```

### Common Error Codes
- `INVALID_CREDENTIALS` - Wrong username/password
- `ACCOUNT_PENDING` - Account awaiting approval
- `INSUFFICIENT_PERMISSIONS` - Role-based access denied
- `FILE_PROCESSING_ERROR` - PDF processing failed
- `API_QUOTA_EXCEEDED` - Gemini API limit reached

## 📝 Rate Limits

- **Authentication**: 10 requests per minute
- **PDF Analysis**: 5 requests per minute
- **General API**: 100 requests per minute

## 🔄 Pagination

For endpoints returning lists, use query parameters:

```
GET /endpoint?page=1&size=20
```

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## 📡 WebSocket Support

Real-time updates available for:
- Project status changes
- Accuracy validation results
- System notifications

Connect to: `ws://localhost:8003/ws`

---

**For interactive testing, visit:** http://localhost:8003/docs




