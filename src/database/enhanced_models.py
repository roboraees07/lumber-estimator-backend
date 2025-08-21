#!/usr/bin/env python3
"""
Enhanced Database Models for Contractor Profiling
Advanced contractor and item management with detailed profiling
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

class EnhancedDatabaseManager:
    def __init__(self, db_path: str = "data/lumber_estimator.db"):
        """Initialize enhanced database with contractor profiling"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_enhanced_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_enhanced_database(self):
        """Create enhanced database tables for contractor profiling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enhanced contractors table with profiling
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contractors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    business_license TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    contact_number TEXT,
                    email TEXT,
                    website TEXT,
                    specialty TEXT,
                    business_type TEXT, -- supplier, contractor, manufacturer
                    service_area TEXT, -- local, regional, national
                    payment_terms TEXT, -- net30, net15, COD, etc.
                    credit_rating TEXT, -- A, B, C, D
                    delivery_options TEXT, -- pickup, delivery, both
                    minimum_order REAL DEFAULT 0,
                    discount_policy TEXT,
                    warranty_policy TEXT,
                    certifications TEXT, -- JSON array of certifications
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    rating REAL DEFAULT 0, -- 0-5 star rating
                    total_orders INTEGER DEFAULT 0,
                    total_value REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Enhanced materials table with detailed specs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contractor_id INTEGER,
                    item_name TEXT NOT NULL,
                    display_name TEXT,
                    sku TEXT, -- contractor's SKU
                    category TEXT,
                    subcategory TEXT,
                    unit TEXT DEFAULT 'each',
                    price REAL NOT NULL,
                    cost REAL, -- contractor's cost (if available)
                    currency TEXT DEFAULT 'USD',
                    price_per TEXT, -- per unit, per sq ft, etc.
                    dimensions TEXT, -- length x width x height
                    weight REAL,
                    weight_unit TEXT DEFAULT 'lbs',
                    material_type TEXT, -- wood, steel, concrete, etc.
                    grade_quality TEXT, -- A, B, construction grade, etc.
                    brand TEXT,
                    manufacturer TEXT,
                    model_number TEXT,
                    color TEXT,
                    finish TEXT,
                    description TEXT,
                    specifications TEXT, -- detailed specs JSON
                    installation_notes TEXT,
                    safety_info TEXT,
                    compliance_codes TEXT, -- building codes, standards
                    lead_time_days INTEGER DEFAULT 0,
                    stock_quantity INTEGER,
                    minimum_order_qty INTEGER DEFAULT 1,
                    bulk_pricing TEXT, -- JSON for quantity breaks
                    seasonal_availability BOOLEAN DEFAULT 1,
                    is_special_order BOOLEAN DEFAULT 0,
                    discontinued BOOLEAN DEFAULT 0,
                    replacement_item_id INTEGER, -- if discontinued
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contractor_id) REFERENCES contractors (id),
                    FOREIGN KEY (replacement_item_id) REFERENCES materials (id)
                )
            ''')
            
            # Material categories master table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS material_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    parent_category_id INTEGER,
                    description TEXT,
                    typical_units TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_category_id) REFERENCES material_categories (id)
                )
            ''')
            
            # Contractor reviews and ratings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contractor_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contractor_id INTEGER,
                    project_id INTEGER,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT,
                    delivery_rating INTEGER CHECK (delivery_rating >= 1 AND delivery_rating <= 5),
                    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
                    price_rating INTEGER CHECK (price_rating >= 1 AND price_rating <= 5),
                    service_rating INTEGER CHECK (service_rating >= 1 AND service_rating <= 5),
                    reviewer_name TEXT,
                    order_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contractor_id) REFERENCES contractors (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Price history for tracking changes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_id INTEGER,
                    old_price REAL,
                    new_price REAL,
                    change_reason TEXT,
                    effective_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (material_id) REFERENCES materials (id)
                )
            ''')
            
            # Contractor capabilities (what they specialize in)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contractor_capabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contractor_id INTEGER,
                    capability TEXT, -- lumber, steel, electrical, etc.
                    proficiency_level TEXT, -- basic, intermediate, expert
                    years_experience INTEGER,
                    certifications TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contractor_id) REFERENCES contractors (id)
                )
            ''')
            
            # Enhanced projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT, -- residential, commercial, industrial
                    location TEXT,
                    pdf_path TEXT,
                    total_cost REAL,
                    estimated_duration_days INTEGER,
                    start_date DATE,
                    end_date DATE,
                    status TEXT DEFAULT 'planning', -- planning, active, completed, cancelled
                    client_name TEXT,
                    client_contact TEXT,
                    analysis_data TEXT, -- JSON data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Material orders/estimates
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS material_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    contractor_id INTEGER,
                    material_id INTEGER,
                    quantity REAL,
                    unit_price REAL,
                    total_price REAL,
                    order_date DATE,
                    expected_delivery DATE,
                    actual_delivery DATE,
                    status TEXT DEFAULT 'estimated', -- estimated, ordered, delivered, cancelled
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (contractor_id) REFERENCES contractors (id),
                    FOREIGN KEY (material_id) REFERENCES materials (id)
                )
            ''')
            
            # Initialize material categories
            self._initialize_categories(cursor)
            
            conn.commit()
    
    def _initialize_categories(self, cursor):
        """Initialize standard material categories"""
        categories = [
            ('Lumber', None, 'Wood building materials'),
            ('Structural Steel', None, 'Steel beams, columns, and framing'),
            ('Concrete', None, 'Concrete products and reinforcement'),
            ('Electrical', None, 'Electrical components and systems'),
            ('Plumbing', None, 'Plumbing materials and fixtures'),
            ('HVAC', None, 'Heating, ventilation, and air conditioning'),
            ('Fasteners', None, 'Bolts, screws, nails, and hardware'),
            ('Doors & Windows', None, 'Doors, windows, and related hardware'),
            ('Roofing', None, 'Roofing materials and accessories'),
            ('Insulation', None, 'Insulation materials'),
            ('Drywall', None, 'Drywall and finishing materials'),
            ('Flooring', None, 'Flooring materials'),
            ('Paint & Finishes', None, 'Paint, stain, and finish materials'),
            # Subcategories for Lumber
            ('Dimensional Lumber', 1, '2x4, 2x6, 2x8, etc.'),
            ('Engineered Lumber', 1, 'LVL, I-joists, etc.'),
            ('Plywood & OSB', 1, 'Sheet goods'),
            ('Specialty Lumber', 1, 'Treated, cedar, etc.'),
            # Subcategories for Electrical
            ('Wire & Cable', 4, 'Electrical wire and cables'),
            ('Outlets & Switches', 4, 'Electrical outlets and switches'),
            ('Lighting', 4, 'Light fixtures and bulbs'),
            ('Panels & Breakers', 4, 'Electrical panels and circuit breakers'),
        ]
        
        cursor.execute('SELECT COUNT(*) FROM material_categories')
        if cursor.fetchone()[0] == 0:  # Only insert if table is empty
            cursor.executemany('''
                INSERT INTO material_categories (name, parent_category_id, description)
                VALUES (?, ?, ?)
            ''', categories)

class ContractorProfileManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def create_contractor_profile(self, contractor_data: Dict[str, Any]) -> int:
        """Create a detailed contractor profile"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert contractor
            cursor.execute('''
                INSERT INTO contractors (
                    name, business_license, address, city, state, zip_code,
                    contact_number, email, website, specialty, business_type,
                    service_area, payment_terms, credit_rating, delivery_options,
                    minimum_order, discount_policy, warranty_policy, certifications, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contractor_data['name'],
                contractor_data.get('business_license'),
                contractor_data.get('address'),
                contractor_data.get('city'),
                contractor_data.get('state'),
                contractor_data.get('zip_code'),
                contractor_data.get('contact_number'),
                contractor_data.get('email'),
                contractor_data.get('website'),
                contractor_data.get('specialty'),
                contractor_data.get('business_type', 'supplier'),
                contractor_data.get('service_area', 'local'),
                contractor_data.get('payment_terms', 'net30'),
                contractor_data.get('credit_rating', 'A'),
                contractor_data.get('delivery_options', 'both'),
                contractor_data.get('minimum_order', 0),
                contractor_data.get('discount_policy'),
                contractor_data.get('warranty_policy'),
                json.dumps(contractor_data.get('certifications', [])),
                contractor_data.get('notes')
            ))
            
            contractor_id = cursor.lastrowid
            
            # Add capabilities
            for capability in contractor_data.get('capabilities', []):
                cursor.execute('''
                    INSERT INTO contractor_capabilities 
                    (contractor_id, capability, proficiency_level, years_experience, certifications)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    contractor_id,
                    capability['name'],
                    capability.get('proficiency_level', 'intermediate'),
                    capability.get('years_experience', 0),
                    capability.get('certifications', '')
                ))
            
            conn.commit()
            return contractor_id
    
    def get_contractor_profile(self, contractor_id: int) -> Optional[Dict]:
        """Get complete contractor profile with capabilities"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get contractor details
            cursor.execute('SELECT * FROM contractors WHERE id = ?', (contractor_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            contractor = dict(zip(columns, row))
            
            # Parse JSON fields
            if contractor['certifications']:
                contractor['certifications'] = json.loads(contractor['certifications'])
            
            # Get capabilities
            cursor.execute('''
                SELECT capability, proficiency_level, years_experience, certifications
                FROM contractor_capabilities WHERE contractor_id = ?
            ''', (contractor_id,))
            
            capabilities = []
            for cap_row in cursor.fetchall():
                capabilities.append({
                    'name': cap_row[0],
                    'proficiency_level': cap_row[1],
                    'years_experience': cap_row[2],
                    'certifications': cap_row[3]
                })
            
            contractor['capabilities'] = capabilities
            
            # Get statistics
            # Simplified review stats (no review table yet)
            contractor['review_count'] = 0
            contractor['average_rating'] = contractor.get('rating', 0)
            
            return contractor
    
    def search_contractors(self, filters: Dict[str, Any]) -> List[Dict]:
        """Search contractors with advanced filtering"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT c.*, 
                       COUNT(DISTINCT m.id) as material_count,
                       0 as review_count,
                       COALESCE(c.rating, 0) as avg_rating
                FROM contractors c
                LEFT JOIN materials m ON c.id = m.contractor_id
                WHERE c.is_active = 1
            '''
            params = []
            
            # Add filters
            if filters.get('specialty'):
                query += ' AND c.specialty LIKE ?'
                params.append(f"%{filters['specialty']}%")
            
            if filters.get('business_type'):
                query += ' AND c.business_type = ?'
                params.append(filters['business_type'])
            
            if filters.get('service_area'):
                query += ' AND c.service_area = ?'
                params.append(filters['service_area'])
            
            if filters.get('city'):
                query += ' AND c.city LIKE ?'
                params.append(f"%{filters['city']}%")
            
            if filters.get('state'):
                query += ' AND c.state = ?'
                params.append(filters['state'])
            
            if filters.get('min_rating'):
                query += ' AND c.rating >= ?'
                params.append(filters['min_rating'])
            
            query += ' GROUP BY c.id ORDER BY avg_rating DESC, c.name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
    
    def update_contractor_profile(self, contractor_id: int, updates: Dict[str, Any]) -> bool:
        """Update contractor profile"""
        if not updates:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle JSON fields
            if 'certifications' in updates and isinstance(updates['certifications'], list):
                updates['certifications'] = json.dumps(updates['certifications'])
            
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [contractor_id]
            
            cursor.execute(f'''
                UPDATE contractors 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            conn.commit()
            return cursor.rowcount > 0

class MaterialItemManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def add_material_item(self, contractor_id: int, material_data: Dict[str, Any]) -> int:
        """Add a detailed material item"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle JSON fields
            specifications = material_data.get('specifications', {})
            if isinstance(specifications, dict):
                specifications = json.dumps(specifications)
            
            bulk_pricing = material_data.get('bulk_pricing', [])
            if isinstance(bulk_pricing, list):
                bulk_pricing = json.dumps(bulk_pricing)
            
            cursor.execute('''
                INSERT INTO materials (
                    contractor_id, item_name, display_name, sku, category, subcategory,
                    unit, price, cost, currency, price_per, dimensions, weight, weight_unit,
                    material_type, grade_quality, brand, manufacturer, model_number,
                    color, finish, description, specifications, installation_notes,
                    safety_info, compliance_codes, lead_time_days, stock_quantity,
                    minimum_order_qty, bulk_pricing, seasonal_availability, is_special_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contractor_id,
                material_data['item_name'],
                material_data.get('display_name'),
                material_data.get('sku'),
                material_data.get('category'),
                material_data.get('subcategory'),
                material_data.get('unit', 'each'),
                material_data['price'],
                material_data.get('cost'),
                material_data.get('currency', 'USD'),
                material_data.get('price_per'),
                material_data.get('dimensions'),
                material_data.get('weight'),
                material_data.get('weight_unit', 'lbs'),
                material_data.get('material_type'),
                material_data.get('grade_quality'),
                material_data.get('brand'),
                material_data.get('manufacturer'),
                material_data.get('model_number'),
                material_data.get('color'),
                material_data.get('finish'),
                material_data.get('description'),
                specifications,
                material_data.get('installation_notes'),
                material_data.get('safety_info'),
                material_data.get('compliance_codes'),
                material_data.get('lead_time_days', 0),
                material_data.get('stock_quantity'),
                material_data.get('minimum_order_qty', 1),
                bulk_pricing,
                material_data.get('seasonal_availability', True),
                material_data.get('is_special_order', False)
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_material_categories(self) -> List[Dict]:
        """Get all material categories"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, parent_category_id, description, typical_units
                FROM material_categories
                ORDER BY parent_category_id NULLS FIRST, name
            ''')
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def bulk_import_materials(self, contractor_id: int, materials: List[Dict]) -> Dict[str, Any]:
        """Bulk import materials for a contractor"""
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": []
        }
        
        for material in materials:
            try:
                self.add_material_item(contractor_id, material)
                results["imported"] += 1
            except Exception as e:
                results["errors"].append(f"Error importing {material.get('item_name', 'unknown')}: {str(e)}")
                results["skipped"] += 1
        
        return results
    
    def update_material_pricing(self, material_id: int, new_price: float, reason: str = None) -> bool:
        """Update material price with history tracking"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current price
            cursor.execute('SELECT price FROM materials WHERE id = ?', (material_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_price = result[0]
            
            # Record price history
            cursor.execute('''
                INSERT INTO price_history (material_id, old_price, new_price, change_reason, effective_date)
                VALUES (?, ?, ?, ?, DATE('now'))
            ''', (material_id, old_price, new_price, reason))
            
            # Update material price
            cursor.execute('''
                UPDATE materials 
                SET price = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_price, material_id))
            
            conn.commit()
            return True
    
    def get_contractor_materials(self, contractor_id: int) -> List[Dict]:
        """Get all materials for a specific contractor"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, item_name, display_name, sku, category, subcategory,
                       unit, price, cost, currency, material_type, grade_quality,
                       brand, manufacturer, stock_quantity, created_at
                FROM materials 
                WHERE contractor_id = ? AND discontinued = 0
                ORDER BY category, item_name
            ''', (contractor_id,))
            
            rows = cursor.fetchall()
            columns = ['id', 'item_name', 'display_name', 'sku', 'category', 'subcategory',
                      'unit', 'price', 'cost', 'currency', 'material_type', 'grade_quality',
                      'brand', 'manufacturer', 'stock_quantity', 'created_at']
            
            return [dict(zip(columns, row)) for row in rows]

class ProjectManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def create_project(self, name: str, description: str = None, pdf_path: str = None) -> int:
        """Create a new project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (name, description, pdf_path)
                VALUES (?, ?, ?)
            ''', (name, description, pdf_path))
            conn.commit()
            return cursor.lastrowid
    
    def save_project_analysis(self, project_id: int, analysis_data: Dict, total_cost: float = None):
        """Save analysis results for a project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects 
                SET analysis_data = ?, total_cost = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(analysis_data), total_cost, project_id))
            conn.commit()
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                project = dict(zip(columns, row))
                if project['analysis_data']:
                    project['analysis_data'] = json.loads(project['analysis_data'])
                return project
            return None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            projects = []
            for row in rows:
                project = dict(zip(columns, row))
                if project['analysis_data']:
                    try:
                        project['analysis_data'] = json.loads(project['analysis_data'])
                    except:
                        project['analysis_data'] = {}
                projects.append(project)
            return projects


