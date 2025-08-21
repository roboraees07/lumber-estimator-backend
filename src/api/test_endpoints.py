#!/usr/bin/env python3
"""
Test API Endpoints
No authentication required - for testing PDF upload and lumber estimation
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pathlib import Path
import shutil
import os
from datetime import datetime

from ..core.lumber_pdf_extractor import lumber_pdf_extractor
from ..core.lumber_estimation_engine import lumber_estimation_engine
from ..core.lumber_database import lumber_db

# Create router
router = APIRouter(prefix="/test", tags=["Test Endpoints"])

@router.post(
    "/upload-pdf-estimate",
    summary="📄 Test PDF Upload & Lumber Estimation",
    description="Upload a PDF and get both general material estimates and lumber-specific estimates. NO AUTHENTICATION REQUIRED.",
    response_description="Complete analysis with both material and lumber estimates"
)
async def test_pdf_upload_and_estimation(
    file: UploadFile = File(..., description="Architectural PDF file", example="building_plans.pdf"),
    project_name: str = Form("Test Project", description="Project name for the estimate")
):
    """
    ## Test PDF Upload & Lumber Estimation 📄
    
    **NO AUTHENTICATION REQUIRED** - This endpoint is for testing purposes.
    
    Upload an architectural PDF and get:
    1. **General Material Analysis** - All materials found in the PDF
    2. **Lumber-Specific Analysis** - Lumber quantities and costs
    3. **Building Dimensions** - Extracted from the drawings
    4. **Complete Lumber Estimate** - Based on extracted dimensions
    
    **What Gets Analyzed:**
    - Building dimensions and area calculations
    - Wall framing materials (studs, plates, headers)
    - Floor joist requirements
    - Roof rafter specifications
    - Sheathing needs
    - Hardware and fasteners
    
    **Response Includes:**
    - Extracted materials with quantities
    - Database matches with pricing
    - Full lumber estimate with costs
    - Building specifications
    - Analysis confidence levels
    """
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create temp directory for uploads
        temp_dir = Path("data/test_uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded PDF
        pdf_path = temp_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"📁 PDF saved to: {pdf_path}")
        
        # Generate lumber estimate from PDF
        print("🔍 Starting PDF analysis...")
        lumber_estimate = lumber_pdf_extractor.generate_lumber_estimate_from_pdf(
            str(pdf_path), 
            project_name
        )
        
        if "error" in lumber_estimate:
            raise HTTPException(status_code=500, detail=f"PDF analysis failed: {lumber_estimate['error']}")
        
        # Clean up temp file
        try:
            os.unlink(pdf_path)
            print(f"🗑️ Cleaned up temp file: {pdf_path}")
        except:
            pass
        
        return {
            "success": True,
            "message": "PDF analysis completed successfully",
            "project_name": project_name,
            "pdf_filename": file.filename,
            "analysis_timestamp": datetime.now().isoformat(),
            "results": lumber_estimate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        try:
            if 'pdf_path' in locals():
                os.unlink(pdf_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

@router.post(
    "/manual-lumber-estimate",
    summary="🏗️ Test Manual Lumber Estimation",
    description="Test lumber estimation with manual dimensions. NO AUTHENTICATION REQUIRED.",
    response_description="Complete lumber estimate based on manual dimensions"
)
async def test_manual_lumber_estimation(
    length: float = Form(..., description="Length in feet", example=40.0),
    width: float = Form(..., description="Width in feet", example=30.0),
    height: float = Form(8.0, description="Height in feet", example=8.0),
    project_name: str = Form("Manual Test Project", description="Project name")
):
    """
    ## Test Manual Lumber Estimation 🏗️
    
    **NO AUTHENTICATION REQUIRED** - This endpoint is for testing purposes.
    
    Generate a complete lumber estimate based on manual dimensions.
    
    **What Gets Calculated:**
    - Wall framing (studs, plates, headers)
    - Floor joists (size and quantity)
    - Roof rafters (with pitch calculations)
    - Sheathing requirements
    - Hardware and fasteners
    
    **Construction Standards Applied:**
    - 16" stud spacing
    - 16" joist spacing
    - 24" rafter spacing
    - 15% waste factor
    """
    
    try:
        # Generate estimate
        estimate = lumber_estimation_engine.estimate_complete_project(
            length=length,
            width=width,
            height=height,
            project_name=project_name
        )
        
        # Convert to serializable format
        response_data = {
            "project_name": estimate.project_name,
            "dimensions": f"{length:.1f}' x {width:.1f}' x {height:.1f}'",
            "total_area_sqft": estimate.total_area_sqft,
            "perimeter_feet": estimate.summary["perimeter_feet"],
            "total_cost": estimate.total_cost,
            "cost_per_sqft": estimate.summary["cost_per_sqft"],
            "waste_factor": estimate.summary["waste_factor"],
            "total_lumber_items": estimate.summary["total_lumber_items"],
            "estimates_by_category": {}
        }
        
        # Add category breakdowns
        for category, estimates in estimate.estimates_by_category.items():
            if estimates:
                response_data["estimates_by_category"][category] = []
                for est in estimates:
                    response_data["estimates_by_category"][category].append({
                        "description": est.item.description,
                        "dimensions": est.item.dimensions,
                        "material": est.item.material,
                        "grade": est.item.grade,
                        "quantity_needed": est.quantity_needed,
                        "unit": est.item.unit,
                        "unit_price": est.unit_price,
                        "total_cost": est.total_cost,
                        "area_coverage": est.area_coverage,
                        "notes": est.notes
                    })
        
        return {
            "success": True,
            "message": "Manual lumber estimation completed successfully",
            "estimate": response_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual estimation failed: {str(e)}")

@router.get(
    "/lumber-database",
    summary="📋 Test Lumber Database Access",
    description="Test access to the lumber database. NO AUTHENTICATION REQUIRED.",
    response_description="Lumber database overview and sample items"
)
async def test_lumber_database():
    """
    ## Test Lumber Database Access 📋
    
    **NO AUTHENTICATION REQUIRED** - This endpoint is for testing purposes.
    
    Get an overview of the lumber database including:
    - Total number of items
    - Available categories
    - Sample items from each category
    - Database structure information
    """
    
    try:
        # Get database overview
        all_items = lumber_db.get_all_items()
        categories = lumber_db.get_categories()
        subcategories = lumber_db.get_subcategories()
        
        # Get sample items from each category
        category_samples = {}
        for category in categories:
            items = lumber_db.get_items_by_category(category)
            category_samples[category] = {
                "total_items": len(items),
                "sample_items": []
            }
            
            # Add first 3 items as samples
            for item in items[:3]:
                category_samples[category]["sample_items"].append({
                    "description": item.description,
                    "dimensions": item.dimensions,
                    "material": item.material,
                    "grade": item.grade,
                    "unit_price": item.unit_price,
                    "unit": item.unit
                })
        
        return {
            "success": True,
            "message": "Lumber database access successful",
            "database_overview": {
                "total_items": len(all_items),
                "total_categories": len(categories),
                "total_subcategories": len(subcategories),
                "categories": categories,
                "subcategories": subcategories
            },
            "category_samples": category_samples
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database access failed: {str(e)}")

@router.get(
    "/search-lumber",
    summary="🔍 Test Lumber Search",
    description="Test lumber search functionality. NO AUTHENTICATION REQUIRED.",
    response_description="Search results for lumber items"
)
async def test_lumber_search(query: str):
    """
    ## Test Lumber Search 🔍
    
    **NO AUTHENTICATION REQUIRED** - This endpoint is for testing purposes.
    
    Search the lumber database for specific items.
    
    **Search Examples:**
    - `2x4` - Find all 2x4 lumber
    - `LVL` - Find all LVL beams
    - `OSB` - Find all OSB sheathing
    - `stud` - Find all stud materials
    """
    
    try:
        # Search for items
        results = lumber_db.search_items(query)
        
        # Convert to serializable format
        items = []
        for item in results:
            items.append({
                "item_id": item.item_id,
                "description": item.description,
                "category": item.category,
                "subcategory": item.subcategory,
                "dimensions": item.dimensions,
                "material": item.material,
                "grade": item.grade,
                "unit_price": item.unit_price,
                "unit": item.unit
            })
        
        return {
            "success": True,
            "message": "Lumber search completed successfully",
            "search_query": query,
            "total_found": len(items),
            "results": items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get(
    "/health",
    summary="💚 Test System Health",
    description="Check if all lumber estimation components are working. NO AUTHENTICATION REQUIRED.",
    response_description="System health status"
)
async def test_system_health():
    """
    ## Test System Health 💚
    
    **NO AUTHENTICATION REQUIRED** - This endpoint is for testing purposes.
    
    Check the health of all lumber estimation system components:
    - Lumber database
    - Estimation engine
    - PDF extractor
    - API endpoints
    """
    
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check lumber database
        try:
            all_items = lumber_db.get_all_items()
            health_status["components"]["lumber_database"] = {
                "status": "healthy",
                "total_items": len(all_items),
                "categories": len(lumber_db.get_categories())
            }
        except Exception as e:
            health_status["components"]["lumber_database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "unhealthy"
        
        # Check estimation engine
        try:
            test_area = lumber_estimation_engine.calculate_area_requirements(10, 10, 8)
            health_status["components"]["estimation_engine"] = {
                "status": "healthy",
                "test_area_sqft": test_area.area_sqft,
                "test_perimeter_feet": test_area.perimeter_feet
            }
        except Exception as e:
            health_status["components"]["estimation_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "unhealthy"
        
        # Check PDF extractor
        try:
            api_key = lumber_pdf_extractor.api_key
            health_status["components"]["pdf_extractor"] = {
                "status": "healthy" if api_key else "limited",
                "gemini_available": api_key is not None,
                "note": "Limited functionality without Gemini API key" if not api_key else "Full functionality available"
            }
        except Exception as e:
            health_status["components"]["pdf_extractor"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "unhealthy"
        
        return {
            "success": True,
            "message": "System health check completed",
            "health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "System health check failed",
            "error": str(e),
            "health": {
                "overall_status": "error",
                "timestamp": datetime.now().isoformat()
            }
        }


