#!/usr/bin/env python3
"""
Contractor Data Input System
Handles importing contractor data from various sources (CSV, JSON, Excel, manual input)
"""

import csv
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..database.enhanced_models import EnhancedDatabaseManager, ContractorProfileManager, MaterialItemManager

class ContractorDataImporter:
    def __init__(self, db_manager: EnhancedDatabaseManager = None):
        """Initialize with database manager"""
        self.db = db_manager or EnhancedDatabaseManager()
        self.contractor_manager = ContractorProfileManager(self.db)
        self.material_manager = MaterialItemManager(self.db)
    
    def import_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """Import contractor data from CSV file
        
        Expected CSV format:
        contractor_name,contact_number,address,email,specialty,item_name,display_name,category,unit,price,description
        """
        results = {
            "contractors_added": 0,
            "materials_added": 0,
            "errors": [],
            "summary": {}
        }
        
        try:
            df = pd.read_csv(csv_path)
            required_columns = ['contractor_name', 'item_name', 'price']
            
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"Missing required columns: {missing}")
            
            # Group by contractor
            contractor_groups = df.groupby('contractor_name')
            
            for contractor_name, group in contractor_groups:
                try:
                    # Get contractor info from first row
                    first_row = group.iloc[0]
                    
                    # Create contractor profile
                    contractor_data = {
                        'name': contractor_name,
                        'address': first_row.get('address', ''),
                        'contact_number': first_row.get('contact_number', ''),
                        'email': first_row.get('email', ''),
                        'specialty': first_row.get('specialty', '')
                    }
                    contractor_id = self.contractor_manager.create_contractor_profile(contractor_data)
                    results["contractors_added"] += 1
                    
                    # Add materials
                    materials_for_contractor = 0
                    for _, row in group.iterrows():
                        try:
                            self.material_manager.add_material(
                                contractor_id=contractor_id,
                                item_name=row['item_name'],
                                price=float(row['price']),
                                display_name=row.get('display_name', ''),
                                category=row.get('category', ''),
                                unit=row.get('unit', 'each'),
                                description=row.get('description', ''),
                                specifications=row.get('specifications', '')
                            )
                            materials_for_contractor += 1
                            results["materials_added"] += 1
                        except Exception as e:
                            results["errors"].append(f"Error adding material {row['item_name']}: {str(e)}")
                    
                    results["summary"][contractor_name] = materials_for_contractor
                    
                except Exception as e:
                    results["errors"].append(f"Error processing contractor {contractor_name}: {str(e)}")
            
        except Exception as e:
            results["errors"].append(f"Error reading CSV file: {str(e)}")
        
        return results
    
    def import_from_json(self, json_path: str) -> Dict[str, Any]:
        """Import contractor data from JSON file
        
        Expected JSON format:
        {
            "contractors": [
                {
                    "name": "ABC Supply",
                    "address": "123 Main St",
                    "contact_number": "(555) 123-4567",
                    "email": "contact@abc.com",
                    "specialty": "lumber",
                    "materials": [
                        {
                            "item_name": "2x4_stud_8ft",
                            "display_name": "2x4 Stud 8ft",
                            "category": "lumber",
                            "unit": "each",
                            "price": 3.25,
                            "description": "Standard 2x4 stud"
                        }
                    ]
                }
            ]
        }
        """
        results = {
            "contractors_added": 0,
            "materials_added": 0,
            "errors": [],
            "summary": {}
        }
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for contractor_data in data.get('contractors', []):
                try:
                    # Add contractor
                    contractor_id = self.contractor_manager.add_contractor(
                        name=contractor_data['name'],
                        address=contractor_data.get('address', ''),
                        contact_number=contractor_data.get('contact_number', ''),
                        email=contractor_data.get('email', ''),
                        specialty=contractor_data.get('specialty', '')
                    )
                    results["contractors_added"] += 1
                    
                    # Add materials
                    materials_added = 0
                    for material in contractor_data.get('materials', []):
                        try:
                            self.material_manager.add_material(
                                contractor_id=contractor_id,
                                item_name=material['item_name'],
                                price=float(material['price']),
                                display_name=material.get('display_name', ''),
                                category=material.get('category', ''),
                                unit=material.get('unit', 'each'),
                                description=material.get('description', ''),
                                specifications=material.get('specifications', '')
                            )
                            materials_added += 1
                            results["materials_added"] += 1
                        except Exception as e:
                            results["errors"].append(f"Error adding material {material.get('item_name', 'unknown')}: {str(e)}")
                    
                    results["summary"][contractor_data['name']] = materials_added
                    
                except Exception as e:
                    results["errors"].append(f"Error processing contractor {contractor_data.get('name', 'unknown')}: {str(e)}")
        
        except Exception as e:
            results["errors"].append(f"Error reading JSON file: {str(e)}")
        
        return results
    
    def import_from_excel(self, excel_path: str, sheet_name: str = None) -> Dict[str, Any]:
        """Import contractor data from Excel file"""
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_path)
            
            # Save as temporary CSV and import
            temp_csv = Path(excel_path).with_suffix('.csv')
            df.to_csv(temp_csv, index=False)
            
            results = self.import_from_csv(str(temp_csv))
            
            # Clean up temp file
            temp_csv.unlink()
            
            return results
            
        except Exception as e:
            return {
                "contractors_added": 0,
                "materials_added": 0,
                "errors": [f"Error importing from Excel: {str(e)}"],
                "summary": {}
            }
    
    def add_contractor_manual(self, contractor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a contractor manually through API"""
        results = {
            "contractor_id": None,
            "materials_added": 0,
            "errors": []
        }
        
        try:
            # Add contractor
            contractor_id = self.contractor_manager.add_contractor(
                name=contractor_data['name'],
                address=contractor_data.get('address', ''),
                contact_number=contractor_data.get('contact_number', ''),
                email=contractor_data.get('email', ''),
                specialty=contractor_data.get('specialty', '')
            )
            results["contractor_id"] = contractor_id
            
            # Add materials if provided
            for material in contractor_data.get('materials', []):
                try:
                    self.material_manager.add_material(
                        contractor_id=contractor_id,
                        item_name=material['item_name'],
                        price=float(material['price']),
                        display_name=material.get('display_name', ''),
                        category=material.get('category', ''),
                        unit=material.get('unit', 'each'),
                        description=material.get('description', ''),
                        specifications=material.get('specifications', '')
                    )
                    results["materials_added"] += 1
                except Exception as e:
                    results["errors"].append(f"Error adding material {material.get('item_name', 'unknown')}: {str(e)}")
            
        except Exception as e:
            results["errors"].append(f"Error adding contractor: {str(e)}")
        
        return results
    
    def update_contractor_pricing(self, contractor_id: int, pricing_updates: List[Dict]) -> Dict[str, Any]:
        """Update pricing for existing contractor materials"""
        results = {
            "updated": 0,
            "errors": []
        }
        
        try:
            contractor_materials = self.material_manager.get_contractor_materials(contractor_id)
            material_dict = {mat['item_name']: mat['id'] for mat in contractor_materials}
            
            for update in pricing_updates:
                item_name = update['item_name']
                new_price = float(update['price'])
                
                if item_name in material_dict:
                    material_id = material_dict[item_name]
                    if self.material_manager.update_material_price(material_id, new_price):
                        results["updated"] += 1
                    else:
                        results["errors"].append(f"Failed to update price for {item_name}")
                else:
                    results["errors"].append(f"Material {item_name} not found for this contractor")
        
        except Exception as e:
            results["errors"].append(f"Error updating pricing: {str(e)}")
        
        return results
    
    def export_contractor_data(self, contractor_id: int = None, format: str = "csv") -> str:
        """Export contractor data to file"""
        try:
            if contractor_id:
                # Export specific contractor
                contractor = self.contractor_manager.get_contractor(contractor_id)
                materials = self.material_manager.get_contractor_materials(contractor_id)
                filename = f"contractor_{contractor['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                # Export all contractors
                contractors = self.contractor_manager.get_all_contractors()
                materials = []
                for contractor in contractors:
                    materials.extend(self.material_manager.get_contractor_materials(contractor['id']))
                filename = f"all_contractors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create data for export
            export_data = []
            for material in materials:
                export_data.append({
                    'contractor_name': material['contractor_name'],
                    'contact_number': material.get('contact_number', ''),
                    'item_name': material['item_name'],
                    'display_name': material['display_name'],
                    'category': material['category'],
                    'unit': material['unit'],
                    'price': material['price'],
                    'description': material['description'],
                    'specifications': material['specifications']
                })
            
            if format.lower() == 'csv':
                filepath = f"data/exports/{filename}.csv"
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(export_data)
                df.to_csv(filepath, index=False)
            elif format.lower() == 'json':
                filepath = f"data/exports/{filename}.json"
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w') as f:
                    json.dump({"contractors": export_data}, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting data: {str(e)}")

def migrate_existing_data():
    """Migrate existing CSV data to database"""
    db = DatabaseManager()
    importer = ContractorDataImporter(db)
    
    print("🔄 Migrating existing contractor data to database...")
    
    # Check for existing CSV files
    csv_files = [
        "contractor_items_detailed.csv",
        "electrical_items_pricing.csv"
    ]
    
    total_results = {
        "contractors_added": 0,
        "materials_added": 0,
        "errors": [],
        "files_processed": []
    }
    
    for csv_file in csv_files:
        if Path(csv_file).exists():
            print(f"📋 Processing {csv_file}...")
            results = importer.import_from_csv(csv_file)
            total_results["contractors_added"] += results["contractors_added"]
            total_results["materials_added"] += results["materials_added"]
            total_results["errors"].extend(results["errors"])
            total_results["files_processed"].append(csv_file)
            
            print(f"✅ Added {results['contractors_added']} contractors and {results['materials_added']} materials from {csv_file}")
            if results["errors"]:
                print(f"⚠️ {len(results['errors'])} errors occurred")
    
    print(f"\n📊 Migration Summary:")
    print(f"   • Total contractors added: {total_results['contractors_added']}")
    print(f"   • Total materials added: {total_results['materials_added']}")
    print(f"   • Files processed: {len(total_results['files_processed'])}")
    print(f"   • Total errors: {len(total_results['errors'])}")
    
    return total_results

if __name__ == "__main__":
    # Run migration
    migrate_existing_data()