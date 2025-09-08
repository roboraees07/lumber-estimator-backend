#!/usr/bin/env python3
"""
Contractor Management APIs
Advanced contractor profiling and item management endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import tempfile
import shutil
import os
from datetime import datetime, date

from ..database.enhanced_models import EnhancedDatabaseManager, ContractorProfileManager, MaterialItemManager, QuotationManager, QuotationItemManager

# Initialize enhanced database and managers
enhanced_db = EnhancedDatabaseManager()
contractor_profile_manager = ContractorProfileManager(enhanced_db)
material_item_manager = MaterialItemManager(enhanced_db)
quotation_manager = QuotationManager(enhanced_db)
quotation_item_manager = QuotationItemManager(enhanced_db)

# Create router for contractor management
router = APIRouter(prefix="/contractors", tags=["contractor-management"])

# Pydantic models for enhanced contractor management
class ContractorCapability(BaseModel):
    name: str
    proficiency_level: Optional[str] = "intermediate"
    years_experience: Optional[int] = 0
    certifications: Optional[str] = None

class ContractorProfileCreate(BaseModel):
    name: str = Field(..., description="Unique contractor/supplier name", example="ABC Construction Supply")
    business_license: Optional[str] = Field(None, description="Official business license number", example="BL-12345-CA")
    address: Optional[str] = Field(None, description="Street address", example="1234 Builder's Way")
    city: Optional[str] = Field(None, description="City", example="Construction City")
    state: Optional[str] = Field(None, description="State/Province", example="CA")
    zip_code: Optional[str] = Field(None, description="ZIP/Postal code", example="90210")
    contact_number: Optional[str] = Field(None, description="Primary phone number", example="(555) 123-4567")
    email: Optional[str] = Field(None, description="Business email address", example="contact@abc-supply.com")
    website: Optional[str] = Field(None, description="Company website", example="https://abc-supply.com")
    specialty: Optional[str] = Field(None, description="Primary business specialty", example="Lumber and Building Materials")
    business_type: Optional[str] = Field("supplier", description="Type of business", example="supplier")
    service_area: Optional[str] = Field("local", description="Geographic service area", example="regional")
    payment_terms: Optional[str] = Field("net30", description="Standard payment terms", example="net30")
    credit_rating: Optional[str] = Field("A", description="Financial credit rating", example="A")
    delivery_options: Optional[str] = Field("both", description="Available delivery options", example="both")
    minimum_order: Optional[float] = Field(0, description="Minimum order amount", example=500.00)
    discount_policy: Optional[str] = Field(None, description="Discount policy details", example="2% net 10, 1% net 30")
    warranty_policy: Optional[str] = Field(None, description="Product warranty policy", example="1 year manufacturer warranty")
    certifications: Optional[List[str]] = Field([], description="Industry certifications", example=["NWFA Certified", "ISO 9001"])
    notes: Optional[str] = Field(None, description="Additional notes", example="Specializes in sustainable lumber products")
    capabilities: Optional[List[ContractorCapability]] = Field([], description="Professional capabilities and expertise")

    class Config:
        schema_extra = {
            "example": {
                "name": "ABC Construction Supply",
                "business_license": "BL-12345-CA",
                "address": "1234 Builder's Way",
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
                "notes": "Specializes in sustainable lumber products",
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
                        "years_experience": 8,
                        "certifications": "AWS Certified"
                    }
                ]
            }
        }

class ContractorProfileUpdate(BaseModel):
    business_license: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    specialty: Optional[str] = None
    business_type: Optional[str] = None
    service_area: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_rating: Optional[str] = None
    delivery_options: Optional[str] = None
    minimum_order: Optional[float] = None
    discount_policy: Optional[str] = None
    warranty_policy: Optional[str] = None
    certifications: Optional[List[str]] = None
    notes: Optional[str] = None

class MaterialItemCreate(BaseModel):
    item_name: str = Field(..., description="Unique material identifier", example="2x4_stud_8ft_premium")
    display_name: Optional[str] = Field(None, description="Human-readable material name", example="2x4 Premium Stud 8ft")
    sku: Optional[str] = Field(None, description="Contractor's SKU/part number", example="ABC-2X4-8-PREM")
    category: Optional[str] = Field(None, description="Primary material category", example="Lumber")
    subcategory: Optional[str] = Field(None, description="Material subcategory", example="Dimensional Lumber")
    unit: Optional[str] = Field("each", description="Unit of measurement", example="each")
    price: float = Field(..., description="Unit price in USD", example=4.25)
    cost: Optional[float] = Field(None, description="Contractor's cost (if available)", example=3.50)
    currency: Optional[str] = Field("USD", description="Price currency", example="USD")
    price_per: Optional[str] = Field(None, description="Price per unit description", example="per piece")
    dimensions: Optional[str] = Field(None, description="Physical dimensions", example="1.5\" x 3.5\" x 8'")
    weight: Optional[float] = Field(None, description="Weight per unit", example=8.5)
    weight_unit: Optional[str] = Field("lbs", description="Weight unit", example="lbs")
    material_type: Optional[str] = Field(None, description="Type of material", example="Southern Pine")
    grade_quality: Optional[str] = Field(None, description="Quality grade", example="Premium Grade")
    brand: Optional[str] = Field(None, description="Brand name", example="ABC Premium")
    manufacturer: Optional[str] = Field(None, description="Manufacturer", example="ABC Mills")
    model_number: Optional[str] = Field(None, description="Model/part number", example="2X4-8-PREM")
    color: Optional[str] = Field(None, description="Color/finish", example="Natural")
    finish: Optional[str] = Field(None, description="Surface finish", example="Kiln Dried")
    description: Optional[str] = Field(None, description="Detailed description", example="Premium grade 2x4 stud, kiln dried for superior quality")
    specifications: Optional[Dict[str, Any]] = Field({}, description="Technical specifications")
    installation_notes: Optional[str] = Field(None, description="Installation guidelines", example="Pre-drill for nails near ends")
    safety_info: Optional[str] = Field(None, description="Safety information", example="Wear safety glasses when cutting")
    compliance_codes: Optional[str] = Field(None, description="Building codes/standards", example="IRC 2021, IBC 2021")
    lead_time_days: Optional[int] = Field(0, description="Lead time in days", example=3)
    stock_quantity: Optional[int] = Field(None, description="Current stock level", example=500)
    minimum_order_qty: Optional[int] = Field(1, description="Minimum order quantity", example=10)
    bulk_pricing: Optional[List[Dict[str, Any]]] = Field([], description="Volume pricing tiers")
    seasonal_availability: Optional[bool] = Field(True, description="Available year-round", example=True)
    is_special_order: Optional[bool] = Field(False, description="Requires special ordering", example=False)

    class Config:
        schema_extra = {
            "example": {
                "item_name": "2x4_stud_8ft_premium",
                "display_name": "2x4 Premium Stud 8ft",
                "sku": "ABC-2X4-8-PREM",
                "category": "Lumber",
                "subcategory": "Dimensional Lumber",
                "unit": "each",
                "price": 4.25,
                "cost": 3.50,
                "currency": "USD",
                "price_per": "per piece",
                "dimensions": "1.5\" x 3.5\" x 8'",
                "weight": 8.5,
                "weight_unit": "lbs",
                "material_type": "Southern Pine",
                "grade_quality": "Premium Grade",
                "brand": "ABC Premium",
                "manufacturer": "ABC Mills",
                "model_number": "2X4-8-PREM",
                "color": "Natural",
                "finish": "Kiln Dried",
                "description": "Premium grade 2x4 stud, kiln dried for superior quality and dimensional stability",
                "specifications": {
                    "moisture_content": "19% max",
                    "grade_stamp": "SPIB",
                    "treatment": "Kiln Dried",
                    "straightness": "1/4\" bow max"
                },
                "installation_notes": "Pre-drill for nails near ends to prevent splitting",
                "safety_info": "Wear safety glasses when cutting. Use dust mask for extended cutting.",
                "compliance_codes": "IRC 2021, IBC 2021, ASTM D245",
                "lead_time_days": 3,
                "stock_quantity": 500,
                "minimum_order_qty": 10,
                "bulk_pricing": [
                    {"quantity": 100, "price": 4.00},
                    {"quantity": 500, "price": 3.75},
                    {"quantity": 1000, "price": 3.50}
                ],
                "seasonal_availability": True,
                "is_special_order": False
            }
        }

class MaterialItemUpdate(BaseModel):
    display_name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    dimensions: Optional[str] = None
    weight: Optional[float] = None
    material_type: Optional[str] = None
    grade_quality: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    color: Optional[str] = None
    finish: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    installation_notes: Optional[str] = None
    safety_info: Optional[str] = None
    compliance_codes: Optional[str] = None
    lead_time_days: Optional[int] = None
    stock_quantity: Optional[int] = None
    minimum_order_qty: Optional[int] = None
    bulk_pricing: Optional[List[Dict[str, Any]]] = None
    seasonal_availability: Optional[bool] = None
    is_special_order: Optional[bool] = None

class ContractorSearchFilters(BaseModel):
    specialty: Optional[str] = None
    business_type: Optional[str] = None
    service_area: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    min_rating: Optional[float] = None

class ContractorReview(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    delivery_rating: Optional[int] = Field(None, ge=1, le=5)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    price_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    reviewer_name: Optional[str] = None
    order_date: Optional[date] = None

# Quotation and Item Models
class QuotationItemCreate(BaseModel):
    item_name: str = Field(..., description="Name of the item", example="Premium Oak Flooring")
    sku: Optional[str] = Field(None, description="SKU/Product Code (optional)", example="OAK-PREM-001")
    unit: str = Field(..., description="Unit of measure", example="per sq ft")
    unit_of_measure: str = Field(..., description="Unit of measure description", example="per sq ft, per piece, per hour")
    cost: float = Field(..., description="Cost per unit", example=12.50)

class QuotationItemResponse(BaseModel):
    item_id: int
    item_name: str
    sku_id: str  # Will be "N/A" if not provided
    unit: str
    unit_of_measure: str
    cost: float
    quantity: float
    total_cost: float
    description: Optional[str]
    category: Optional[str]

class QuotationCreate(BaseModel):
    quotation_name: Optional[str] = Field(None, description="Name of the quotation")
    client_name: Optional[str] = Field(None, description="Client name")
    client_email: Optional[str] = Field(None, description="Client email")
    client_phone: Optional[str] = Field(None, description="Client phone")
    project_address: Optional[str] = Field(None, description="Project address")
    project_description: Optional[str] = Field(None, description="Project description")
    notes: Optional[str] = Field(None, description="Additional notes")
    valid_until: Optional[date] = Field(None, description="Quotation valid until date")
    items: List[QuotationItemCreate] = Field(..., description="List of items to add to quotation")

class SimpleQuotationItem(BaseModel):
    """Simplified quotation item model - only essential fields"""
    item_name: str = Field(..., description="Name of the item")
    sku: Optional[str] = Field(None, description="SKU/Product Code")
    unit: str = Field(..., description="Unit of measure")
    unit_of_measure: str = Field(..., description="Unit description")
    cost: float = Field(..., description="Cost per unit")

class QuotationResponse(BaseModel):
    quotation_id: int
    user_id: int
    quotation_name: Optional[str]
    client_name: Optional[str]
    total_cost: float
    status: str
    item_count: int
    created_at: str
    updated_at: str

# Enhanced Contractor Profile Endpoints
@router.post(
    "/profiles/",
    response_model=dict,
    summary="🏢 Create Contractor Profile",
    description="Create a comprehensive contractor profile with detailed business information, capabilities, and certifications.",
    response_description="Contractor profile created successfully with assigned ID",
    responses={
        200: {
            "description": "Contractor profile created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "contractor_id": 123,
                        "message": "Contractor profile created successfully"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Contractor name already exists"
                    }
                }
            }
        }
    }
)
async def create_contractor_profile(contractor: ContractorProfileCreate):
    """
    ## Create Detailed Contractor Profile 🏢
    
    Create a comprehensive contractor profile with detailed business information.
    
    **Features:**
    - Complete business information (license, address, contact details)
    - Capability tracking with proficiency levels
    - Certification management
    - Payment terms and credit rating
    - Service area and delivery options
    - Professional specializations
    
    **Required Fields:**
    - `name`: Unique contractor name
    
    **Optional Enhancements:**
    - `business_license`: Official business license number
    - `capabilities`: Array of professional capabilities
    - `certifications`: List of industry certifications
    - `payment_terms`: Standard payment terms (net30, net15, etc.)
    - `credit_rating`: Financial credit rating (A, B, C, D)
    
    **Example Use Cases:**
    - Onboarding new suppliers
    - Managing contractor relationships
    - Tracking capabilities and certifications
    - Setting up payment and delivery terms
    """
    try:
        contractor_id = contractor_profile_manager.create_contractor_profile(contractor.dict())
        return {
            "contractor_id": contractor_id, 
            "message": "Contractor profile created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{contractor_id}")
async def get_contractor_profile(contractor_id: int):
    """Get complete contractor profile"""
    try:
        profile = contractor_profile_manager.get_contractor_profile(contractor_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Contractor profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profiles/{contractor_id}")
async def update_contractor_profile(contractor_id: int, updates: ContractorProfileUpdate):
    """Update contractor profile"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        success = contractor_profile_manager.update_contractor_profile(contractor_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Contractor profile not found")
        return {"message": "Contractor profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profiles/search")
async def search_contractor_profiles(filters: ContractorSearchFilters):
    """Search contractor profiles with advanced filtering"""
    try:
        contractors = contractor_profile_manager.search_contractors(filters.dict())
        return {
            "contractors": contractors,
            "total_found": len(contractors),
            "filters_applied": {k: v for k, v in filters.dict().items() if v is not None}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Material Item Management Endpoints
@router.post(
    "/{contractor_id}/items/",
    response_model=dict,
    summary="📦 Add Material Item",
    description="Add a comprehensive material item to contractor inventory with detailed specifications.",
    response_description="Material item added successfully with assigned ID",
    responses={
        200: {
            "description": "Material item added successfully",
            "content": {
                "application/json": {
                    "example": {
                        "material_id": 456,
                        "message": "Material item added successfully"
                    }
                }
            }
        },
        404: {
            "description": "Contractor not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Contractor not found"
                    }
                }
            }
        },
        400: {
            "description": "Invalid material data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Material with this name already exists for this contractor"
                    }
                }
            }
        }
    }
)
async def add_material_item(contractor_id: int, material: MaterialItemCreate):
    """
    ## Add Comprehensive Material Item 📦
    
    Add a detailed material item to a contractor's inventory with complete specifications.
    
    **Features:**
    - Complete material specifications (30+ fields)
    - Pricing and cost tracking
    - Inventory management
    - Technical specifications
    - Safety and compliance information
    - Bulk pricing tiers
    - Lead time tracking
    
    **Required Fields:**
    - `item_name`: Unique material identifier
    - `price`: Unit price in USD
    
    **Enhanced Features:**
    - `specifications`: Technical details as JSON object
    - `bulk_pricing`: Volume pricing tiers
    - `compliance_codes`: Building codes and standards
    - `safety_info`: Safety guidelines and warnings
    - `installation_notes`: Installation guidance
    
    **Example Use Cases:**
    - Building contractor material catalogs
    - Managing lumber and steel inventories
    - Tracking electrical and plumbing supplies
    - Setting up bulk pricing structures
    - Maintaining compliance documentation
    """
    try:
        # Verify contractor exists
        profile = contractor_profile_manager.get_contractor_profile(contractor_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Contractor not found")
        
        material_id = material_item_manager.add_material_item(contractor_id, material.dict())
        return {
            "material_id": material_id,
            "message": "Material item added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{contractor_id}/items/bulk")
async def bulk_add_material_items(contractor_id: int, materials: List[MaterialItemCreate]):
    """Bulk add material items to contractor inventory"""
    try:
        # Verify contractor exists
        profile = contractor_profile_manager.get_contractor_profile(contractor_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Contractor not found")
        
        materials_data = [material.dict() for material in materials]
        results = material_item_manager.bulk_import_materials(contractor_id, materials_data)
        
        return {
            "imported": results["imported"],
            "skipped": results["skipped"],
            "errors": results["errors"],
            "message": f"Bulk import completed: {results['imported']} imported, {results['skipped']} skipped"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{contractor_id}/items/")
async def get_contractor_materials(
    contractor_id: int,
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(100),
    offset: Optional[int] = Query(0)
):
    """Get materials for a contractor with filtering and pagination"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT m.*, c.name as contractor_name
                FROM materials m
                JOIN contractors c ON m.contractor_id = c.id
                WHERE m.contractor_id = ? AND m.discontinued = 0
            '''
            params = [contractor_id]
            
            if category:
                query += ' AND m.category = ?'
                params.append(category)
            
            if search:
                query += ' AND (m.item_name LIKE ? OR m.display_name LIKE ? OR m.description LIKE ?)'
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param])
            
            query += ' ORDER BY m.category, m.item_name LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            materials = []
            
            for row in rows:
                material = dict(zip(columns, row))
                # Parse JSON fields
                if material.get('specifications'):
                    try:
                        material['specifications'] = json.loads(material['specifications'])
                    except:
                        material['specifications'] = {}
                if material.get('bulk_pricing'):
                    try:
                        material['bulk_pricing'] = json.loads(material['bulk_pricing'])
                    except:
                        material['bulk_pricing'] = []
                materials.append(material)
            
            # Get total count
            count_query = 'SELECT COUNT(*) FROM materials WHERE contractor_id = ? AND discontinued = 0'
            count_params = [contractor_id]
            
            if category:
                count_query += ' AND category = ?'
                count_params.append(category)
            
            if search:
                count_query += ' AND (item_name LIKE ? OR display_name LIKE ? OR description LIKE ?)'
                count_params.extend([search_param, search_param, search_param])
            
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            return {
                "materials": materials,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(materials) < total_count
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{material_id}")
async def update_material_item(material_id: int, updates: MaterialItemUpdate):
    """Update material item details"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle JSON fields
            if 'specifications' in update_data and isinstance(update_data['specifications'], dict):
                update_data['specifications'] = json.dumps(update_data['specifications'])
            
            if 'bulk_pricing' in update_data and isinstance(update_data['bulk_pricing'], list):
                update_data['bulk_pricing'] = json.dumps(update_data['bulk_pricing'])
            
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values()) + [material_id]
            
            cursor.execute(f'''
                UPDATE materials 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Material item not found")
            
            conn.commit()
            return {"message": "Material item updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{material_id}/price")
async def update_material_price(
    material_id: int, 
    new_price: float, 
    reason: Optional[str] = None
):
    """Update material price with history tracking"""
    try:
        success = material_item_manager.update_material_pricing(material_id, new_price, reason)
        if not success:
            raise HTTPException(status_code=404, detail="Material item not found")
        return {"message": "Material price updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{material_id}/price-history")
async def get_material_price_history(material_id: int):
    """Get price history for a material item"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT old_price, new_price, change_reason, effective_date, created_at
                FROM price_history 
                WHERE material_id = ?
                ORDER BY created_at DESC
            ''', (material_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            history = [dict(zip(columns, row)) for row in rows]
            
            return {"price_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{material_id}")
async def discontinue_material_item(material_id: int, replacement_item_id: Optional[int] = None):
    """Mark material item as discontinued (soft delete)"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE materials 
                SET discontinued = 1, replacement_item_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (replacement_item_id, material_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Material item not found")
            
            conn.commit()
            return {"message": "Material item marked as discontinued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Material Categories Endpoints
@router.get("/categories/")
async def get_material_categories():
    """Get all material categories"""
    try:
        categories = material_item_manager.get_material_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import/Export Endpoints
@router.post("/{contractor_id}/items/import")
async def import_materials_file(contractor_id: int, file: UploadFile = File(...)):
    """Import materials from CSV/Excel file"""
    try:
        # Verify contractor exists
        profile = contractor_profile_manager.get_contractor_profile(contractor_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Contractor not found")
        
        # Save uploaded file temporarily
        suffix = '.csv' if file.filename.endswith('.csv') else '.xlsx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Import data based on file type
            if file.filename.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(tmp_path)
            else:
                import pandas as pd
                df = pd.read_excel(tmp_path)
            
            # Convert to materials list
            materials = []
            for _, row in df.iterrows():
                material = {
                    'item_name': row.get('item_name') or row.get('name'),
                    'display_name': row.get('display_name'),
                    'category': row.get('category'),
                    'price': float(row.get('price', 0)),
                    'unit': row.get('unit', 'each'),
                    'description': row.get('description'),
                    'specifications': row.get('specifications', {}),
                    'brand': row.get('brand'),
                    'manufacturer': row.get('manufacturer')
                }
                materials.append(material)
            
            # Bulk import
            results = material_item_manager.bulk_import_materials(contractor_id, materials)
            
            return results
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Review and Rating Endpoints
@router.post("/{contractor_id}/reviews/")
async def add_contractor_review(contractor_id: int, review: ContractorReview):
    """Add a review for a contractor"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO contractor_reviews (
                    contractor_id, rating, review_text, delivery_rating, quality_rating,
                    price_rating, service_rating, reviewer_name, order_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contractor_id, review.rating, review.review_text, review.delivery_rating,
                review.quality_rating, review.price_rating, review.service_rating,
                review.reviewer_name, review.order_date
            ))
            
            # Update contractor's average rating
            cursor.execute('''
                UPDATE contractors 
                SET rating = (
                    SELECT AVG(rating) FROM contractor_reviews WHERE contractor_id = ?
                ), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (contractor_id, contractor_id))
            
            conn.commit()
            return {"message": "Review added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{contractor_id}/reviews/")
async def get_contractor_reviews(contractor_id: int, limit: int = Query(10), offset: int = Query(0)):
    """Get reviews for a contractor"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM contractor_reviews 
                WHERE contractor_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (contractor_id, limit, offset))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            reviews = [dict(zip(columns, row)) for row in rows]
            
            return {"reviews": reviews}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quotation Management Endpoints
@router.post(
    "/quotations/create",
    response_model=dict,
    summary="📋 Create Quotation Item",
    description="Create a new quotation with a single item. Simplified endpoint that only requires item details.",
    response_description="Quotation created successfully with item",
    responses={
        200: {
            "description": "Quotation created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Quotation created successfully",
                        "data": {
                            "quotation_id": 123,
                            "item": {
                                "item_id": 456,
                                "item_name": "Premium Oak Flooring",
                                "sku": "OAK-PREM-001",
                                "unit": "per sq ft",
                                "unit_of_measure": "per sq ft",
                                "cost": 12.50,
                                "quantity": 1,
                                "total_cost": 12.50
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Item data is required",
                        "detail": "Item data is required"
                    }
                }
            }
        }
    }
)
async def create_quotation_item(
    user_id: int = Query(..., description="User ID who is creating the quotation"),
    item_data: SimpleQuotationItem = None
):
    """
    ## Create Quotation Item 📋
    
    Create a new quotation with a single item. Simplified endpoint that only requires item details.
    
    **Required Fields:**
    - `user_id`: User creating the quotation
    - `item_name`: Name of the item
    - `unit`: Unit of measure
    - `unit_of_measure`: Unit description
    - `cost`: Cost per unit
    
    **Optional Fields:**
    - `sku`: SKU/Product Code
    
    **Response Format:**
    - `quotation_id`: Auto-assigned quotation ID
    - `item`: Single item with assigned ID and details
    
    **Example Use Cases:**
    - Creating simple quotations with single items
    - Quick item addition to new quotations
    - Simplified contractor pricing setup
    """
    try:
        if not item_data:
            raise HTTPException(status_code=400, detail="Item data is required")
        
        # Create quotation with minimal data
        quotation_id = quotation_manager.create_quotation(user_id, None)
        
        # Add single item to quotation with default values for missing fields
        item_dict = item_data.dict()
        item_dict['quantity'] = 1  # Default quantity
        item_dict['description'] = None  # Default description
        item_dict['category'] = None  # Default category
        
        item_id = quotation_item_manager.add_item_to_quotation(
            quotation_id, 
            item_dict
        )
        
        # Get the created item with all details
        items = quotation_item_manager.get_items_by_quotation(quotation_id)
        created_item = next((i for i in items if i['id'] == item_id), None)
        
        if not created_item:
            raise HTTPException(status_code=500, detail="Failed to retrieve created item")
        
        return {
            "success": True,
            "message": "Quotation created successfully",
            "data": {
                "quotation_id": quotation_id,
                "item": {
                    "item_id": created_item['id'],
                    "item_name": created_item['item_name'],
                    "sku": created_item['sku'],
                    "unit": created_item['unit'],
                    "unit_of_measure": created_item['unit_of_measure'],
                    "cost": created_item['cost'],
                    "quantity": created_item['quantity'],
                    "total_cost": created_item['total_cost'],
                    "description": created_item.get('description'),
                    "category": created_item.get('category')
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/quotations/{quotation_id}/items",
    response_model=dict,
    summary="📦 Get Quotation Items",
    description="Get all items from a specific quotation ID",
    response_description="List of items in the quotation",
    responses={
        200: {
            "description": "Items retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Items retrieved successfully",
                        "data": {
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
                    }
                }
            }
        },
        404: {
            "description": "Quotation not found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Quotation not found",
                        "detail": "Quotation not found"
                    }
                }
            }
        }
    }
)
async def get_quotation_items(quotation_id: int):
    """
    ## Get Quotation Items 📦
    
    Retrieve all items from a specific quotation.
    
    **Response includes:**
    - `item_id`: Auto-assigned item ID
    - `item_name`: Name of the item
    - `sku_id`: SKU/Product Code (or "N/A" if not provided)
    - `unit`: Unit of measure
    - `unit_of_measure`: Unit description
    - `cost`: Cost per unit
    - `quantity`: Quantity
    - `total_cost`: Total cost for this item
    - `total_items`: Total number of items
    - `total_cost`: Total cost of all items
    """
    try:
        # Verify quotation exists
        quotation = quotation_manager.get_quotation(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Get items
        items = quotation_item_manager.get_items_by_quotation(quotation_id)
        
        # Format response
        formatted_items = []
        total_cost = 0
        
        for item in items:
            formatted_items.append({
                "item_id": item['id'],
                "item_name": item['item_name'],
                "sku_id": item['sku'],
                "unit": item['unit'],
                "unit_of_measure": item['unit_of_measure'],
                "cost": item['cost'],
                "quantity": item['quantity'],
                "total_cost": item['total_cost']
            })
            total_cost += item['total_cost']
        
        return {
            "success": True,
            "message": "Items retrieved successfully",
            "data": {
                "quotation_id": quotation_id,
                "items": formatted_items,
                "total_items": len(formatted_items),
                "total_cost": total_cost
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/quotations/{quotation_id}/items",
    response_model=dict,
    summary="➕ Add Item to Quotation",
    description="Add a new item to an existing quotation",
    response_description="Item added successfully",
    responses={
        200: {
            "description": "Item added successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Item added to quotation successfully",
                        "data": {
                            "item_id": 789,
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
                    }
                }
            }
        },
        404: {
            "description": "Quotation not found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Quotation not found",
                        "detail": "Quotation not found"
                    }
                }
            }
        }
    }
)
async def add_item_to_quotation(quotation_id: int, item: QuotationItemCreate):
    """
    ## Add Item to Quotation ➕
    
    Add a new item to an existing quotation.
    
    **Required Fields:**
    - `item_name`: Name of the item
    - `unit`: Unit of measure
    - `unit_of_measure`: Unit description
    - `cost`: Cost per unit
    
    **Optional Fields:**
    - `sku`: SKU/Product Code (returns "N/A" if not provided)
    
    **Response includes:**
    - `item_id`: Auto-assigned item ID
    - Complete item details with calculated total cost
    """
    try:
        # Verify quotation exists
        quotation = quotation_manager.get_quotation(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Add item with default values for missing fields
        item_dict = item.dict()
        item_dict['quantity'] = 1  # Default quantity
        item_dict['description'] = None  # Default description
        item_dict['category'] = None  # Default category
        
        item_id = quotation_item_manager.add_item_to_quotation(
            quotation_id, 
            item_dict
        )
        
        # Get the created item
        items = quotation_item_manager.get_items_by_quotation(quotation_id)
        created_item = next((i for i in items if i['id'] == item_id), None)
        
        if created_item:
            formatted_item = {
                "item_id": created_item['id'],
                "item_name": created_item['item_name'],
                "sku_id": created_item['sku'],
                "unit": created_item['unit'],
                "unit_of_measure": created_item['unit_of_measure'],
                "cost": created_item['cost'],
                "quantity": created_item['quantity'],
                "total_cost": created_item['total_cost']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve created item")
        
        return {
            "success": True,
            "message": "Item added to quotation successfully",
            "data": {
                "item_id": item_id,
                "item": formatted_item
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/quotations/user/{user_id}",
    response_model=dict,
    summary="📋 Get User Quotations",
    description="Get all quotations linked with a specific user ID with optional status filter",
    response_description="List of user's quotations",
    responses={
        200: {
            "description": "Quotations retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "User quotations retrieved successfully",
                        "data": {
                            "user_id": 1,
                            "quotations": [
                                {
                                    "quotation_id": 123,
                                    "quotation_name": "Office Renovation",
                                    "client_name": "ABC Corp",
                                    "total_cost": 1250.00,
                                    "status": "pending",
                                    "item_count": 3,
                                    "skus": ["OAK-PREM-001", "STEEL-001", "NAIL-500"],
                                    "created_at": "2024-01-15T10:30:00",
                                    "updated_at": "2024-01-15T10:30:00"
                                }
                            ],
                            "total_quotations": 1,
                            "status_filter": "pending"
                        }
                    }
                }
            }
        }
    }
)
async def get_user_quotations(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter quotations by status (pending, approved, rejected, draft, sent)")
):
    """
    ## Get User Quotations 📋
    
    Retrieve all quotations for a specific user with optional status filtering.
    
    **Query Parameters:**
    - `status`: Optional filter by quotation status (pending, approved, rejected, draft, sent)
    
    **Response includes:**
    - `quotation_id`: Quotation ID
    - `quotation_name`: Name of the quotation
    - `client_name`: Client name
    - `total_cost`: Total cost of quotation
    - `status`: Quotation status (pending, approved, rejected, draft, sent)
    - `item_count`: Number of items in quotation
    - `skus`: Array of SKUs from all items in the quotation
    - `created_at`: Creation timestamp
    - `updated_at`: Last update timestamp
    - `total_quotations`: Total number of quotations
    - `status_filter`: Applied status filter (if any)
    """
    try:
        # Validate status filter if provided
        valid_statuses = ['pending', 'approved', 'rejected', 'draft', 'sent']
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status filter. Valid options: {', '.join(valid_statuses)}"
            )
        
        quotations = quotation_manager.get_quotations_by_user(user_id, status)
        
        # Format response
        formatted_quotations = []
        for quotation in quotations:
            formatted_quotations.append({
                "quotation_id": quotation['id'],
                "quotation_name": quotation.get('quotation_name'),
                "client_name": quotation.get('client_name'),
                "total_cost": quotation.get('total_cost', 0),
                "status": quotation.get('status', 'draft'),
                "item_count": quotation.get('item_count', 0),
                "skus": quotation.get('skus', []),
                "created_at": quotation.get('created_at'),
                "updated_at": quotation.get('updated_at')
            })
        
        return {
            "success": True,
            "message": "User quotations retrieved successfully",
            "data": {
                "user_id": user_id,
                "quotations": formatted_quotations,
                "total_quotations": len(formatted_quotations),
                "status_filter": status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
