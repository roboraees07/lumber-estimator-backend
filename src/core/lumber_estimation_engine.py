#!/usr/bin/env python3
"""
Lumber Estimation Engine
Analyzes architectural areas and calculates lumber quantities and costs
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

from .lumber_database import LumberDatabase, LumberItem

@dataclass
class AreaSpecification:
    """Represents an architectural area with dimensions"""
    name: str
    length_feet: float
    width_feet: float
    height_feet: float
    area_sqft: float
    perimeter_feet: float
    category: str  # Walls, Floor, Roof, etc.

@dataclass
class LumberEstimate:
    """Represents a lumber estimate for a specific item"""
    item: LumberItem
    quantity_needed: float
    unit_price: float
    total_cost: float
    area_coverage: str
    notes: str

@dataclass
class ProjectEstimate:
    """Complete project lumber estimate"""
    project_name: str
    total_area_sqft: float
    total_cost: float
    estimates_by_category: Dict[str, List[LumberEstimate]]
    summary: Dict[str, Any]
    timestamp: str

class LumberEstimationEngine:
    """Engine for calculating lumber quantities and costs based on architectural areas"""
    
    def __init__(self):
        self.lumber_db = LumberDatabase()
        
        # Standard construction practices and ratios
        self.construction_standards = {
            "wall_stud_spacing": 16,  # inches between studs
            "joist_spacing": 16,      # inches between joists
            "rafter_spacing": 24,     # inches between rafters
            "header_height": 12,      # inches for door/window headers
            "plate_thickness": 2,     # inches for top/bottom plates
            "sheathing_coverage": 0.95,  # 95% coverage for sheathing
            "waste_factor": 1.15,     # 15% waste factor
        }
    
    def calculate_area_requirements(self, length: float, width: float, height: float = 8.0) -> AreaSpecification:
        """Calculate area requirements for a given space"""
        area_sqft = length * width
        perimeter_feet = 2 * (length + width)
        
        return AreaSpecification(
            name="Main Area",
            length_feet=length,
            width_feet=width,
            height_feet=height,
            area_sqft=area_sqft,
            perimeter_feet=perimeter_feet,
            category="General"
        )
    
    def estimate_wall_framing(self, area: AreaSpecification) -> List[LumberEstimate]:
        """Estimate wall framing lumber requirements"""
        estimates = []
        
        # Calculate studs needed
        perimeter_feet = area.perimeter_feet
        stud_spacing_inches = self.construction_standards["wall_stud_spacing"]
        studs_needed = math.ceil((perimeter_feet * 12) / stud_spacing_inches)
        
        # Add corner studs and extra for openings
        studs_needed += 4  # Corner studs
        studs_needed += math.ceil(perimeter_feet / 8)  # Extra for openings
        
        # Calculate plates (top and bottom)
        plates_needed = perimeter_feet * 2
        
        # Find appropriate stud size based on height
        if area.height_feet <= 8:
            stud_size = "2X4"
            stud_length = 8
        elif area.height_feet <= 10:
            stud_size = "2X4"
            stud_length = 10
        else:
            stud_size = "2X6"
            stud_length = 12
        
        # Find matching lumber items
        stud_items = self.lumber_db.get_items_by_subcategory("Studs")
        plate_items = self.lumber_db.get_items_by_subcategory("Headers")
        
        # Select best stud option
        best_stud = None
        for item in stud_items:
            if (f"{stud_size}X{stud_length}" in item.dimensions and 
                item.length_feet >= area.height_feet):
                if best_stud is None or item.unit_price < best_stud.unit_price:
                    best_stud = item
        
        # Select best plate option
        best_plate = None
        for item in plate_items:
            if f"{stud_size}X{stud_length}" in item.dimensions:
                if best_plate is None or item.unit_price < best_plate.unit_price:
                    best_plate = item
        
        if best_stud:
            estimates.append(LumberEstimate(
                item=best_stud,
                quantity_needed=studs_needed,
                unit_price=best_stud.unit_price,
                total_cost=best_stud.unit_price * studs_needed,
                area_coverage=f"Wall studs for {area.perimeter_feet:.1f} linear feet",
                notes=f"Spaced at {stud_spacing_inches}\" centers, height: {area.height_feet:.1f}'"
            ))
        
        if best_plate:
            estimates.append(LumberEstimate(
                item=best_plate,
                quantity_needed=plates_needed,
                unit_price=best_plate.unit_price,
                total_cost=best_plate.unit_price * plates_needed,
                area_coverage=f"Top and bottom plates for {area.perimeter_feet:.1f} linear feet",
                notes="Standard construction practice"
            ))
        
        return estimates
    
    def estimate_floor_joists(self, area: AreaSpecification) -> List[LumberEstimate]:
        """Estimate floor joist lumber requirements"""
        estimates = []
        
        # Calculate joists needed
        joist_spacing_inches = self.construction_standards["joist_spacing"]
        joists_needed = math.ceil((area.width_feet * 12) / joist_spacing_inches) + 1
        
        # Calculate joist length (span)
        joist_length = area.length_feet
        
        # Find appropriate joist size based on span
        if joist_length <= 12:
            joist_size = "2X8"
        elif joist_length <= 16:
            joist_size = "2X10"
        else:
            joist_size = "2X12"
        
        # Find matching lumber items
        joist_items = self.lumber_db.get_items_by_subcategory("Dimensional Lumber")
        
        # Select best joist option
        best_joist = None
        for item in joist_items:
            if (f"{joist_size}X{int(joist_length)}" in item.dimensions and 
                item.category == "Joist"):
                if best_joist is None or item.unit_price < best_joist.unit_price:
                    best_joist = item
        
        if best_joist:
            estimates.append(LumberEstimate(
                item=best_joist,
                quantity_needed=joists_needed,
                unit_price=best_joist.unit_price,
                total_cost=best_joist.unit_price * joists_needed,
                area_coverage=f"Floor joists for {area.area_sqft:.1f} sq ft",
                notes=f"Spaced at {joist_spacing_inches}\" centers, span: {joist_length:.1f}'"
            ))
        
        # Add joist hangers
        hanger_items = self.lumber_db.get_items_by_subcategory("Hardware")
        for item in hanger_items:
            if "HU" in item.dimensions:
                hangers_needed = joists_needed
                if "25" in item.dimensions:  # 25-pack
                    packs_needed = math.ceil(hangers_needed / 25)
                    estimates.append(LumberEstimate(
                        item=item,
                        quantity_needed=packs_needed,
                        unit_price=item.unit_price,
                        total_cost=item.unit_price * packs_needed,
                        area_coverage=f"Joist hangers for {joists_needed} joists",
                        notes=f"{packs_needed} packs of 25"
                    ))
                break
        
        return estimates
    
    def estimate_roof_rafters(self, area: AreaSpecification) -> List[LumberEstimate]:
        """Estimate roof rafter lumber requirements"""
        estimates = []
        
        # Calculate rafters needed
        rafter_spacing_inches = self.construction_standards["rafter_spacing"]
        rafters_needed = math.ceil((area.width_feet * 12) / rafter_spacing_inches) + 1
        
        # Calculate rafter length (considering roof pitch)
        # Assuming 6:12 pitch for calculation
        roof_pitch = 6/12
        rafter_length = math.sqrt(area.length_feet**2 + (area.length_feet * roof_pitch)**2)
        
        # Find appropriate rafter size based on span
        if rafter_length <= 16:
            rafter_size = "2X6"
        elif rafter_length <= 24:
            rafter_size = "2X8"
        else:
            rafter_size = "2X10"
        
        # Find matching lumber items
        rafter_items = self.lumber_db.get_items_by_subcategory("Rafters")
        
        # Select best rafter option
        best_rafter = None
        for item in rafter_items:
            if (f"{rafter_size}X{int(rafter_length)}" in item.dimensions and 
                item.category == "Roof"):
                if best_rafter is None or item.unit_price < best_rafter.unit_price:
                    best_rafter = item
        
        if best_rafter:
            estimates.append(LumberEstimate(
                item=best_rafter,
                quantity_needed=rafters_needed,
                unit_price=best_rafter.unit_price,
                total_cost=best_rafter.unit_price * rafters_needed,
                area_coverage=f"Roof rafters for {area.area_sqft:.1f} sq ft",
                notes=f"Spaced at {rafter_spacing_inches}\" centers, length: {rafter_length:.1f}'"
            ))
        
        return estimates
    
    def estimate_sheathing(self, area: AreaSpecification) -> List[LumberEstimate]:
        """Estimate sheathing requirements"""
        estimates = []
        
        # Wall sheathing
        wall_area = area.perimeter_feet * area.height_feet
        wall_sheets_needed = math.ceil(wall_area / 32)  # 4x8 sheets = 32 sq ft
        
        # Find OSB sheathing
        sheathing_items = self.lumber_db.get_items_by_subcategory("Sheathing")
        for item in sheathing_items:
            if "OSB" in item.material and "4X8" in item.dimensions:
                estimates.append(LumberEstimate(
                    item=item,
                    quantity_needed=wall_sheets_needed,
                    unit_price=item.unit_price,
                    total_cost=item.unit_price * wall_sheets_needed,
                    area_coverage=f"Wall sheathing for {wall_area:.1f} sq ft",
                    notes="4x8 OSB sheets"
                ))
                break
        
        # Roof sheathing
        roof_area = area.area_sqft * 1.1  # 10% overhang
        roof_sheets_needed = math.ceil(roof_area / 32)
        
        for item in sheathing_items:
            if "OSB" in item.material and "4X8" in item.dimensions:
                estimates.append(LumberEstimate(
                    item=item,
                    quantity_needed=roof_sheets_needed,
                    unit_price=item.unit_price,
                    total_cost=item.unit_price * roof_sheets_needed,
                    area_coverage=f"Roof sheathing for {roof_area:.1f} sq ft",
                    notes="4x8 OSB sheets with 10% overhang"
                ))
                break
        
        return estimates
    
    def estimate_headers_and_beams(self, area: AreaSpecification) -> List[LumberEstimate]:
        """Estimate headers and beams for openings"""
        estimates = []
        
        # Estimate door and window headers
        # Assume 1 door and 2 windows per 400 sq ft
        openings_per_400sqft = 3
        openings_needed = math.ceil(area.area_sqft / 400) * openings_per_400sqft
        
        # Find LVL headers
        lvl_items = self.lumber_db.get_items_by_subcategory("LVL Beams")
        for item in lvl_items:
            if "LVL" in item.material and "11-7/8" in item.dimensions:
                # Use 12' LVL for most openings
                if "12" in item.dimensions:
                    estimates.append(LumberEstimate(
                        item=item,
                        quantity_needed=openings_needed,
                        unit_price=item.unit_price,
                        total_cost=item.unit_price * openings_needed,
                        area_coverage=f"Headers for {openings_needed} openings",
                        notes="LVL headers for doors and windows"
                    ))
                    break
        
        return estimates
    
    def estimate_complete_project(self, length: float, width: float, height: float = 8.0, 
                                project_name: str = "Lumber Project") -> ProjectEstimate:
        """Estimate complete lumber requirements for a project"""
        
        # Calculate area specifications
        area = self.calculate_area_requirements(length, width, height)
        
        # Get estimates for each category
        wall_estimates = self.estimate_wall_framing(area)
        floor_estimates = self.estimate_floor_joists(area)
        roof_estimates = self.estimate_roof_rafters(area)
        sheathing_estimates = self.estimate_sheathing(area)
        header_estimates = self.estimate_headers_and_beams(area)
        
        # Combine all estimates
        all_estimates = wall_estimates + floor_estimates + roof_estimates + sheathing_estimates + header_estimates
        
        # Calculate totals
        total_cost = sum(est.total_cost for est in all_estimates)
        
        # Apply waste factor
        total_cost_with_waste = total_cost * self.construction_standards["waste_factor"]
        
        # Organize by category
        estimates_by_category = {
            "Walls": [est for est in all_estimates if est.item.category == "Walls"],
            "Joist": [est for est in all_estimates if est.item.category == "Joist"],
            "Roof": [est for est in all_estimates if est.item.category == "Roof"],
            "Cornice and Decking": [est for est in all_estimates if est.item.category == "Cornice and Decking"],
            "Post & Beams": [est for est in all_estimates if est.item.category == "Post & Beams"]
        }
        
        # Create summary
        summary = {
            "total_lumber_items": len(all_estimates),
            "total_cost_without_waste": total_cost,
            "waste_factor": f"{((self.construction_standards['waste_factor'] - 1) * 100):.0f}%",
            "total_cost_with_waste": total_cost_with_waste,
            "cost_per_sqft": total_cost_with_waste / area.area_sqft if area.area_sqft > 0 else 0,
            "dimensions": f"{length:.1f}' x {width:.1f}' x {height:.1f}'",
            "area_sqft": area.area_sqft,
            "perimeter_feet": area.perimeter_feet
        }
        
        return ProjectEstimate(
            project_name=project_name,
            total_area_sqft=area.area_sqft,
            total_cost=total_cost_with_waste,
            estimates_by_category=estimates_by_category,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
    
    def export_estimate_to_json(self, estimate: ProjectEstimate, filepath: str = None) -> str:
        """Export estimate to JSON file"""
        if not filepath:
            filepath = f"lumber_estimate_{estimate.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to serializable format
        data = {
            "project_name": estimate.project_name,
            "total_area_sqft": estimate.total_area_sqft,
            "total_cost": estimate.total_cost,
            "timestamp": estimate.timestamp,
            "summary": estimate.summary,
            "estimates_by_category": {}
        }
        
        for category, estimates in estimate.estimates_by_category.items():
            data["estimates_by_category"][category] = []
            for est in estimates:
                data["estimates_by_category"][category].append({
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
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def get_lumber_categories(self) -> List[str]:
        """Get all available lumber categories"""
        return self.lumber_db.get_categories()
    
    def get_lumber_subcategories(self) -> List[str]:
        """Get all available lumber subcategories"""
        return self.lumber_db.get_subcategories()
    
    def search_lumber_items(self, query: str) -> List[LumberItem]:
        """Search lumber items"""
        return self.lumber_db.search_items(query)

# Global instance
lumber_estimation_engine = LumberEstimationEngine()

