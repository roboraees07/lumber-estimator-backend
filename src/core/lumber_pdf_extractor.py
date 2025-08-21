#!/usr/bin/env python3
"""
Lumber-Specific PDF Extractor
Analyzes architectural PDFs and extracts lumber quantities, dimensions, and materials
"""

import os
import json
import base64
import re
import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Third-party imports
import google.generativeai as genai

from .lumber_database import LumberDatabase, LumberItem
from .lumber_estimation_engine import LumberEstimationEngine

class LumberPDFExtractor:
    """Extracts lumber quantities and dimensions from architectural PDFs"""
    
    def __init__(self):
        """Initialize the lumber PDF extractor"""
        self.lumber_db = LumberDatabase()
        self.lumber_engine = LumberEstimationEngine()
        self.model = None  # Will be initialized when needed
        self.cache_dir = Path("data/pdf_analysis_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_pdf_hash(self, pdf_path: str) -> str:
        """Generate a hash of the PDF file for caching"""
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except:
            return str(Path(pdf_path).stat().st_mtime)  # Fallback to modification time
    
    def _get_cached_result(self, pdf_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        cache_file = self.cache_dir / f"{pdf_hash}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Check if cache is less than 24 hours old
                    cache_time = datetime.fromisoformat(cached_data.get("cache_timestamp", "2000-01-01"))
                    if (datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours
                        print(f"📋 Using cached result for PDF analysis")
                        return cached_data.get("analysis_result")
            except:
                pass
        return None
    
    def _save_to_cache(self, pdf_hash: str, result: Dict[str, Any]):
        """Save analysis result to cache"""
        cache_file = self.cache_dir / f"{pdf_hash}.json"
        cache_data = {
            "cache_timestamp": datetime.now().isoformat(),
            "analysis_result": result
        }
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            print(f"💾 Analysis result cached for future use")
        except Exception as e:
            print(f"⚠️ Failed to cache result: {e}")

    def _ensure_gemini_ready(self):
        """Ensure Gemini is ready, loading environment if needed"""
        if self.model is not None:
            return True
            
        # Try to load environment variables from .env file
        env_file = Path(".env")
        if env_file.exists():
            print("📋 Loading environment from .env file for lumber extraction...")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Environment variables loaded for lumber extraction")
        
        # Now try to initialize Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Gemini AI ready for lumber extraction!")
                return True
            except Exception as e:
                print(f"❌ Gemini setup failed: {e}")
                self.model = None
                return False
        else:
            print("⚠️ Warning: GEMINI_API_KEY not set for lumber extraction")
            self.model = None
            return False

    def convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF to high-resolution images for analysis"""
        images = []
        
        try:
            import fitz  # PyMuPDF
            print("📷 Converting PDF to images for lumber analysis...")
            
            doc = fitz.open(pdf_path)
            print(f"✅ PDF has {len(doc)} pages")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Render page to image with high resolution
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better detail
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                from PIL import Image
                import io
                
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                images.append(img_base64)
                
                # Save image for debugging
                image_path = f"temp_lumber_page_{page_num + 1}.png"
                img.save(image_path)
                print(f"💾 Saved page {page_num + 1}: {image_path}")
            
            doc.close()
            print(f"✅ Successfully converted {len(images)} pages")
            return images
            
        except ImportError:
            print("❌ PyMuPDF not available. Install with: pip install PyMuPDF")
            return []
        except Exception as e:
            print(f"❌ PDF to image conversion failed: {e}")
            return []

    def analyze_pdf_for_lumber(self, images: List[str]) -> Dict[str, Any]:
        """Analyze PDF images specifically for lumber extraction"""
        if not self._ensure_gemini_ready():
            return {"error": "Gemini not available"}
        
        if not images:
            return {"error": "No images to analyze"}
        
        all_materials = []
        building_dimensions = None
        
        for page_num, img_base64 in enumerate(images):
            print(f"🔍 Analyzing page {page_num + 1} for lumber quantities...")
            
            prompt = f"""
            You are an expert construction estimator and civil engineer. Analyze this architectural/construction drawing and extract SPECIFIC lumber and construction materials.

            This is page {page_num + 1} of a construction document.

            CRITICAL: Focus on EXTRACTING BUILDING DIMENSIONS and LUMBER QUANTITIES.

            IMPORTANT: For building dimensions, you MUST extract BOTH length and width. If you cannot determine a dimension, estimate it based on the drawing scale or typical construction practices. NEVER return null for length or width.

            ANALYSIS APPROACH - Follow this EXACT sequence:
            1. First, identify the drawing scale and any explicit dimensions
            2. Calculate building dimensions from floor plan measurements
            3. Count visible structural elements (studs, joists, rafters)
            4. Apply standard construction spacing rules consistently
            5. Use the SAME calculation method for similar elements

            STANDARD CONSTRUCTION RULES (use these EXACTLY):
            - Stud spacing: 16 inches on center
            - Joist spacing: 16 inches on center  
            - Rafter spacing: 24 inches on center
            - Wall height: 8 feet (unless specified otherwise)
            - Waste factor: 15% for all materials

            Return ONLY a valid JSON in this exact format:
            {{
                "page": {page_num + 1},
                "building_dimensions": {{
                    "length_feet": number (REQUIRED - never null),
                    "width_feet": number (REQUIRED - never null),
                    "height_feet": number (estimate if not shown),
                    "area_sqft": number (calculate from length × width),
                    "perimeter_feet": number (calculate from 2 × (length + width))
                }},
                "lumber_materials": [
                    {{
                        "item_name": "specific lumber name (e.g., 2X4 STUD, 2X8 JOIST)",
                        "quantity": number (be specific - count studs, joists, rafters, etc.),
                        "unit": "each/lf/sheet/pack",
                        "category": "Walls/Joist/Roof/Cornice and Decking/Post & Beams",
                        "dimensions": "size description (e.g., 2X4X8, 2X8X16)",
                        "location": "where used (e.g., wall framing, floor joists, roof rafters)"
                    }}
                ],
                "other_materials": [
                    {{
                        "item_name": "material name (be specific - e.g., 'Electrical Outlet', 'Ceiling Light', 'Roof Shingles')",
                        "quantity": number (count actual items or calculate area needed),
                        "unit": "each/sf/lf/cf/etc",
                        "category": "electrical/plumbing/hvac/finishes/structural",
                        "dimensions": "size if shown (e.g., 4x4, 6x6, 12x12)",
                        "location": "where used (e.g., kitchen, living room, exterior wall)"
                    }}
                ]
            }}

            LUMBER FOCUS AREAS:
            - **Wall Framing**: 2X4, 2X6 studs, plates, headers
            - **Floor Joists**: 2X8, 2X10, 2X12 joists, joist hangers
            - **Roof Rafters**: 2X6, 2X8 rafters, roof sheathing
            - **Sheathing**: OSB, plywood sheets for walls and roof
            - **Beams**: LVL beams, posts, structural elements

            DIMENSION EXTRACTION:
            - Look for scale indicators, dimensions, room sizes
            - Calculate area from floor plan measurements
            - Estimate height from section drawings
            - Count studs, joists, rafters based on spacing
            - If dimensions are not explicitly shown, estimate based on:
              * Drawing scale (e.g., 1/4" = 1' means 1 inch on paper = 4 feet)
              * Room sizes and layouts
              * Typical construction practices
              * Compare with known elements in the drawing

            QUANTITY CALCULATION:
            - Count visible materials in drawings
            - Estimate based on building dimensions
            - Use standard construction spacing (16" for studs, 16" for joists, 24" for rafters)
            - Include waste factor considerations

            Be SPECIFIC with quantities and dimensions. If exact numbers aren't shown, estimate based on standard construction practices.
            """
            
            try:
                # Create image part for Gemini Vision
                image_part = {
                    "mime_type": "image/png",
                    "data": img_base64
                }
                
                response = self.model.generate_content([prompt, image_part])
                response_text = response.text
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    page_result = json.loads(json_match.group())
                    
                    # Extract building dimensions (use first page with dimensions)
                    if not building_dimensions and "building_dimensions" in page_result:
                        building_dimensions = page_result["building_dimensions"]
                        print(f"✅ Found building dimensions: {building_dimensions}")
                    
                    # Extract lumber materials
                    if "lumber_materials" in page_result:
                        all_materials.extend(page_result["lumber_materials"])
                        print(f"✅ Page {page_num + 1}: Found {len(page_result['lumber_materials'])} lumber materials")
                    
                    # Extract other materials
                    if "other_materials" in page_result:
                        all_materials.extend(page_result["other_materials"])
                        print(f"✅ Page {page_num + 1}: Found {len(page_result['other_materials'])} other materials")
                        
                else:
                    print(f"⚠️ Page {page_num + 1}: Could not parse response")
                
            except Exception as e:
                print(f"⚠️ Page {page_num + 1} analysis failed: {e}")
        
        return {
            "building_dimensions": building_dimensions,
            "materials": all_materials,
            "total_materials": len(all_materials)
        }

    def match_extracted_materials_to_database(self, materials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match extracted materials to lumber database items and find contractor sources"""
        matched_materials = []
        
        # Enhanced contractor database with material categories
        contractor_material_categories = {
            "Walls": ["Quality Hardware & Lumber", "Builders Supply Co", "Lumber Depot"],
            "Joist": ["Quality Hardware & Lumber", "Builders Supply Co", "Structural Lumber Co"],
            "Roof": ["Quality Hardware & Lumber", "Roofing Supply Co", "Builders Supply Co"],
            "Cornice and Decking": ["Quality Hardware & Lumber", "Exterior Supply Co", "Builders Supply Co"],
            "Post & Beams": ["Quality Hardware & Lumber", "Structural Lumber Co", "Builders Supply Co"],
            "electrical": ["ElectroMax Electrical Supply", "Quality Hardware & Lumber", "Electrical Depot"],
            "plumbing": ["PlumbRight Supply", "Quality Hardware & Lumber", "Plumbing World"],
            "hvac": ["HVAC Supply Co", "Quality Hardware & Lumber", "Climate Control Supply"],
            "finishes": ["Quality Hardware & Lumber", "Finish Supply Co", "Interior Materials Co"],
            "structural": ["Quality Hardware & Lumber", "Structural Lumber Co", "Builders Supply Co"],
            "mechanical": ["Quality Hardware & Lumber", "Mechanical Supply Co", "Builders Supply Co"]
        }
        
        for material in materials:
            item_name = material.get("item_name", "").lower()
            category = material.get("category", "")
            quantity = material.get("quantity", 1)
            unit = material.get("unit", "each")
            dimensions = material.get("dimensions", "")
            location = material.get("location", "")
            
            # Determine material type for contractor matching
            material_type = self._categorize_material_for_contractors(category, item_name)
            
            # Get available contractors for this material type
            available_contractors = contractor_material_categories.get(material_type, ["Quality Hardware & Lumber"])
            
            # Search for matching lumber items
            if category in ["Walls", "Joist", "Roof", "Cornice and Decking", "Post & Beams"]:
                # Search in lumber database
                search_results = self.lumber_db.search_items(item_name)
                
                # If no direct match, try searching with variations
                if not search_results:
                    # Try common variations
                    variations = [
                        item_name.replace(" ", ""),
                        item_name.replace(" ", "_"),
                        item_name.replace(" ", "-"),
                        item_name.split()[0] if " " in item_name else item_name,
                        item_name.split()[-1] if " " in item_name else item_name
                    ]
                    
                    for variation in variations:
                        if variation and len(variation) > 2:  # Avoid very short searches
                            search_results = self.lumber_db.search_items(variation)
                            if search_results:
                                break
                
                if search_results:
                    # Find best match
                    best_match = search_results[0]
                    matched_materials.append({
                        "extracted_item": {
                            "item_name": material.get("item_name"),
                            "category": category,
                            "dimensions": dimensions,
                            "location": location,
                            "quantity": quantity,
                            "unit": unit
                        },
                        "database_match": {
                            "item_id": best_match.item_id,
                            "description": best_match.description,
                            "category": best_match.category,
                            "subcategory": best_match.subcategory,
                            "dimensions": best_match.dimensions,
                            "material": best_match.material,
                            "grade": best_match.grade,
                            "unit_price": best_match.unit_price,
                            "unit": best_match.unit
                        },
                        "quantity_needed": quantity,
                        "total_cost": best_match.unit_price * quantity,
                        "match_confidence": "high" if len(search_results) == 1 else "medium",
                        "available_contractors": available_contractors,
                        "recommended_contractor": available_contractors[0] if available_contractors else "Quote needed",
                        "material_type": material_type,
                        "notes": f"Matched to database item: {best_match.description}"
                    })
                else:
                    # No match found, add as unmatched item
                    matched_materials.append({
                        "extracted_item": {
                            "item_name": material.get("item_name"),
                            "category": category,
                            "dimensions": dimensions,
                            "location": location,
                            "quantity": quantity,
                            "unit": unit
                        },
                        "database_match": None,
                        "quantity_needed": quantity,
                        "total_cost": "Quote needed",
                        "match_confidence": "none",
                        "available_contractors": available_contractors,
                        "recommended_contractor": available_contractors[0] if available_contractors else "Quote needed",
                        "material_type": material_type,
                        "notes": "Item not found in database - requires contractor quote"
                    })
            else:
                # For non-lumber materials, also try to find matches in the lumber database
                # as some items might be categorized differently
                search_results = self.lumber_db.search_items(item_name)
                
                if search_results:
                    # Found a match in lumber database
                    best_match = search_results[0]
                    matched_materials.append({
                        "extracted_item": {
                            "item_name": material.get("item_name"),
                            "category": category,
                            "dimensions": dimensions,
                            "location": location,
                            "quantity": quantity,
                            "unit": unit
                        },
                        "database_match": {
                            "item_id": best_match.item_id,
                            "description": best_match.description,
                            "category": best_match.category,
                            "subcategory": best_match.subcategory,
                            "dimensions": best_match.dimensions,
                            "material": best_match.material,
                            "grade": best_match.grade,
                            "unit_price": best_match.unit_price,
                            "unit": best_match.unit
                        },
                        "quantity_needed": quantity,
                        "total_cost": best_match.unit_price * quantity,
                        "match_confidence": "medium",
                        "available_contractors": available_contractors,
                        "recommended_contractor": available_contractors[0] if available_contractors else "Quote needed",
                        "material_type": material_type,
                        "notes": f"Matched to lumber database: {best_match.description}"
                    })
                else:
                    # Non-lumber material with no match
                    matched_materials.append({
                        "extracted_item": {
                            "item_name": material.get("item_name"),
                            "category": category,
                            "dimensions": dimensions,
                            "location": location,
                            "quantity": quantity,
                            "unit": unit
                        },
                        "database_match": None,
                        "quantity_needed": quantity,
                        "total_cost": "Quote needed",
                        "match_confidence": "non-lumber",
                        "available_contractors": available_contractors,
                        "recommended_contractor": available_contractors[0] if available_contractors else "Quote needed",
                        "material_type": material_type,
                        "notes": f"Non-lumber material - {category} category"
                    })
        
        return matched_materials
    
    def _categorize_material_for_contractors(self, category: str, item_name: str) -> str:
        """Categorize material for contractor matching"""
        item_lower = item_name.lower()
        
        # Lumber categories
        if category in ["Walls", "Joist", "Roof", "Cornice and Decking", "Post & Beams"]:
            return category.lower()
        
        # Electrical items
        if any(word in item_lower for word in ["outlet", "switch", "light", "fan", "ceiling", "can", "flush", "led", "smoke", "detector", "garage", "pull", "wall", "eaves", "exterior", "disc", "disposal"]):
            return "electrical"
        
        # Plumbing items
        if any(word in item_lower for word in ["pipe", "fitting", "fixture", "faucet", "toilet", "sink", "drain", "valve", "pump"]):
            return "plumbing"
        
        # HVAC items
        if any(word in item_lower for word in ["hvac", "duct", "vent", "air", "heating", "cooling", "furnace", "ac", "thermostat"]):
            return "hvac"
        
        # Structural items
        if any(word in item_lower for word in ["beam", "column", "steel", "concrete", "rebar", "anchor", "bolt", "fastener"]):
            return "structural"
        
        # Mechanical items
        if any(word in item_lower for word in ["motor", "pump", "compressor", "generator", "engine", "transmission"]):
            return "mechanical"
        
        # Default to finishes for other items
        return "finishes"
    
    def _generate_contractor_summary(self, matched_materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of contractors needed for the project"""
        contractor_summary = {}
        
        for material in matched_materials:
            contractors = material.get("available_contractors", [])
            material_type = material.get("material_type", "unknown")
            quantity = material.get("quantity_needed", 0)
            
            for contractor in contractors:
                if contractor not in contractor_summary:
                    contractor_summary[contractor] = {
                        "materials": [],
                        "total_items": 0,
                        "estimated_cost": 0,
                        "material_types": set()
                    }
                
                contractor_summary[contractor]["materials"].append({
                    "item_name": material["extracted_item"]["item_name"],
                    "quantity": quantity,
                    "unit": material["extracted_item"]["unit"],
                    "category": material["extracted_item"]["category"],
                    "estimated_cost": material.get("total_cost", "Quote needed")
                })
                
                contractor_summary[contractor]["total_items"] += quantity
                contractor_summary[contractor]["material_types"].add(material_type)
                
                if isinstance(material.get("total_cost"), (int, float)):
                    contractor_summary[contractor]["estimated_cost"] += material["total_cost"]
        
        # Convert sets to lists for JSON serialization
        for contractor in contractor_summary:
            contractor_summary[contractor]["material_types"] = list(contractor_summary[contractor]["material_types"])
        
        return contractor_summary
    
    def _generate_material_category_summary(self, matched_materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of materials by category"""
        category_summary = {}
        
        for material in matched_materials:
            category = material["extracted_item"]["category"]
            material_type = material.get("material_type", "unknown")
            quantity = material.get("quantity_needed", 0)
            
            if category not in category_summary:
                category_summary[category] = {
                    "total_quantity": 0,
                    "items": [],
                    "contractors": set(),
                    "estimated_cost": 0
                }
            
            category_summary[category]["total_quantity"] += quantity
            category_summary[category]["items"].append({
                "item_name": material["extracted_item"]["item_name"],
                "quantity": quantity,
                "unit": material["extracted_item"]["unit"],
                "dimensions": material["extracted_item"]["dimensions"],
                "location": material["extracted_item"]["location"],
                "recommended_contractor": material.get("recommended_contractor", "Quote needed"),
                "estimated_cost": material.get("total_cost", "Quote needed")
            })
            
            # Add contractors for this category
            contractors = material.get("available_contractors", [])
            category_summary[category]["contractors"].update(contractors)
            
            # Add to estimated cost
            if isinstance(material.get("total_cost"), (int, float)):
                category_summary[category]["estimated_cost"] += material["total_cost"]
        
        # Convert sets to lists for JSON serialization
        for category in category_summary:
            category_summary[category]["contractors"] = list(category_summary[category]["contractors"])
        
        return category_summary
    
    def _generate_simple_summary(self, materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a simple summary of all items found"""
        summary = {
            "total_items_found": len(materials),
            "items_by_category": {},
            "total_quantities": {}
        }
        
        for material in materials:
            category = material.get("category", "Unknown")
            item_name = material.get("item_name", "Unknown")
            quantity = material.get("quantity", 0)
            unit = material.get("unit", "each")
            
            # Initialize category if not exists
            if category not in summary["items_by_category"]:
                summary["items_by_category"][category] = []
                summary["total_quantities"][category] = 0
            
            # Add item to category
            summary["items_by_category"][category].append({
                "item": item_name,
                "quantity": quantity,
                "unit": unit
            })
            
            # Add to total quantity
            summary["total_quantities"][category] += quantity
        
        return summary
    
    def _generate_simple_detailed_items(self, matched_materials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate simple detailed information for each item"""
        detailed_items = []
        
        for material in matched_materials:
            extracted_item = material["extracted_item"]
            
            # Create simple item detail
            item_detail = {
                "item_name": extracted_item["item_name"],
                "category": extracted_item["category"],
                "quantity_needed": material["quantity_needed"],
                "unit": extracted_item["unit"],
                "dimensions": extracted_item.get("dimensions", ""),
                "location": extracted_item.get("location", ""),
                "database_match": "Available" if material["database_match"] else "Quotation needed",
                "unit_price": material["database_match"]["unit_price"] if material["database_match"] else "Quotation needed",
                "total_price": material["total_cost"] if isinstance(material["total_cost"], (int, float)) else "Quotation needed",
                "available_contractors": material["available_contractors"],
                "recommended_contractor": material["recommended_contractor"]
            }
            
            # Add database details if available
            if material["database_match"]:
                item_detail.update({
                    "item_id": material["database_match"]["item_id"],
                    "description": material["database_match"]["description"],
                    "material": material["database_match"]["material"],
                    "grade": material["database_match"]["grade"]
                })
            
            # Add lumber-specific details for lumber items
            if extracted_item["category"] in ["Walls", "Joist", "Roof", "Cornice and Decking", "Post & Beams"]:
                if extracted_item.get("dimensions"):
                    dims = extracted_item["dimensions"].split("X")
                    if len(dims) >= 2:
                        item_detail["lumber_specs"] = {
                            "width_inches": dims[0] if len(dims) > 0 else "",
                            "thickness_inches": dims[1] if len(dims) > 1 else "",
                            "length_feet": dims[2] if len(dims) > 2 else ""
                        }
                
                # Add construction standards info
                item_detail["construction_info"] = {
                    "spacing": "16\" on center" if "stud" in extracted_item["item_name"].lower() else "24\" on center" if "rafter" in extracted_item["item_name"].lower() else "As specified",
                    "waste_factor": "15%",
                    "installation_notes": "Standard construction practices apply"
                }
            
            detailed_items.append(item_detail)
        
        return detailed_items
    
    def _generate_lumber_estimates(self, matched_materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed lumber estimates with specifications"""
        lumber_estimates = {
            "total_lumber_items": 0,
            "total_lumber_cost": 0,
            "lumber_by_category": {},
            "detailed_lumber_specs": []
        }
        
        for material in matched_materials:
            extracted_item = material["extracted_item"]
            category = extracted_item["category"]
            
            # Only process lumber materials
            if category in ["Walls", "Joist", "Roof", "Cornice and Decking", "Post & Beams"]:
                lumber_estimates["total_lumber_items"] += 1
                
                # Initialize category if not exists
                if category not in lumber_estimates["lumber_by_category"]:
                    lumber_estimates["lumber_by_category"][category] = {
                        "items": [],
                        "total_quantity": 0,
                        "total_cost": 0
                    }
                
                # Create detailed lumber specification
                lumber_spec = {
                    "item_name": extracted_item["item_name"],
                    "category": category,
                    "specifications": {
                        "dimensions": extracted_item.get("dimensions", ""),
                        "material": material["database_match"]["material"] if material["database_match"] else "Unknown",
                        "grade": material["database_match"]["grade"] if material["database_match"] else "Unknown",
                        "length": extracted_item.get("dimensions", "").split("X")[-1] if "X" in extracted_item.get("dimensions", "") else "",
                        "width": extracted_item.get("dimensions", "").split("X")[0] if "X" in extracted_item.get("dimensions", "") else "",
                        "thickness": extracted_item.get("dimensions", "").split("X")[1] if len(extracted_item.get("dimensions", "").split("X")) > 2 else ""
                    },
                    "quantity": {
                        "needed": material["quantity_needed"],
                        "unit": extracted_item["unit"],
                        "location": extracted_item.get("location", "")
                    },
                    "pricing": {
                        "unit_price": material["database_match"]["unit_price"] if material["database_match"] else "Quotation needed",
                        "total_price": material["total_cost"] if isinstance(material["total_cost"], (int, float)) else "Quotation needed",
                        "price_per_unit": f"${material['database_match']['unit_price']:.2f}" if material["database_match"] else "Quotation needed"
                    },
                    "sourcing": {
                        "available_contractors": material["available_contractors"],
                        "recommended_contractor": material["recommended_contractor"],
                        "database_match": "Available" if material["database_match"] else "Quotation needed"
                    }
                }
                
                # Add database details if available
                if material["database_match"]:
                    lumber_spec["database_info"] = {
                        "item_id": material["database_match"]["item_id"],
                        "description": material["database_match"]["description"],
                        "subcategory": material["database_match"]["subcategory"]
                    }
                    lumber_spec["pricing"]["unit_price"] = material["database_match"]["unit_price"]
                    lumber_spec["pricing"]["total_price"] = material["total_cost"]
                    
                    # Add to total cost
                    if isinstance(material["total_cost"], (int, float)):
                        lumber_estimates["total_lumber_cost"] += material["total_cost"]
                        lumber_estimates["lumber_by_category"][category]["total_cost"] += material["total_cost"]
                
                # Add to category summary
                lumber_estimates["lumber_by_category"][category]["items"].append({
                    "item_name": extracted_item["item_name"],
                    "quantity": material["quantity_needed"],
                    "unit_price": lumber_spec["pricing"]["unit_price"],
                    "total_cost": lumber_spec["pricing"]["total_price"]
                })
                lumber_estimates["lumber_by_category"][category]["total_quantity"] += material["quantity_needed"]
                
                # Add to detailed specs
                lumber_estimates["detailed_lumber_specs"].append(lumber_spec)
        
        return lumber_estimates

    def generate_lumber_estimate_from_pdf(self, pdf_path: str, project_name: str = "PDF Project", force_fresh: bool = False) -> Dict[str, Any]:
        """Generate complete lumber estimate from PDF"""
        
        print(f"🏗️ Starting lumber estimation from PDF: {Path(pdf_path).name}")
        
        # Check cache first (unless forcing fresh analysis)
        if not force_fresh:
            pdf_hash = self._get_pdf_hash(pdf_path)
            cached_result = self._get_cached_result(pdf_hash)
            if cached_result:
                # Update project name and timestamp for cached result
                cached_result["project_info"]["project_name"] = project_name
                cached_result["project_info"]["analysis_date"] = datetime.now().isoformat()
                cached_result["analysis_timestamp"] = datetime.now().isoformat()
                print(f"✅ Returning cached analysis result")
                return cached_result
        else:
            print(f"🔄 Forcing fresh analysis (ignoring cache)")
        
        pdf_hash = self._get_pdf_hash(pdf_path)
        
        # Step 1: Convert PDF to images
        images = self.convert_pdf_to_images(pdf_path)
        if not images:
            return {"error": "Failed to convert PDF to images"}
        
        # Step 2: Analyze images for lumber extraction
        extraction_result = self.analyze_pdf_for_lumber(images)
        if "error" in extraction_result:
            return extraction_result
        
        # Step 3: Match materials to database
        matched_materials = self.match_extracted_materials_to_database(extraction_result["materials"])
        
        # Step 4: Generate simplified estimates
        estimates = {
            "project_info": {
                "project_name": project_name,
                "pdf_filename": Path(pdf_path).name,
                "analysis_date": datetime.now().isoformat(),
                "extraction_method": "AI-powered PDF analysis"
            },
            "building_dimensions": extraction_result["building_dimensions"],
            "summary": self._generate_simple_summary(extraction_result["materials"]),
            "detailed_items": self._generate_simple_detailed_items(matched_materials),
            "lumber_estimates": self._generate_lumber_estimates(matched_materials)
        }
        
        # Step 5: If we have building dimensions, generate full lumber estimate
        if extraction_result["building_dimensions"]:
            try:
                dims = extraction_result["building_dimensions"]
                
                # Validate and clean dimensions
                length = dims.get("length_feet")
                width = dims.get("width_feet")
                height = dims.get("height_feet", 8.0)
                
                # Check if we have valid dimensions for estimation
                if length is None or width is None:
                    print(f"⚠️ Missing dimensions: length={length}, width={width}")
                    print(f"   Cannot generate full lumber estimate without complete dimensions")
                    estimates["full_lumber_estimate"] = {
                        "status": "Incomplete dimensions",
                        "message": f"Need both length ({length}) and width ({width}) for accurate estimation",
                        "available_dimensions": dims
                    }
                else:
                    # Validate dimensions are positive numbers
                    if length <= 0 or width <= 0:
                        print(f"⚠️ Invalid dimensions: length={length}, width={width}")
                        estimates["full_lumber_estimate"] = {
                            "status": "Invalid dimensions",
                            "message": f"Dimensions must be positive numbers: length={length}, width={width}",
                            "available_dimensions": dims
                        }
                    else:
                        print(f"✅ Valid dimensions: {length}' x {width}' x {height}'")
                        full_estimate = self.lumber_engine.estimate_complete_project(
                            length=length,
                            width=width,
                            height=height,
                            project_name=project_name
                        )
                        
                        estimates["full_lumber_estimate"] = {
                            "status": "Success",
                            "total_area_sqft": full_estimate.total_area_sqft,
                            "total_cost": full_estimate.total_cost,
                            "message": f"Generated full lumber estimate: ${full_estimate.total_cost:.2f}"
                        }
                
            except Exception as e:
                print(f"⚠️ Full lumber estimate generation failed: {e}")
                estimates["full_lumber_estimate"] = {
                    "status": "Error",
                    "message": str(e)
                }
        
        # Save results
        output_dir = Path("outputs/lumber_pdf_estimates")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{project_name}_pdf_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(estimates, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")
        
        # Cache the result for future use
        self._save_to_cache(pdf_hash, estimates)
        
        return estimates
        
        return estimates

# Global instance - will be created when first accessed
_lumber_pdf_extractor_instance = None

def get_lumber_pdf_extractor():
    """Get or create the lumber PDF extractor instance"""
    global _lumber_pdf_extractor_instance
    if _lumber_pdf_extractor_instance is None:
        _lumber_pdf_extractor_instance = LumberPDFExtractor()
    return _lumber_pdf_extractor_instance

# For backward compatibility
lumber_pdf_extractor = get_lumber_pdf_extractor()
