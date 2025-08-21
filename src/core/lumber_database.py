#!/usr/bin/env python3
"""
Lumber Database
Contains comprehensive lumber items with descriptions, unit prices, and specifications
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class LumberItem:
    """Represents a lumber item with all specifications"""
    item_id: str
    description: str
    category: str
    subcategory: str
    dimensions: str
    material: str
    grade: str
    unit_price: float
    unit: str
    length_feet: Optional[float] = None
    width_inches: Optional[float] = None
    thickness_inches: Optional[float] = None

class LumberDatabase:
    """Comprehensive lumber database with pricing and specifications"""
    
    def __init__(self):
        self.items = self._initialize_database()
    
    def _initialize_database(self) -> Dict[str, LumberItem]:
        """Initialize the lumber database with all items"""
        items = {}
        
        # Walls Category
        walls_items = [
            # 2x4 Studs
            ("2X4X104-5/8_KD_HF", "2X4X104-5/8 KD HF STUD", "Walls", "Studs", "2X4X104-5/8", "KD HF", "STUD", 4.37, "lf", 8.72, 4, 2),
            ("2X4X12_KD_HFIR", "2X4X12 KD H-FIR STD&BTR", "Walls", "Studs", "2X4X12", "KD H-FIR", "STD&BTR", 5.71, "lf", 12, 4, 2),
            ("2X4X16_SYP_BORATES", "2X4X16 SYP #3 BORATES INT", "Walls", "Studs", "2X4X16", "SYP", "#3 BORATES INT", 8.77, "lf", 16, 4, 2),
            ("2X4X12_KD_HFIR_2", "2X4X12 KD H-FIR STD&BTR", "Walls", "Studs", "2X4X12", "KD H-FIR", "STD&BTR", 5.85, "lf", 12, 4, 2),
            ("2X4X14_KD_HFIR", "2X4X14 KD H-FIR STD&BTR", "Walls", "Studs", "2X4X14", "KD H-FIR", "STD&BTR", 7.63, "lf", 14, 4, 2),
            ("2X4X16_KD_HFIR", "2X4X16 KD H-FIR STD&BTR", "Walls", "Studs", "2X4X16", "KD H-FIR", "STD&BTR", 8.71, "lf", 16, 4, 2),
            ("2X4X140-5/8_FJ_KD_SPF", "2X4X140-5/8 FJ KD SPF", "Walls", "Studs", "2X4X140-5/8", "FJ KD SPF", "STUD", 6.79, "lf", 11.72, 4, 2),
            
            # 2x6 Studs
            ("2X6X12_KD_HFIR", "2X6X12 KD H-FIR #2&BTR", "Walls", "Studs", "2X6X12", "KD H-FIR", "#2&BTR", 8.25, "lf", 12, 6, 2),
            ("2X6X140-5/8_FJ_KD_SPF", "2X6X140-5/8 FJ KD SPF", "Walls", "Studs", "2X6X140-5/8", "FJ KD SPF", "STUD", 9.89, "lf", 11.72, 6, 2),
            ("2X6X16_SYP_BORATES", "2X6X16 SYP #3 BORATES INT", "Walls", "Studs", "2X6X16", "SYP", "#3 BORATES INT", 13.55, "lf", 16, 6, 2),
            ("2X6X16_KD_HFIR", "2X6X16 KD H-FIR #2&BTR", "Walls", "Studs", "2X6X16", "KD H-FIR", "#2&BTR", 11.54, "lf", 16, 6, 2),
            
            # LVL Beams
            ("LVL_1-3/4X16X20", "1-3/4X16X20 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X16X20", "LVL", "2.0BTR", 165.41, "each", 20, 16, 1.75),
            ("LVL_1-3/4X11-7/8X28", "1-3/4X11-7/8X28 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X28", "LVL", "2.0BTR", 204.57, "each", 28, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X22", "1-3/4X11-7/8X22 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X22", "LVL", "2.0BTR", 124.52, "each", 22, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X20", "1-3/4X11-7/8X20 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X20", "LVL", "2.0BTR", 116.21, "each", 20, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X18", "1-3/4X11-7/8X18 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X18", "LVL", "2.0BTR", 127.42, "each", 18, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X16", "1-3/4X11-7/8X16 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X16", "LVL", "2.0BTR", 108.22, "each", 16, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X14", "1-3/4X11-7/8X14 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X14", "LVL", "2.0BTR", 97.72, "each", 14, 11.875, 1.75),
            ("LVL_1-3/4X11-7/8X12", "1-3/4X11-7/8X12 LVL 2.0BTR", "Walls", "LVL Beams", "1-3/4X11-7/8X12", "LVL", "2.0BTR", 79.20, "each", 12, 11.875, 1.75),
            
            # Other Wall Items
            ("2X12X12_KD_HFIR", "2X12X12 KD H-FIR #2&BTR", "Walls", "Headers", "2X12X12", "KD H-FIR", "#2&BTR", 19.99, "lf", 12, 12, 2),
            ("2X12X14_KD_HFIR", "2X12X14 KD H-FIR #2&BTR", "Walls", "Headers", "2X12X14", "KD H-FIR", "#2&BTR", 30.25, "lf", 14, 12, 2),
            ("LVL_3-1/2X5-1/2", "3-1/2X5-1/2 LVL 1.7E", "Walls", "LVL Beams", "3-1/2X5-1/2", "LVL", "1.7E", 8.92, "lf", 1, 5.5, 3.5),
            
            # Fasteners and Hardware
            ("HEX_NUT_1/2_ZINC", "1/2 HEX NUT ZINC", "Walls", "Fasteners", "1/2", "ZINC", "HEX", 0.17, "each"),
            ("FLAT_WASHER_1/2_ZINC", "1/2 USS FLAT WASHER ZINC", "Walls", "Fasteners", "1/2", "ZINC", "USS", 0.19, "each"),
            ("STB2-50414F25", "STB2-50414F25 1/2X4-1/4", "Walls", "Fasteners", "1/2X4-1/4", "STEEL", "STB2", 1.04, "each"),
            
            # Sheathing
            ("OSB_7/16X4X8", "7/16X4X8 OSB", "Walls", "Sheathing", "7/16X4X8", "OSB", "STANDARD", 9.70, "sheet", 8, 4, 0.4375),
            ("ZIP_WALL_7/16X4X10", "7/16X4X10 ZIP WALL", "Walls", "Sheathing", "7/16X4X10", "ZIP", "WALL", 31.84, "sheet", 10, 4, 0.4375),
            ("ZIP_TAPE_30YD", "ZIP TAPE 30 YD", "Walls", "Fasteners", "30 YD", "ZIP", "TAPE", 31.54, "roll"),
            
            # Generic items that PDF extractor looks for
            ("2X6_RAFTER_16", "2X6 RAFTER 16'", "Walls", "Generic", "2X6X16", "KD H-FIR", "#2&BTR", 16.11, "each", 16, 6, 2),
            ("2X4_STUD_8", "2X4 STUD 8'", "Walls", "Generic", "2X4X8", "KD H-FIR", "STD&BTR", 5.71, "each", 8, 4, 2),
            ("2X4_TOP_PLATE_12", "2X4 TOP PLATE 12'", "Walls", "Generic", "2X4X12", "KD H-FIR", "STD&BTR", 5.71, "lf", 12, 4, 2),
            ("2X4_BOTTOM_PLATE_12", "2X4 BOTTOM PLATE 12'", "Walls", "Generic", "2X4X12", "KD H-FIR", "STD&BTR", 5.71, "lf", 12, 4, 2),
            
            # Additional generic items for PDF extraction
            ("PLYWOOD_SHEATHING_4X8", "Plywood Sheathing 4x8", "Walls", "Sheathing", "4X8", "PLYWOOD", "STANDARD", 12.50, "sheet", 8, 4, 0.5),
            ("2X6_FASCIA_12", "2X6 Fascia 12'", "Walls", "Trim", "2X6X12", "KD H-FIR", "#2&BTR", 8.25, "lf", 12, 6, 2),
            ("ROOF_SHINGLES", "Roof Shingles", "Roof", "Shingles", "STANDARD", "ASPHALT", "3-TAB", 45.00, "square", 100, 0, 0),
            ("FLASHING", "Flashing", "Roof", "Flashing", "STANDARD", "ALUMINUM", "COIL", 2.50, "lf", 10, 0, 0),
            ("NAILS_3IN", "3 inch Nails", "Structural", "Fasteners", "3IN", "STEEL", "GALVANIZED", 8.99, "pack", 0, 0, 0),
            ("SCREWS_3IN", "3 inch Screws", "Structural", "Fasteners", "3IN", "STEEL", "PHILLIPS", 12.99, "pack", 0, 0, 0),
            
            # Additional common construction items
            ("OSB_SHEATHING_4X8", "OSB Sheathing 4x8", "Walls", "Sheathing", "4X8", "OSB", "STANDARD", 9.70, "sheet", 8, 4, 0.4375),
            ("2X8_RAFTER_16", "2X8 Rafter 16'", "Roof", "Rafters", "2X8X16", "KD H-FIR", "#2&BTR", 21.67, "each", 16, 8, 2),
            ("2X10_RAFTER_16", "2X10 Rafter 16'", "Roof", "Rafters", "2X10X16", "KD H-FIR", "#2&BTR", 28.50, "each", 16, 10, 2),
            ("2X12_RAFTER_16", "2X12 Rafter 16'", "Roof", "Rafters", "2X12X16", "KD H-FIR", "#2&BTR", 34.19, "each", 16, 12, 2),
            ("2X6_RAFTER_12", "2X6 Rafter 12'", "Roof", "Rafters", "2X6X12", "KD H-FIR", "#2&BTR", 12.79, "each", 12, 6, 2),
            ("2X8_RAFTER_12", "2X8 Rafter 12'", "Roof", "Rafters", "2X8X12", "KD H-FIR", "#2&BTR", 16.52, "each", 12, 8, 2),
            ("2X10_RAFTER_12", "2X10 Rafter 12'", "Roof", "Rafters", "2X10X12", "KD H-FIR", "#2&BTR", 22.00, "each", 12, 10, 2),
            ("2X12_RAFTER_12", "2X12 Rafter 12'", "Roof", "Rafters", "2X12X12", "KD H-FIR", "#2&BTR", 29.39, "each", 12, 12, 2),
        ]
        
        # Joist Category
        joist_items = [
            # LVL Joists
            ("LVL_JOIST_1-3/4X16X24", "1-3/4X16X24 LVL 2.0BTR", "Joist", "LVL Joists", "1-3/4X16X24", "LVL", "2.0BTR", 200.95, "each", 24, 16, 1.75),
            ("LVL_JOIST_1-3/4X11-7/8X12", "1-3/4X11-7/8X12 LVL 2.0BTR", "Joist", "LVL Joists", "1-3/4X11-7/8X12", "LVL", "2.0BTR", 81.37, "each", 12, 11.875, 1.75),
            ("LVL_JOIST_1-3/4X11-7/8X16", "1-3/4X11-7/8X16 LVL 2.0BTR", "Joist", "LVL Joists", "1-3/4X11-7/8X16", "LVL", "2.0BTR", 111.19, "each", 16, 11.875, 1.75),
            ("LVL_JOIST_1-3/4X11-7/8X14", "1-3/4X11-7/8X14 LVL 2.0BTR", "Joist", "LVL Joists", "1-3/4X11-7/8X14", "LVL", "2.0BTR", 100.40, "each", 14, 11.875, 1.75),
            ("LVL_JOIST_1-3/4X11-7/8X20", "1-3/4X11-7/8X20 LVL 2.0BTR", "Joist", "LVL Joists", "1-3/4X11-7/8X20", "LVL", "2.0BTR", 119.39, "each", 20, 11.875, 1.75),
            
            # 2x12 Joists
            ("2X12X24_GDF_HF", "2X12X24 GDF/HF 2B", "Joist", "Dimensional Lumber", "2X12X24", "GDF/HF", "2B", 70.79, "lf", 24, 12, 2),
            ("2X12X20_KD_HFIR", "2X12X20 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X12X20", "KD H-FIR", "#2&BTR", 34.19, "lf", 20, 12, 2),
            ("2X12X18_KD_HFIR", "2X12X18 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X12X18", "KD H-FIR", "#2&BTR", 29.39, "lf", 18, 12, 2),
            ("2X12X14_KD_HFIR", "2X12X14 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X12X14", "KD H-FIR", "#2&BTR", 30.25, "lf", 14, 12, 2),
            
            # 2x8 Joists
            ("2X8X20_KD_HFIR", "2X8X20 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X8X20", "KD H-FIR", "#2&BTR", 21.67, "lf", 20, 8, 2),
            ("2X8X18_KD_HFIR", "2X8X18 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X8X18", "KD H-FIR", "#2&BTR", 17.44, "lf", 18, 8, 2),
            ("2X8X16_KD_HFIR", "2X8X16 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X8X16", "KD H-FIR", "#2&BTR", 16.11, "lf", 16, 8, 2),
            ("2X8X14_KD_HFIR", "2X8X14 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X8X14", "KD H-FIR", "#2&BTR", 12.79, "lf", 14, 8, 2),
            
            # 2x6 Joists
            ("2X6X20_KD_HFIR", "2X6X20 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X20", "KD H-FIR", "#2&BTR", 14.07, "lf", 20, 6, 2),
            ("2X6X18_KD_HFIR", "2X6X18 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X18", "KD H-FIR", "#2&BTR", 13.74, "lf", 18, 6, 2),
            ("2X6X16_KD_HFIR", "2X6X16 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X16", "KD H-FIR", "#2&BTR", 11.83, "lf", 16, 6, 2),
            ("2X6X14_KD_HFIR", "2X6X14 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X14", "KD H-FIR", "#2&BTR", 8.80, "lf", 14, 6, 2),
            ("2X6X12_KD_HFIR", "2X6X12 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X12", "KD H-FIR", "#2&BTR", 8.45, "lf", 12, 6, 2),
            ("2X6X10_KD_HFIR", "2X6X10 KD H-FIR #2&BTR", "Joist", "Dimensional Lumber", "2X6X10", "KD H-FIR", "#2&BTR", 6.70, "lf", 10, 6, 2),
            
            # Joist Hangers
            ("HU412_25", "HU412 (25)", "Joist", "Hardware", "HU412", "STEEL", "25 PACK", 18.02, "pack"),
            ("HU416_25", "HU416 (25)", "Joist", "Hardware", "HU416", "STEEL", "25 PACK", 23.09, "pack"),
        ]
        
        # Roof Category
        roof_items = [
            # Joist Hangers
            ("LUS26Z_100", "LUS26Z (100)", "Roof", "Hardware", "LUS26Z", "STEEL", "100 PACK", 1.37, "pack"),
            
            # 2x8 Roof Rafters
            ("2X8X32_GDF_HF", "2X8X32 GDF/HF 2B", "Roof", "Rafters", "2X8X32", "GDF/HF", "2B", 106.69, "lf", 32, 8, 2),
            ("2X8X28_GDF_HF", "2X8X28 GDF/HF 2B", "Roof", "Rafters", "2X8X28", "GDF/HF", "2B", 77.99, "lf", 28, 8, 2),
            ("2X8X24_GDF_HF", "2X8X24 GDF/HF 2B", "Roof", "Rafters", "2X8X24", "GDF/HF", "2B", 34.69, "lf", 24, 8, 2),
            ("2X8X22_GDF_HF", "2X8X22 GDF/HF 2B", "Roof", "Rafters", "2X8X22", "GDF/HF", "2B", 35.58, "lf", 22, 8, 2),
            ("2X8X20_KD_HFIR_ROOF", "2X8X20 KD H-FIR #2&BTR", "Roof", "Rafters", "2X8X20", "KD H-FIR", "#2&BTR", 21.67, "lf", 20, 8, 2),
            ("2X8X18_KD_HFIR_ROOF", "2X8X18 KD H-FIR #2&BTR", "Roof", "Rafters", "2X8X18", "KD H-FIR", "#2&BTR", 17.44, "lf", 18, 8, 2),
            ("2X8X16_KD_HFIR_ROOF", "2X8X16 KD H-FIR #2&BTR", "Roof", "Rafters", "2X8X16", "KD H-FIR", "#2&BTR", 16.52, "lf", 16, 8, 2),
            ("2X8X12_KD_HFIR_ROOF", "2X8X12 KD H-FIR #2&BTR", "Roof", "Rafters", "2X8X12", "KD H-FIR", "#2&BTR", 10.68, "lf", 12, 8, 2),
            ("2X8X10_KD_HFIR_ROOF", "2X8X10 KD H-FIR #2&BTR", "Roof", "Rafters", "2X8X10", "KD H-FIR", "#2&BTR", 8.91, "lf", 10, 8, 2),
            
            # 2x6 Roof Rafters
            ("2X6X32_GDF_HF", "2X6X32 GDF/HF 2B", "Roof", "Rafters", "2X6X32", "GDF/HF", "2B", 71.03, "lf", 32, 6, 2),
            ("2X6X30_GDF_HF", "2X6X30 GDF/HF 2B", "Roof", "Rafters", "2X6X30", "GDF/HF", "2B", 66.27, "lf", 30, 6, 2),
            ("2X6X28_GDF_HF", "2X6X28 GDF/HF 2B", "Roof", "Rafters", "2X6X28", "GDF/HF", "2B", 64.82, "lf", 28, 6, 2),
            ("2X6X26_GDF_HF", "2X6X26 GDF/HF 2B", "Roof", "Rafters", "2X6X26", "GDF/HF", "2B", 61.66, "lf", 26, 6, 2),
            ("2X6X24_GDF_HF", "2X6X24 GDF/HF 2B", "Roof", "Rafters", "2X6X24", "GDF/HF", "2B", 25.68, "lf", 24, 6, 2),
            ("2X6X22_GDF_HF", "2X6X22 GDF/HF 2B", "Roof", "Rafters", "2X6X22", "GDF/HF", "2B", 23.68, "lf", 22, 6, 2),
            ("2X6X20_KD_HFIR_ROOF", "2X6X20 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X20", "KD H-FIR", "#2&BTR", 14.07, "lf", 20, 6, 2),
            ("2X6X18_KD_HFIR_ROOF", "2X6X18 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X18", "KD H-FIR", "#2&BTR", 13.74, "lf", 18, 6, 2),
            ("2X6X16_KD_HFIR_ROOF", "2X6X16 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X16", "KD H-FIR", "#2&BTR", 11.83, "lf", 16, 6, 2),
            ("2X6X14_KD_HFIR_ROOF", "2X6X14 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X14", "KD H-FIR", "#2&BTR", 8.80, "lf", 14, 6, 2),
            ("2X6X12_KD_HFIR_ROOF", "2X6X12 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X12", "KD H-FIR", "#2&BTR", 8.45, "lf", 12, 6, 2),
            ("2X6X10_KD_HFIR_ROOF", "2X6X10 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X10", "KD H-FIR", "#2&BTR", 6.70, "lf", 10, 6, 2),
            ("2X6X8_KD_HFIR_ROOF", "2X6X8 KD H-FIR #2&BTR", "Roof", "Rafters", "2X6X8", "KD H-FIR", "#2&BTR", 5.48, "lf", 8, 6, 2),
        ]
        
        # Cornice and Decking Category
        cornice_items = [
            # OSB and Soffit
            ("OSB_8X6X16_TXT_LAP", "8X6X16 TXT OSBSMRT LAP", "Cornice and Decking", "Soffit", "8X6X16", "OSB", "TXT LAP", 10.96, "sheet", 16, 6, 0.75),
            ("OSB_3/8X12X16_TXT_LAP", "3/8X12X16 TXT OSBSMRT LAP", "Cornice and Decking", "Soffit", "3/8X12X16", "OSB", "TXT LAP", 22.50, "sheet", 16, 12, 0.375),
            ("OSB_3/8X4X8_TXT_SOFFIT", "3/8X4X8 TXT OSBSMRT SOFFIT", "Cornice and Decking", "Soffit", "3/8X4X8", "OSB", "TXT SOFFIT", 45.95, "sheet", 8, 4, 0.375),
            ("OSB_3/8X16X16_SLD_SOFF", "3/8X16X16 SLD OSBSMRT SOFF", "Cornice and Decking", "Soffit", "3/8X16X16", "OSB", "SLD SOFF", 40.68, "sheet", 16, 16, 0.375),
            
            # Vents and Hardware
            ("UNDEREAVE_VENT_8X16_WHITE", "8X16 UNDEREAVE VENT WHITE", "Cornice and Decking", "Vents", "8X16", "PLASTIC", "WHITE", 2.62, "each", 1, 16, 8),
            ("SIDING_CORNER_12_TEX_ALUM", "SIDING CORNER 12\" TEX ALUM", "Cornice and Decking", "Trim", "12\"", "ALUMINUM", "TEXTURED", 3.08, "lf", 1, 12, 0.125),
            
            # Trim
            ("TRIM_4/4X2X16_TXT", "4/4X2X16 TXT OSBSMRT TRIM", "Cornice and Decking", "Trim", "4/4X2X16", "OSB", "TXT TRIM", 9.05, "lf", 16, 2, 1),
            ("TRIM_4/4X4X16_TXT", "4/4X4X16 TXT OSBSMRT TRIM", "Cornice and Decking", "Trim", "4/4X4X16", "OSB", "TXT TRIM", 14.42, "lf", 16, 4, 1),
            ("TRIM_4/4X8X16_TXT", "4/4X8X16 TXT OSBSMRT TRIM", "Cornice and Decking", "Trim", "4/4X8X16", "OSB", "TXT TRIM", 33.82, "lf", 16, 8, 1),
            
            # Other
            ("OSB_7/16X4X8_CORNICE", "7/16X4X8 OSB", "Cornice and Decking", "Sheathing", "7/16X4X8", "OSB", "STANDARD", 9.70, "sheet", 8, 4, 0.4375),
            ("PSCA_7/16_250", "PSCA 7/16 (250)", "Cornice and Decking", "Fasteners", "7/16", "STEEL", "250 PACK", 0.07, "pack"),
        ]
        
        # Post & Beams Category
        post_beam_items = [
            ("POST_6X6X12_GDF_RS", "6X6X12 GDF R/S", "Post & Beams", "Posts", "6X6X12", "GDF", "R/S", 125.16, "each", 12, 6, 6),
            ("APB66R_6", "APB66R (6)", "Post & Beams", "Hardware", "APB66R", "STEEL", "6 PACK", 45.88, "pack"),
            ("BEAM_8X8-20_DF", "8X8-20 DF", "Post & Beams", "Beams", "8X8-20", "DF", "STANDARD", 800.95, "each", 20, 8, 8),
            ("BEAM_8X12-14_DF", "8X12-14 DF", "Post & Beams", "Beams", "8X12-14", "DF", "STANDARD", 560.66, "each", 14, 12, 8),
            ("BEAM_8X12+10_DF", "8X12+10 DF", "Post & Beams", "Beams", "8X12+10", "DF", "STANDARD", 400.47, "each", 10, 12, 8),
            ("BEAM_8X12_DF", "8X12 DF", "Post & Beams", "Beams", "8X12", "DF", "STANDARD", 320.38, "each", 12, 12, 8),
        ]
        
        # Combine all items
        all_items = walls_items + joist_items + roof_items + cornice_items + post_beam_items
        
        # Create LumberItem objects
        for item_data in all_items:
            if len(item_data) == 9:  # Items without dimensions
                item = LumberItem(
                    item_id=item_data[0],
                    description=item_data[1],
                    category=item_data[2],
                    subcategory=item_data[3],
                    dimensions=item_data[4],
                    material=item_data[5],
                    grade=item_data[6],
                    unit_price=item_data[7],
                    unit=item_data[8]
                )
            else:  # Items with dimensions
                item = LumberItem(
                    item_id=item_data[0],
                    description=item_data[1],
                    category=item_data[2],
                    subcategory=item_data[3],
                    dimensions=item_data[4],
                    material=item_data[5],
                    grade=item_data[6],
                    unit_price=item_data[7],
                    unit=item_data[8],
                    length_feet=item_data[9],
                    width_inches=item_data[10],
                    thickness_inches=item_data[11]
                )
            
            items[item.item_id] = item
        
        return items
    
    def get_all_items(self) -> List[LumberItem]:
        """Get all lumber items"""
        return list(self.items.values())
    
    def get_items_by_category(self, category: str) -> List[LumberItem]:
        """Get items by category"""
        return [item for item in self.items.values() if item.category == category]
    
    def get_items_by_subcategory(self, subcategory: str) -> List[LumberItem]:
        """Get items by subcategory"""
        return [item for item in self.items.values() if item.subcategory == subcategory]
    
    def search_items(self, query: str) -> List[LumberItem]:
        """Search items by description, material, or grade with improved matching"""
        query = query.lower().strip()
        results = []
        
        # Common item name variations and synonyms
        item_variations = {
            "stud": ["stud", "2x4", "2x6", "2x8", "2x10", "2x12"],
            "rafter": ["rafter", "2x6", "2x8", "2x10", "2x12"],
            "plate": ["plate", "top plate", "bottom plate", "2x4"],
            "fascia": ["fascia", "2x6", "trim"],
            "sheathing": ["sheathing", "plywood", "osb", "4x8", "4x10"],
            "shingles": ["shingles", "roof shingles", "asphalt"],
            "flashing": ["flashing", "roof flashing"],
            "nails": ["nails", "nail", "fastener"],
            "screws": ["screws", "screw", "fastener"]
        }
        
        for item in self.items.values():
            item_desc = item.description.lower()
            item_material = item.material.lower()
            item_grade = item.grade.lower()
            item_dims = item.dimensions.lower()
            
            # Direct text match
            if (query in item_desc or 
                query in item_material or 
                query in item_grade or
                query in item_dims):
                results.append(item)
                continue
            
            # Check for variations and synonyms
            for category, variations in item_variations.items():
                if query in variations:
                    # Check if this item matches the category
                    if any(var in item_desc for var in variations):
                        results.append(item)
                        break
            
            # Fuzzy matching for common patterns
            if "2x" in query and "2x" in item_dims:
                # Extract dimensions and compare
                query_dims = query.replace("2x", "").replace(" ", "").lower()
                item_dims_clean = item_dims.replace("2x", "").replace(" ", "").lower()
                if query_dims in item_dims_clean or item_dims_clean in query_dims:
                    results.append(item)
                    continue
            
            # Handle sheathing variations
            if "sheathing" in query or "plywood" in query:
                if "sheathing" in item_desc or "plywood" in item_desc or "osb" in item_desc:
                    results.append(item)
                    continue
            
            # Handle trim and fascia
            if "fascia" in query or "trim" in query:
                if "fascia" in item_desc or "trim" in item_desc:
                    results.append(item)
                    continue
        
        # Sort results by relevance (exact matches first, then partial matches)
        def sort_key(item):
            item_desc = item.description.lower()
            if query in item_desc:
                return 0  # Exact match
            elif any(word in item_desc for word in query.split()):
                return 1  # Partial match
            else:
                return 2  # Fuzzy match
        
        results.sort(key=sort_key)
        return results
    
    def get_item_by_id(self, item_id: str) -> Optional[LumberItem]:
        """Get item by ID"""
        return self.items.get(item_id)
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(set(item.category for item in self.items.values()))
    
    def get_subcategories(self) -> List[str]:
        """Get all available subcategories"""
        return list(set(item.subcategory for item in self.items.values()))
    
    def export_to_json(self, filepath: str = None) -> str:
        """Export database to JSON file"""
        if not filepath:
            filepath = "lumber_database.json"
        
        data = {}
        for item_id, item in self.items.items():
            data[item_id] = {
                "description": item.description,
                "category": item.category,
                "subcategory": item.subcategory,
                "dimensions": item.dimensions,
                "material": item.material,
                "grade": item.grade,
                "unit_price": item.unit_price,
                "unit": item.unit,
                "length_feet": item.length_feet,
                "width_inches": item.width_inches,
                "thickness_inches": item.thickness_inches
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath

# Global instance
lumber_db = LumberDatabase()

