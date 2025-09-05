# Quotation Management APIs

## Overview
This document describes the new quotation management APIs that have been added to the contractor management system. These APIs implement the relationship where 1 user can make multiple quotations, and 1 quotation can have multiple items.

## Database Schema

### Tables Created
1. **quotations** - Stores quotation information
2. **quotation_items** - Stores items within quotations

### Relationships
- `quotations.user_id` → `users.id` (1 user can have many quotations)
- `quotation_items.quotation_id` → `quotations.id` (1 quotation can have many items)

## API Endpoints

### 1. Create First Quotation
**Endpoint:** `POST /contractors/quotations/create`

**Description:** Creates a new quotation with items for a user. Auto-assigns quotation ID and item IDs.

**Parameters:**
- `user_id` (query parameter): User ID creating the quotation

**Request Body:**
```json
{
  "quotation_name": "Office Renovation Project",
  "client_name": "ABC Corporation",
  "client_email": "contact@abc-corp.com",
  "client_phone": "(555) 123-4567",
  "project_address": "123 Business St, City, State 12345",
  "project_description": "Complete office renovation",
  "notes": "Urgent project",
  "valid_until": "2024-02-15",
  "items": [
    {
      "item_name": "Premium Oak Flooring",
      "sku": "OAK-PREM-001",
      "unit": "per sq ft",
      "unit_of_measure": "per sq ft",
      "cost": 12.50,
      "quantity": 100,
      "description": "High-quality oak flooring",
      "category": "Flooring"
    }
  ]
}
```

**Response:**
```json
{
  "quotation_id": 123,
  "message": "Quotation created successfully",
  "items": [
    {
      "item_id": 456,
      "item_name": "Premium Oak Flooring",
      "sku_id": "OAK-PREM-001",
      "unit": "per sq ft",
      "unit_of_measure": "per sq ft",
      "cost": 12.50,
      "quantity": 100,
      "total_cost": 1250.00
    }
  ]
}
```

### 2. Get Quotation Items
**Endpoint:** `GET /contractors/quotations/{quotation_id}/items`

**Description:** Retrieves all items from a specific quotation.

**Response:**
```json
{
  "quotation_id": 123,
  "items": [
    {
      "item_id": 456,
      "item_name": "Premium Oak Flooring",
      "sku_id": "OAK-PREM-001",
      "unit": "per sq ft",
      "unit_of_measure": "per sq ft",
      "cost": 12.50,
      "quantity": 100,
      "total_cost": 1250.00
    }
  ],
  "total_items": 1,
  "total_cost": 1250.00
}
```

### 3. Add Item to Quotation
**Endpoint:** `POST /contractors/quotations/{quotation_id}/items`

**Description:** Adds a new item to an existing quotation.

**Request Body:**
```json
{
  "item_name": "Steel Beams",
  "sku": null,
  "unit": "per piece",
  "unit_of_measure": "per piece",
  "cost": 150.00,
  "quantity": 5,
  "description": "Structural steel beams",
  "category": "Structural"
}
```

**Response:**
```json
{
  "item_id": 789,
  "message": "Item added to quotation successfully",
  "item": {
    "item_id": 789,
    "item_name": "Steel Beams",
    "sku_id": "N/A",
    "unit": "per piece",
    "unit_of_measure": "per piece",
    "cost": 150.00,
    "quantity": 5,
    "total_cost": 750.00
  }
}
```

### 4. Get User Quotations
**Endpoint:** `GET /contractors/quotations/user/{user_id}`

**Description:** Retrieves all quotations for a specific user.

**Response:**
```json
{
  "user_id": 1,
  "quotations": [
    {
      "quotation_id": 123,
      "quotation_name": "Office Renovation Project",
      "client_name": "ABC Corporation",
      "total_cost": 2000.00,
      "status": "draft",
      "item_count": 2,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total_quotations": 1
}
```

## Key Features

### Auto-Increment IDs
- Quotation IDs are auto-assigned by the database
- Item IDs are auto-assigned by the database
- No manual ID assignment required

### SKU Handling
- SKU is optional for items
- If SKU is not provided, the API returns "N/A" in the response
- This matches the modal behavior shown in the image

### Cost Calculations
- Individual item total cost = quantity × cost
- Quotation total cost = sum of all item total costs
- Costs are automatically calculated and updated

### Data Validation
- Required fields are validated
- Proper error handling with HTTP status codes
- Detailed error messages for debugging

## Usage Examples

### Creating a Quotation from Dashboard
When a user clicks "Create Your First Quotation" from the dashboard:

1. Frontend calls `POST /contractors/quotations/create` with user_id and items
2. Backend creates quotation and items with auto-assigned IDs
3. Frontend receives quotation_id and item details for display

### Adding Items to Existing Quotation
When a user adds items to an existing quotation:

1. Frontend calls `POST /contractors/quotations/{quotation_id}/items` with item details
2. Backend adds item and updates quotation total cost
3. Frontend receives new item details with auto-assigned item_id

### Viewing Quotation Items
When displaying items in a quotation:

1. Frontend calls `GET /contractors/quotations/{quotation_id}/items`
2. Backend returns all items with proper formatting
3. Frontend displays items with SKU showing "N/A" if not provided

### Listing User Quotations
When showing all quotations for a user:

1. Frontend calls `GET /contractors/quotations/user/{user_id}`
2. Backend returns all quotations with item counts and totals
3. Frontend displays quotation list with summary information

## Error Handling

### Common Error Responses
- **400 Bad Request**: Invalid input data, missing required fields
- **404 Not Found**: Quotation not found
- **500 Internal Server Error**: Database or server errors

### Example Error Response
```json
{
  "detail": "Items list cannot be empty"
}
```

## Testing

A test script `test_quotation_apis.py` has been created to verify all endpoints work correctly. The script tests:

1. Creating a quotation with multiple items
2. Retrieving quotation items
3. Adding items to existing quotations
4. Getting all quotations for a user

## Integration Notes

- The APIs are integrated into the existing contractor management router
- All endpoints follow the same authentication and error handling patterns
- Database tables are created automatically when the application starts
- The APIs are fully documented with OpenAPI/Swagger specifications
