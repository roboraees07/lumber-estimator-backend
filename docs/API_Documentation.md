# 🏗️ Lumber Estimator API Documentation

## Overview

The Lumber Estimator API provides comprehensive construction material estimation with advanced contractor profiling and item management capabilities.

**Base URL:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/docs`  
**Alternative Docs:** `http://localhost:8000/redoc`

## Quick Start

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **View interactive docs:**
   Open `http://localhost:8000/docs` in your browser

3. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## Authentication

Currently, the API is open access. Authentication will be added in future versions.

## Core Features

### 🏢 Contractor Profiling System
- Detailed contractor profiles with business information
- Capability tracking and specializations  
- Reviews and ratings system
- Geographic and service area management

### 📦 Advanced Item Management
- Comprehensive material catalogs
- Detailed specifications and pricing
- Bulk import/export capabilities
- Price history tracking
- Inventory management

### 📊 Analytics Dashboard
- Performance metrics
- Price competitiveness analysis
- Geographic distribution
- Category analytics

### 🔍 Advanced Search
- Multi-criteria search across contractors and materials
- Price range filtering
- Geographic filtering
- Rating-based filtering

## API Endpoints

### Health & Status

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Lumber Estimator API",
  "version": "1.0.0",
  "status": "active",
  "docs_url": "/docs"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 🏢 Contractor Management

### Create Contractor Profile

#### `POST /contractors/profiles/`

Create a detailed contractor profile with capabilities and business information.

**Request Body:**
```json
{
  "name": "ABC Construction Supply",
  "business_license": "BL-12345",
  "address": "123 Builder St",
  "city": "Construction City",
  "state": "CA",
  "zip_code": "90210",
  "contact_number": "(555) 123-4567",
  "email": "contact@abc-supply.com",
  "website": "https://abc-supply.com",
  "specialty": "Lumber and Building Materials",
  "business_type": "supplier",
  "service_area": "regional",
  "payment_terms": "net30",
  "credit_rating": "A",
  "delivery_options": "both",
  "minimum_order": 500.00,
  "discount_policy": "2% net 10, 1% net 30",
  "warranty_policy": "1 year manufacturer warranty",
  "certifications": ["NWFA Certified", "ISO 9001"],
  "notes": "Specializes in sustainable lumber",
  "capabilities": [
    {
      "name": "Lumber Supply",
      "proficiency_level": "expert",
      "years_experience": 15,
      "certifications": "NWFA Certified"
    },
    {
      "name": "Steel Products",
      "proficiency_level": "intermediate",
      "years_experience": 8
    }
  ]
}
```

**Response:**
```json
{
  "contractor_id": 123,
  "message": "Contractor profile created successfully"
}
```

### Get Contractor Profile

#### `GET /contractors/profiles/{contractor_id}`

Get complete contractor profile with capabilities and statistics.

**Response:**
```json
{
  "id": 123,
  "name": "ABC Construction Supply",
  "business_license": "BL-12345",
  "address": "123 Builder St",
  "city": "Construction City",
  "state": "CA",
  "contact_number": "(555) 123-4567",
  "email": "contact@abc-supply.com",
  "specialty": "Lumber and Building Materials",
  "business_type": "supplier",
  "rating": 4.8,
  "capabilities": [
    {
      "name": "Lumber Supply",
      "proficiency_level": "expert",
      "years_experience": 15
    }
  ],
  "review_count": 45,
  "average_rating": 4.8
}
```

### Search Contractors

#### `POST /contractors/profiles/search`

Search contractors with advanced filtering.

**Request Body:**
```json
{
  "specialty": "lumber",
  "business_type": "supplier",
  "service_area": "regional",
  "city": "Construction City",
  "state": "CA",
  "min_rating": 4.0
}
```

**Response:**
```json
{
  "contractors": [
    {
      "id": 123,
      "name": "ABC Construction Supply",
      "rating": 4.8,
      "material_count": 150,
      "review_count": 45
    }
  ],
  "total_found": 1,
  "filters_applied": {
    "specialty": "lumber",
    "min_rating": 4.0
  }
}
```

---

## 📦 Material Item Management

### Add Material Item

#### `POST /contractors/{contractor_id}/items/`

Add a detailed material item to contractor inventory.

**Request Body:**
```json
{
  "item_name": "2x4_stud_8ft_premium",
  "display_name": "2x4 Premium Stud 8ft",
  "sku": "ABC-2X4-8-PREM",
  "category": "Lumber",
  "subcategory": "Dimensional Lumber",
  "unit": "each",
  "price": 4.25,
  "cost": 3.50,
  "currency": "USD",
  "dimensions": "1.5\" x 3.5\" x 8'",
  "weight": 8.5,
  "weight_unit": "lbs",
  "material_type": "Southern Pine",
  "grade_quality": "Premium Grade",
  "brand": "ABC Premium",
  "manufacturer": "ABC Mills",
  "model_number": "2X4-8-PREM",
  "description": "Premium grade 2x4 stud, kiln dried",
  "specifications": {
    "moisture_content": "19% max",
    "grade_stamp": "SPIB",
    "treatment": "Kiln Dried"
  },
  "installation_notes": "Pre-drill for nails near ends",
  "safety_info": "Wear safety glasses when cutting",
  "compliance_codes": "IRC 2021, IBC 2021",
  "lead_time_days": 3,
  "stock_quantity": 500,
  "minimum_order_qty": 10,
  "bulk_pricing": [
    {"quantity": 100, "price": 4.00},
    {"quantity": 500, "price": 3.75}
  ],
  "seasonal_availability": true,
  "is_special_order": false
}
```

**Response:**
```json
{
  "material_id": 456,
  "message": "Material item added successfully"
}
```

### Bulk Add Materials

#### `POST /contractors/{contractor_id}/items/bulk`

Add multiple material items at once.

**Request Body:**
```json
[
  {
    "item_name": "2x4_stud_8ft",
    "price": 3.25,
    "category": "Lumber"
  },
  {
    "item_name": "2x6_stud_8ft", 
    "price": 8.50,
    "category": "Lumber"
  }
]
```

**Response:**
```json
{
  "imported": 2,
  "skipped": 0,
  "errors": [],
  "message": "Bulk import completed: 2 imported, 0 skipped"
}
```

### Get Contractor Materials

#### `GET /contractors/{contractor_id}/items/`

Get materials for a contractor with filtering and pagination.

**Query Parameters:**
- `category` (optional): Filter by category
- `search` (optional): Search term
- `limit` (optional): Results limit (default: 100)
- `offset` (optional): Results offset (default: 0)

**Response:**
```json
{
  "materials": [
    {
      "id": 456,
      "item_name": "2x4_stud_8ft_premium",
      "display_name": "2x4 Premium Stud 8ft",
      "category": "Lumber",
      "price": 4.25,
      "unit": "each",
      "stock_quantity": 500,
      "contractor_name": "ABC Construction Supply"
    }
  ],
  "total_count": 150,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

### Update Material Price

#### `PUT /contractors/items/{material_id}/price`

Update material price with history tracking.

**Query Parameters:**
- `new_price` (required): New price
- `reason` (optional): Reason for price change

**Response:**
```json
{
  "message": "Material price updated successfully"
}
```

### Get Price History

#### `GET /contractors/items/{material_id}/price-history`

Get price change history for a material.

**Response:**
```json
{
  "price_history": [
    {
      "old_price": 4.00,
      "new_price": 4.25,
      "change_reason": "Supplier cost increase",
      "effective_date": "2025-01-15",
      "created_at": "2025-01-15 10:30:00"
    }
  ]
}
```

---

## 📊 Dashboard & Analytics

### Dashboard Overview

#### `GET /dashboard/overview`

Get comprehensive dashboard statistics.

**Response:**
```json
{
  "totals": {
    "contractors": 45,
    "materials": 2500,
    "projects": 125
  },
  "recent_activity": {
    "new_contractors_30_days": 3,
    "new_materials_30_days": 150
  },
  "analytics": {
    "materials_by_category": [
      {"category": "Lumber", "count": 800},
      {"category": "Steel", "count": 400}
    ],
    "contractors_by_type": [
      {"type": "supplier", "count": 30},
      {"type": "contractor", "count": 15}
    ],
    "top_contractors": [
      {
        "id": 123,
        "name": "ABC Construction Supply",
        "rating": 4.8,
        "review_count": 45
      }
    ]
  }
}
```

### Contractor Performance

#### `GET /dashboard/contractors/{contractor_id}/performance`

Get detailed performance metrics for a contractor.

**Response:**
```json
{
  "contractor": {
    "id": 123,
    "name": "ABC Construction Supply",
    "business_type": "supplier",
    "specialty": "Lumber and Building Materials"
  },
  "inventory": {
    "total_materials": 150,
    "categories_covered": 5
  },
  "competitiveness": {
    "competitive_items": 75,
    "total_items": 150,
    "competitiveness_rate": 50.0
  },
  "activity": {
    "recent_price_changes": 12
  },
  "reviews": {
    "total_reviews": 45,
    "average_rating": 4.8,
    "average_delivery": 4.5,
    "average_quality": 4.9,
    "average_price_rating": 4.2,
    "average_service": 4.7
  }
}
```

### Advanced Search

#### `GET /dashboard/search/advanced`

Advanced search across contractors and materials.

**Query Parameters:**
- `query`: Search term
- `category`: Material category
- `contractor_id`: Specific contractor
- `min_price`, `max_price`: Price range
- `business_type`: Contractor business type
- `service_area`: Service area
- `min_rating`: Minimum contractor rating
- `in_stock_only`: Only items in stock
- `special_order`: Include/exclude special order items
- `limit`, `offset`: Pagination

**Response:**
```json
{
  "results": [
    {
      "material_id": 456,
      "item_name": "2x4_stud_8ft_premium",
      "category": "Lumber",
      "price": 4.25,
      "contractor_id": 123,
      "contractor_name": "ABC Construction Supply",
      "contractor_rating": 4.8,
      "city": "Construction City",
      "state": "CA"
    }
  ],
  "pagination": {
    "total_count": 1250,
    "limit": 50,
    "offset": 0,
    "has_more": true
  },
  "filters_applied": {
    "category": "Lumber",
    "min_rating": 4.0
  }
}
```

---

## 🔍 PDF Estimation

### Direct PDF Estimation

#### `POST /estimate/pdf`

Upload PDF and get material estimation without creating a project.

**Form Data:**
- `file`: PDF file (required)
- `project_name`: Optional project name  
- `use_visual`: Boolean for visual analysis (default: true)

**Response:**
```json
{
  "project_info": {
    "project_name": "LAMONS 3200LS ELECT",
    "analysis_date": "2025-01-15 10:30:00",
    "analysis_methods": ["Gemini AI Text Extraction"]
  },
  "text_analysis": {
    "total_materials_found": 27,
    "total_estimated_cost": 8423.45,
    "items_needing_quotation": 2
  },
  "combined_estimates": [
    {
      "item": "Can Light 6inch H2O-Sealed",
      "quantity": 7,
      "unit_price": 45.50,
      "total_price": 318.50,
      "contractor_name": "ElectroMax Supply",
      "contractor_contact": "(555) 321-9876",
      "status": "found"
    }
  ],
  "summary": {
    "total_items_detected": 27,
    "items_with_pricing": 25,
    "items_needing_quotes": 2,
    "estimated_total_cost": 8423.45,
    "analysis_completeness": "92.6%"
  }
}
```

---

## 📁 File Import/Export

### Import Materials from File

#### `POST /contractors/{contractor_id}/items/import`

Import materials from CSV or Excel file.

**Form Data:**
- `file`: CSV or Excel file

**Expected CSV Format:**
```csv
item_name,display_name,category,price,unit,description,brand,manufacturer
2x4_stud_8ft,2x4 Stud 8ft,Lumber,3.25,each,Standard 2x4 stud,ABC,ABC Mills
```

**Response:**
```json
{
  "imported": 150,
  "skipped": 5,
  "errors": [
    "Invalid price for item: xyz"
  ]
}
```

---

## 📝 Reviews & Ratings

### Add Contractor Review

#### `POST /contractors/{contractor_id}/reviews/`

Add a review for a contractor.

**Request Body:**
```json
{
  "rating": 5,
  "review_text": "Excellent service and fast delivery",
  "delivery_rating": 5,
  "quality_rating": 5,
  "price_rating": 4,
  "service_rating": 5,
  "reviewer_name": "John Builder",
  "order_date": "2025-01-10"
}
```

**Response:**
```json
{
  "message": "Review added successfully"
}
```

---

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. This will be added in future versions.

---

## Data Models

### Contractor Profile
```json
{
  "id": "integer",
  "name": "string (required)",
  "business_license": "string",
  "address": "string", 
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "contact_number": "string",
  "email": "string",
  "website": "string",
  "specialty": "string",
  "business_type": "supplier|contractor|manufacturer",
  "service_area": "local|regional|national",
  "payment_terms": "string",
  "credit_rating": "A|B|C|D",
  "delivery_options": "pickup|delivery|both",
  "minimum_order": "number",
  "rating": "number (0-5)",
  "is_active": "boolean"
}
```

### Material Item
```json
{
  "id": "integer",
  "contractor_id": "integer",
  "item_name": "string (required)",
  "display_name": "string",
  "sku": "string",
  "category": "string",
  "subcategory": "string", 
  "unit": "string",
  "price": "number (required)",
  "cost": "number",
  "dimensions": "string",
  "weight": "number",
  "material_type": "string",
  "grade_quality": "string",
  "brand": "string",
  "manufacturer": "string",
  "description": "string",
  "specifications": "object",
  "stock_quantity": "integer",
  "is_special_order": "boolean",
  "discontinued": "boolean"
}
```

---

## Examples

### Complete Contractor Setup Flow

1. **Create contractor profile:**
```bash
curl -X POST "http://localhost:8000/contractors/profiles/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Superior Building Supply",
    "contact_number": "(555) 987-6543",
    "specialty": "lumber",
    "business_type": "supplier"
  }'
```

2. **Add materials:**
```bash
curl -X POST "http://localhost:8000/contractors/123/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "2x4_stud_8ft",
    "price": 3.25,
    "category": "Lumber"
  }'
```

3. **Search materials:**
```bash
curl "http://localhost:8000/dashboard/search/advanced?category=Lumber&min_price=3&max_price=5"
```

---

## Support

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Dashboard Overview:** http://localhost:8000/dashboard/overview

For technical support, please check the interactive API documentation at `/docs` endpoint.



