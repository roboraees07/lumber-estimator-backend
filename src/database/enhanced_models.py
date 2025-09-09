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
        """Get database connection with proper settings to prevent locking"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")  # Use WAL mode to prevent locking
        conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
        conn.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
        return conn
    
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
                    user_id INTEGER NOT NULL, -- User who created/owns the project
                    analysis_data TEXT, -- JSON data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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
            
            # Manual items table for storing manually added items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manual_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT DEFAULT 'each',
                    sku TEXT,
                    notes TEXT,
                    category TEXT,
                    dimensions TEXT,
                    estimated_unit_price REAL,
                    estimated_cost REAL,
                    database_match_found BOOLEAN DEFAULT 0,
                    contractor_name TEXT,
                    added_by TEXT,
                    added_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            ''')
            
            # Estimate history table for storing submitted estimates
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estimate_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estimate_data TEXT NOT NULL, -- JSON data of the complete estimate
                    total_cost REAL NOT NULL,
                    total_items_count INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, submitted, approved, rejected, completed
                    notes TEXT,
                    client_notes TEXT,
                    approval_date TIMESTAMP,
                    approved_by TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            ''')
            
            # Quotations table for contractor quotations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    quotation_name TEXT,
                    client_name TEXT,
                    client_email TEXT,
                    client_phone TEXT,
                    project_address TEXT,
                    project_description TEXT,
                    total_cost REAL DEFAULT 0,
                    status TEXT DEFAULT 'draft', -- draft, sent, approved, rejected, completed
                    valid_until DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Quotation items table for items within quotations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotation_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quotation_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    sku TEXT,
                    unit TEXT NOT NULL,
                    unit_of_measure TEXT NOT NULL,
                    cost REAL NOT NULL,
                    quantity REAL DEFAULT 1,
                    total_cost REAL,
                    description TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (quotation_id) REFERENCES quotations (id) ON DELETE CASCADE
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

class ManualItemsManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def add_manual_item(self, project_id: int, item_data: Dict[str, Any]) -> int:
        """Add a manual item to a project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO manual_items (
                    project_id, item_name, quantity, unit, sku, notes, category,
                    dimensions, estimated_unit_price, estimated_cost, database_match_found,
                    contractor_name, added_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                item_data['item_name'],
                item_data['quantity'],
                item_data.get('unit', 'each'),
                item_data.get('sku'),
                item_data.get('notes'),
                item_data.get('category'),
                item_data.get('dimensions'),
                item_data.get('estimated_unit_price', 0.0),
                item_data.get('estimated_cost', 0.0),
                item_data.get('database_match_found', False),
                item_data.get('contractor_name'),
                item_data.get('added_by')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_manual_items_for_project(self, project_id: int) -> List[Dict]:
        """Get all manual items for a specific project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM manual_items 
                WHERE project_id = ? 
                ORDER BY added_timestamp DESC
            ''', (project_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_project_manual_items_summary(self, project_id: int) -> Dict[str, Any]:
        """Get summary of manual items for a project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_items,
                    SUM(estimated_cost) as total_cost,
                    SUM(CASE WHEN database_match_found = 1 THEN 1 ELSE 0 END) as matched_items,
                    SUM(CASE WHEN database_match_found = 0 THEN 1 ELSE 0 END) as unmatched_items
                FROM manual_items 
                WHERE project_id = ?
            ''', (project_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_manual_items': row[0],
                    'total_manual_cost': row[1] or 0.0,
                    'matched_items': row[2] or 0,
                    'unmatched_items': row[3] or 0
                }
            return {
                'total_manual_items': 0,
                'total_manual_cost': 0.0,
                'matched_items': 0,
                'unmatched_items': 0
            }
    
    def update_manual_item(self, item_id: int, updates: Dict[str, Any]) -> bool:
        """Update a manual item"""
        if not updates:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [item_id]
            
            cursor.execute(f'''
                UPDATE manual_items 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_manual_item(self, item_id: int) -> bool:
        """Delete a manual item"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM manual_items WHERE id = ?', (item_id,))
            conn.commit()
            return cursor.rowcount > 0

class EstimateHistoryManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def submit_estimate(self, project_id: int, project_name: str, submitted_by: str, estimate_data: Dict[str, Any], total_cost: float, total_items_count: int, notes: str = None, client_notes: str = None) -> int:
        """Submit an estimate and store it in history"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO estimate_history (
                    project_id, project_name, submitted_by, estimate_data, 
                    total_cost, total_items_count, notes, client_notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id, project_name, submitted_by, json.dumps(estimate_data),
                total_cost, total_items_count, notes, client_notes, 'submitted'
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_estimate_history(self, project_id: int = None) -> List[Dict]:
        """Get estimate history, optionally filtered by project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if project_id:
                cursor.execute('''
                    SELECT * FROM estimate_history 
                    WHERE project_id = ? 
                    ORDER BY submitted_at DESC
                ''', (project_id,))
            else:
                cursor.execute('''
                    SELECT * FROM estimate_history 
                    ORDER BY submitted_at DESC
                ''')
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            estimates = []
            
            for row in rows:
                estimate = dict(zip(columns, row))
                # Parse JSON data
                if estimate['estimate_data']:
                    estimate['estimate_data'] = json.loads(estimate['estimate_data'])
                estimates.append(estimate)
            
            return estimates
    
    def update_estimate_status(self, estimate_id: int, status: str, approved_by: str = None, notes: str = None) -> bool:
        """Update estimate status (approve, reject, complete)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if status in ['approved', 'rejected', 'completed']:
                cursor.execute('''
                    UPDATE estimate_history 
                    SET status = ?, approval_date = CURRENT_TIMESTAMP, 
                        approved_by = ?, notes = ?
                    WHERE id = ?
                ''', (status, approved_by, notes, estimate_id))
            else:
                cursor.execute('''
                    UPDATE estimate_history 
                    SET status = ?, notes = ?
                    WHERE id = ?
                ''', (status, notes, estimate_id))
            
            conn.commit()
            return cursor.rowcount > 0


class ProjectManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def create_project(self, name: str, description: str = None, pdf_path: str = None, user_id: int = None) -> int:
        """Create a new project with pending status for estimates"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(projects)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            if 'user_id' not in column_names:
                # If user_id column doesn't exist, create project without it for now
                # This is a temporary fix until the database is migrated
                print("⚠️ Warning: user_id column not found in projects table. Creating project without user_id.")
                cursor.execute('''
                    INSERT INTO projects (name, description, pdf_path, status)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, pdf_path, 'pending'))
            else:
                if user_id is None:
                    raise ValueError("user_id is required to create a project")
                
                cursor.execute('''
                    INSERT INTO projects (name, description, pdf_path, user_id, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, pdf_path, user_id, 'pending'))
            
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
    
    def get_project(self, project_id: int, include_manual_items: bool = True) -> Optional[Dict]:
        """Get project by ID with optional manual items"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                project = dict(zip(columns, row))
                if project['analysis_data']:
                    project['analysis_data'] = json.loads(project['analysis_data'])
                
                # Include manual items if requested
                if include_manual_items:
                    from .enhanced_models import ManualItemsManager
                    manual_manager = ManualItemsManager(self.db)
                    project['manual_items'] = manual_manager.get_manual_items_for_project(project_id)
                    project['manual_items_summary'] = manual_manager.get_project_manual_items_summary(project_id)
                    
                    # Calculate combined totals
                    pdf_total = project.get('total_cost', 0.0) or 0.0
                    manual_total = project.get('manual_items_summary', {}).get('total_manual_cost', 0.0)
                    project['combined_total_cost'] = pdf_total + manual_total
                    project['total_items_count'] = (
                        len(project.get('analysis_data', {}).get('detailed_items', [])) +
                        project.get('manual_items_summary', {}).get('total_manual_items', 0)
                    )
                
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
    
    def get_projects_by_user(self, user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get projects for a specific user with optional status filter"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(projects)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Build query with optional status filter
            if 'user_id' not in column_names:
                # If user_id column doesn't exist, return all projects for now
                # This is a temporary fix until the database is migrated
                print("⚠️ Warning: user_id column not found in projects table. Returning all projects.")
                if status:
                    cursor.execute('SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC', (status,))
                else:
                    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
            else:
                if status:
                    cursor.execute('SELECT * FROM projects WHERE user_id = ? AND status = ? ORDER BY created_at DESC', (user_id, status))
                else:
                    cursor.execute('SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            
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
    
    def update_project_total_cost(self, project_id: int):
        """Update project total cost to include both PDF analysis and manual items"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get PDF analysis total cost
            cursor.execute('SELECT total_cost FROM projects WHERE id = ?', (project_id,))
            pdf_result = cursor.fetchone()
            pdf_total = pdf_result[0] if pdf_result and pdf_result[0] else 0.0
            
            # Get manual items total cost
            cursor.execute('SELECT SUM(estimated_cost) FROM manual_items WHERE project_id = ?', (project_id,))
            manual_result = cursor.fetchone()
            manual_total = manual_result[0] if manual_result and manual_result[0] else 0.0
            
            # Calculate combined total
            combined_total = pdf_total + manual_total
            
            # Update project with combined total
            cursor.execute('''
                UPDATE projects 
                SET total_cost = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (combined_total, project_id))
            
            conn.commit()
            return combined_total
    
    def update_project_status(self, project_id: int, status: str):
        """Update project status"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, project_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_project_approval_status(self, project_id: int, admin_id: int, action: str, rejection_reason: str = None) -> bool:
        """Update project approval status (approve/reject) with admin tracking"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if project exists and is in a valid state for approval/rejection
            cursor.execute('SELECT status FROM projects WHERE id = ?', (project_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            current_status = result[0]
            valid_statuses = ['pending', 'estimate_submitted']
            if current_status not in valid_statuses:
                return False
            
            # Update project status based on action
            if action == "approve":
                new_status = "approved"
            elif action == "reject":
                new_status = "rejected"
            else:
                return False
            
            cursor.execute('''
                UPDATE projects 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_status, project_id))
            
            # Check if project update was successful
            project_updated = cursor.rowcount > 0
            
            # Also update the estimate history if it exists (optional)
            cursor.execute('''
                UPDATE estimate_history 
                SET status = ?, approval_date = CURRENT_TIMESTAMP, 
                    approved_by = (SELECT username FROM users WHERE id = ?),
                    notes = ?
                WHERE project_id = ? AND status = 'submitted'
            ''', (new_status, admin_id, rejection_reason, project_id))
            
            conn.commit()
            return project_updated
    
    def user_owns_project(self, user_id: int, project_id: int) -> bool:
        """Check if a user owns a specific project"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(projects)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            if 'user_id' not in column_names:
                # If user_id column doesn't exist, allow access for now
                # This is a temporary fix until the database is migrated
                print("⚠️ Warning: user_id column not found in projects table. Allowing access to all projects.")
                return True
            
            cursor.execute('SELECT COUNT(*) FROM projects WHERE id = ? AND user_id = ?', (project_id, user_id))
            count = cursor.fetchone()[0]
            return count > 0
    
    def get_estimator_project_stats(self, search: Optional[str] = None) -> List[Dict]:
        """Get project statistics for all estimators with optional name search"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists in projects table
            cursor.execute("PRAGMA table_info(projects)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            if 'user_id' not in column_names:
                # If user_id column doesn't exist, return empty list with warning
                print("⚠️ Warning: user_id column not found in projects table. Cannot track estimator project statistics.")
                return []
            
            # Build the base query
            base_query = '''
                SELECT 
                    u.id as estimator_id,
                    u.first_name,
                    u.last_name,
                    u.username,
                    u.company_name,
                    u.email,
                    u.created_at,
                    COUNT(p.id) as total_projects,
                    SUM(CASE WHEN p.status = 'pending' THEN 1 ELSE 0 END) as pending_projects,
                    SUM(CASE WHEN p.status = 'rejected' THEN 1 ELSE 0 END) as rejected_projects,
                    SUM(CASE WHEN p.status = 'active' THEN 1 ELSE 0 END) as active_projects,
                    COALESCE(SUM(p.total_cost), 0) as total_project_value
                FROM users u
                LEFT JOIN projects p ON u.id = p.user_id
                WHERE u.role = 'estimator' AND u.account_status = 'approved'
            '''
            
            params = []
            
            # Add search filter if provided
            if search:
                search_param = f'%{search}%'
                base_query += ' AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.username LIKE ? OR u.company_name LIKE ?)'
                params.extend([search_param, search_param, search_param, search_param])
            
            # Complete the query
            base_query += '''
                GROUP BY u.id, u.first_name, u.last_name, u.username, u.company_name, u.email, u.created_at
                ORDER BY u.created_at DESC
            '''
            
            cursor.execute(base_query, params)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            estimators = []
            for row in rows:
                estimator = dict(zip(columns, row))
                # Format the estimator data for the frontend
                formatted_estimator = {
                    'id': estimator['estimator_id'],
                    'name': f"{estimator.get('first_name', '')} {estimator.get('last_name', '')}".strip() or estimator['username'],
                    'company_name': estimator.get('company_name'),
                    'email': estimator['email'],
                    'total_projects': estimator['total_projects'] or 0,
                    'pending_projects': estimator['pending_projects'] or 0,
                    'rejected_projects': estimator['rejected_projects'] or 0,
                    'active_projects': estimator['active_projects'] or 0,
                    'total_project_value': estimator['total_project_value'] or 0,
                    'created_at': estimator['created_at']
                }
                estimators.append(formatted_estimator)
            
            return estimators
    
    def get_estimates_created_this_month(self) -> int:
        """Get count of projects created by estimators this month"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists in projects table
            cursor.execute("PRAGMA table_info(projects)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            if 'user_id' not in column_names:
                # If user_id column doesn't exist, return 0
                return 0
            
            # Get current month's projects created by estimators
            cursor.execute('''
                SELECT COUNT(*) 
                FROM projects p
                JOIN users u ON p.user_id = u.id
                WHERE u.role = 'estimator' 
                AND strftime('%Y-%m', p.created_at) = strftime('%Y-%m', 'now')
            ''')
            
            return cursor.fetchone()[0]
    
    def get_projects_created_in_date_range(self, start_date: str, end_date: str) -> int:
        """Get count of projects created within date range"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM projects
                WHERE created_at >= ? AND created_at <= ?
            ''', (start_date, end_date))
            return cursor.fetchone()[0]


class QuotationManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def create_quotation(self, user_id: int, quotation_data: Dict[str, Any] = None) -> int:
        """Create a new quotation for a user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create quotation with minimal data (auto-increment ID) and set status to pending
            cursor.execute('''
                INSERT INTO quotations (user_id, quotation_name, client_name, client_email, 
                                      client_phone, project_address, project_description, 
                                      notes, valid_until, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                quotation_data.get('quotation_name') if quotation_data else None,
                quotation_data.get('client_name') if quotation_data else None,
                quotation_data.get('client_email') if quotation_data else None,
                quotation_data.get('client_phone') if quotation_data else None,
                quotation_data.get('project_address') if quotation_data else None,
                quotation_data.get('project_description') if quotation_data else None,
                quotation_data.get('notes') if quotation_data else None,
                quotation_data.get('valid_until') if quotation_data else None,
                'pending'  # Set status to pending for new quotations
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_quotation(self, quotation_id: int) -> Optional[Dict]:
        """Get quotation by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quotations WHERE id = ?', (quotation_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_quotations_by_user(self, user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all quotations for a user with optional status filter"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the base query
            base_query = '''
                SELECT q.*, 
                       COUNT(qi.id) as item_count,
                       COALESCE(SUM(qi.total_cost), 0) as calculated_total,
                       GROUP_CONCAT(DISTINCT qi.sku) as skus
                FROM quotations q
                LEFT JOIN quotation_items qi ON q.id = qi.quotation_id
                WHERE q.user_id = ?
            '''
            
            params = [user_id]
            
            # Add status filter if provided
            if status:
                base_query += ' AND q.status = ?'
                params.append(status)
            
            # Complete the query
            base_query += '''
                GROUP BY q.id
                ORDER BY q.created_at DESC
            '''
            
            cursor.execute(base_query, params)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            quotations = []
            
            for row in rows:
                quotation = dict(zip(columns, row))
                # Process SKUs - convert comma-separated string to list and filter out None/empty values
                skus_str = quotation.get('skus', '')
                if skus_str:
                    skus = [sku.strip() for sku in skus_str.split(',') if sku.strip() and sku.strip() != 'None']
                    quotation['skus'] = skus
                else:
                    quotation['skus'] = []
                quotations.append(quotation)
            
            return quotations
    
    def update_quotation(self, quotation_id: int, updates: Dict[str, Any]) -> bool:
        """Update quotation details"""
        if not updates:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [quotation_id]
            
            cursor.execute(f'''
                UPDATE quotations 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_quotation(self, quotation_id: int) -> bool:
        """Delete quotation and all its items"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quotations WHERE id = ?', (quotation_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_contractor_quotation_stats(self, search: Optional[str] = None) -> List[Dict]:
        """Get quotation statistics for all contractors with optional name search"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the base query
            base_query = '''
                SELECT 
                    u.id as contractor_id,
                    u.first_name,
                    u.last_name,
                    u.username,
                    u.company_name,
                    u.email,
                    u.created_at,
                    COUNT(q.id) as total_quotations,
                    SUM(CASE WHEN q.status = 'approved' THEN 1 ELSE 0 END) as approved_quotations,
                    SUM(CASE WHEN q.status = 'pending' OR q.status = 'sent' OR q.status = 'draft' THEN 1 ELSE 0 END) as pending_quotations,
                    SUM(CASE WHEN q.status = 'rejected' THEN 1 ELSE 0 END) as declined_quotations
                FROM users u
                LEFT JOIN quotations q ON u.id = q.user_id
                WHERE u.role = 'contractor' AND u.account_status = 'approved'
            '''
            
            params = []
            
            # Add search filter if provided
            if search:
                search_param = f'%{search}%'
                base_query += ' AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.username LIKE ? OR u.company_name LIKE ?)'
                params.extend([search_param, search_param, search_param, search_param])
            
            # Complete the query
            base_query += '''
                GROUP BY u.id, u.first_name, u.last_name, u.username, u.company_name, u.email, u.created_at
                ORDER BY u.created_at DESC
            '''
            
            cursor.execute(base_query, params)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            contractors = []
            for row in rows:
                contractor = dict(zip(columns, row))
                # Format the contractor data for the frontend
                formatted_contractor = {
                    'id': contractor['contractor_id'],
                    'name': f"{contractor.get('first_name', '')} {contractor.get('last_name', '')}".strip() or contractor['username'],
                    'company_name': contractor.get('company_name'),
                    'email': contractor['email'],
                    'total_quotations': contractor['total_quotations'] or 0,
                    'approved_quotations': contractor['approved_quotations'] or 0,
                    'pending_quotations': contractor['pending_quotations'] or 0,
                    'declined_quotations': contractor['declined_quotations'] or 0,
                    'created_at': contractor['created_at']
                }
                contractors.append(formatted_contractor)
            
            return contractors
    
    def get_estimator_quotation_stats(self, search: Optional[str] = None) -> List[Dict]:
        """Get quotation statistics for all estimators with optional name search"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the base query
            base_query = '''
                SELECT 
                    u.id as estimator_id,
                    u.first_name,
                    u.last_name,
                    u.username,
                    u.company_name,
                    u.email,
                    u.created_at,
                    COUNT(q.id) as total_quotations,
                    SUM(CASE WHEN q.status = 'approved' THEN 1 ELSE 0 END) as approved_quotations,
                    SUM(CASE WHEN q.status = 'pending' OR q.status = 'sent' OR q.status = 'draft' THEN 1 ELSE 0 END) as pending_quotations,
                    SUM(CASE WHEN q.status = 'rejected' THEN 1 ELSE 0 END) as declined_quotations
                FROM users u
                LEFT JOIN quotations q ON u.id = q.user_id
                WHERE u.role = 'estimator' AND u.account_status = 'approved'
            '''
            
            params = []
            
            # Add search filter if provided
            if search:
                search_param = f'%{search}%'
                base_query += ' AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.username LIKE ? OR u.company_name LIKE ?)'
                params.extend([search_param, search_param, search_param, search_param])
            
            # Complete the query
            base_query += '''
                GROUP BY u.id, u.first_name, u.last_name, u.username, u.company_name, u.email, u.created_at
                ORDER BY u.created_at DESC
            '''
            
            cursor.execute(base_query, params)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            estimators = []
            for row in rows:
                estimator = dict(zip(columns, row))
                # Format the estimator data for the frontend
                formatted_estimator = {
                    'id': estimator['estimator_id'],
                    'name': f"{estimator.get('first_name', '')} {estimator.get('last_name', '')}".strip() or estimator['username'],
                    'company_name': estimator.get('company_name'),
                    'email': estimator['email'],
                    'total_quotations': estimator['total_quotations'] or 0,
                    'approved_quotations': estimator['approved_quotations'] or 0,
                    'pending_quotations': estimator['pending_quotations'] or 0,
                    'declined_quotations': estimator['declined_quotations'] or 0,
                    'created_at': estimator['created_at']
                }
                estimators.append(formatted_estimator)
            
            return estimators
    
    def get_all_quotations_with_contractor_details(self, search: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all quotations with contractor details for admin dashboard"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the base query with contractor information
            base_query = '''
                SELECT 
                    q.id as quotation_id,
                    q.quotation_name,
                    q.client_name,
                    q.client_email,
                    q.client_phone,
                    q.project_address,
                    q.project_description,
                    q.total_cost,
                    q.status,
                    q.valid_until,
                    q.notes,
                    q.created_at,
                    q.updated_at,
                    u.id as contractor_id,
                    u.first_name,
                    u.last_name,
                    u.username,
                    u.company_name,
                    u.email as contractor_email,
                    u.phone as contractor_phone,
                    COUNT(qi.id) as item_count,
                    GROUP_CONCAT(DISTINCT qi.sku) as skus
                FROM quotations q
                LEFT JOIN users u ON q.user_id = u.id
                LEFT JOIN quotation_items qi ON q.id = qi.quotation_id
            '''
            
            where_conditions = []
            params = []
            
            # Add search filter if provided
            if search:
                search_param = f'%{search}%'
                where_conditions.append('''
                    (q.quotation_name LIKE ? OR q.client_name LIKE ? OR 
                     u.first_name LIKE ? OR u.last_name LIKE ? OR 
                     u.company_name LIKE ? OR u.username LIKE ?)
                ''')
                params.extend([search_param, search_param, search_param, search_param, search_param, search_param])
            
            # Add status filter if provided
            if status:
                where_conditions.append('q.status = ?')
                params.append(status)
            
            # Add WHERE clause if conditions exist
            if where_conditions:
                base_query += ' WHERE ' + ' AND '.join(where_conditions)
            
            # Complete the query with grouping and ordering
            base_query += '''
                GROUP BY q.id, q.quotation_name, q.client_name, q.client_email, q.client_phone,
                         q.project_address, q.project_description, q.total_cost, q.status,
                         q.valid_until, q.notes, q.created_at, q.updated_at,
                         u.id, u.first_name, u.last_name, u.username, u.company_name,
                         u.email, u.phone
                ORDER BY q.created_at DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            cursor.execute(base_query, params)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            quotations = []
            for row in rows:
                quotation = dict(zip(columns, row))
                
                # Format contractor name
                contractor_name = "Unknown"
                if quotation.get('first_name') and quotation.get('last_name'):
                    contractor_name = f"{quotation['first_name']} {quotation['last_name']}"
                elif quotation.get('company_name'):
                    contractor_name = quotation['company_name']
                elif quotation.get('username'):
                    contractor_name = quotation['username']
                
                # Process SKUs - convert comma-separated string to list and filter out None/empty values
                skus_str = quotation.get('skus', '')
                if skus_str:
                    skus = [sku.strip() for sku in skus_str.split(',') if sku.strip() and sku.strip() != 'None']
                    quotation['skus'] = skus
                else:
                    quotation['skus'] = []
                
                # Format the quotation data for the frontend
                formatted_quotation = {
                    'quotation_id': quotation['quotation_id'],
                    'quotation_name': quotation.get('quotation_name', 'Untitled Quotation'),
                    'client_name': quotation.get('client_name'),
                    'client_email': quotation.get('client_email'),
                    'client_phone': quotation.get('client_phone'),
                    'project_address': quotation.get('project_address'),
                    'project_description': quotation.get('project_description'),
                    'total_cost': quotation.get('total_cost', 0),
                    'status': quotation.get('status', 'draft'),
                    'valid_until': quotation.get('valid_until'),
                    'notes': quotation.get('notes'),
                    'created_at': quotation.get('created_at'),
                    'updated_at': quotation.get('updated_at'),
                    'contractor': {
                        'id': quotation.get('contractor_id'),
                        'name': contractor_name,
                        'first_name': quotation.get('first_name'),
                        'last_name': quotation.get('last_name'),
                        'username': quotation.get('username'),
                        'company_name': quotation.get('company_name'),
                        'email': quotation.get('contractor_email'),
                        'phone': quotation.get('contractor_phone')
                    },
                    'item_count': quotation.get('item_count', 0),
                    'skus': quotation.get('skus', [])
                }
                quotations.append(formatted_quotation)
            
            return quotations
    
    def get_quotations_count(self, search: Optional[str] = None, status: Optional[str] = None) -> int:
        """Get total count of quotations for pagination"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = '''
                SELECT COUNT(DISTINCT q.id)
                FROM quotations q
                LEFT JOIN users u ON q.user_id = u.id
            '''
            
            where_conditions = []
            params = []
            
            # Add search filter if provided
            if search:
                search_param = f'%{search}%'
                where_conditions.append('''
                    (q.quotation_name LIKE ? OR q.client_name LIKE ? OR 
                     u.first_name LIKE ? OR u.last_name LIKE ? OR 
                     u.company_name LIKE ? OR u.username LIKE ?)
                ''')
                params.extend([search_param, search_param, search_param, search_param, search_param, search_param])
            
            # Add status filter if provided
            if status:
                where_conditions.append('q.status = ?')
                params.append(status)
            
            # Add WHERE clause if conditions exist
            if where_conditions:
                base_query += ' WHERE ' + ' AND '.join(where_conditions)
            
            cursor.execute(base_query, params)
            return cursor.fetchone()[0]
    
    def get_quotations_added_this_month(self) -> int:
        """Get count of quotations added by contractors this month"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current month's quotations created by contractors
            cursor.execute('''
                SELECT COUNT(*) 
                FROM quotations q
                JOIN users u ON q.user_id = u.id
                WHERE u.role = 'contractor' 
                AND strftime('%Y-%m', q.created_at) = strftime('%Y-%m', 'now')
            ''')
            
            return cursor.fetchone()[0]
    
    def get_quotations_created_in_date_range(self, start_date: str, end_date: str) -> int:
        """Get count of quotations created within date range"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM quotations
                WHERE created_at >= ? AND created_at <= ?
            ''', (start_date, end_date))
            return cursor.fetchone()[0]

    def update_quotation_status(self, quotation_id: int, admin_id: int, action: str, rejection_reason: str = None) -> bool:
        """Update quotation status (approve or reject)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if action == "reject":
                # Reject quotation
                cursor.execute('''
                    UPDATE quotations 
                    SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND status IN ('pending', 'draft', 'sent')
                ''', (quotation_id,))
            elif action == "approve":
                # Approve quotation
                cursor.execute('''
                    UPDATE quotations 
                    SET status = 'approved', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND status IN ('pending', 'draft', 'sent')
                ''', (quotation_id,))
            else:
                return False
            
            conn.commit()
            return cursor.rowcount > 0


class QuotationItemManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def add_item_to_quotation(self, quotation_id: int, item_data: Dict[str, Any]) -> int:
        """Add an item to a quotation"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate total cost
            quantity = item_data.get('quantity', 1)
            cost = item_data.get('cost', 0)
            total_cost = quantity * cost
            
            cursor.execute('''
                INSERT INTO quotation_items (
                    quotation_id, item_name, sku, unit, unit_of_measure, 
                    cost, quantity, total_cost, description, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quotation_id,
                item_data['item_name'],
                item_data.get('sku'),
                item_data.get('unit', 'each'),
                item_data['unit_of_measure'],
                cost,
                quantity,
                total_cost,
                item_data.get('description'),
                item_data.get('category')
            ))
            
            # Update quotation total cost
            self._update_quotation_total_cost(quotation_id, conn)
            
            conn.commit()
            return cursor.lastrowid
    
    def get_items_by_quotation(self, quotation_id: int) -> List[Dict]:
        """Get all items for a quotation"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM quotation_items 
                WHERE quotation_id = ? 
                ORDER BY created_at ASC
            ''', (quotation_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            items = []
            
            for row in rows:
                item = dict(zip(columns, row))
                # Return N/A for empty SKU
                if not item['sku']:
                    item['sku'] = 'N/A'
                items.append(item)
            
            return items
    
    def update_item(self, item_id: int, updates: Dict[str, Any]) -> bool:
        """Update quotation item"""
        if not updates:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # If cost or quantity is being updated, recalculate total_cost
            if 'cost' in updates or 'quantity' in updates:
                # Get current values
                cursor.execute('SELECT cost, quantity FROM quotation_items WHERE id = ?', (item_id,))
                current = cursor.fetchone()
                if current:
                    current_cost = updates.get('cost', current[0])
                    current_quantity = updates.get('quantity', current[1])
                    updates['total_cost'] = current_cost * current_quantity
            
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [item_id]
            
            cursor.execute(f'''
                UPDATE quotation_items 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            if cursor.rowcount > 0:
                # Get quotation_id to update total
                cursor.execute('SELECT quotation_id FROM quotation_items WHERE id = ?', (item_id,))
                result = cursor.fetchone()
                if result:
                    self._update_quotation_total_cost(result[0], conn)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """Delete quotation item"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get quotation_id before deleting
            cursor.execute('SELECT quotation_id FROM quotation_items WHERE id = ?', (item_id,))
            result = cursor.fetchone()
            
            cursor.execute('DELETE FROM quotation_items WHERE id = ?', (item_id,))
            
            if cursor.rowcount > 0 and result:
                # Update quotation total cost
                self._update_quotation_total_cost(result[0], conn)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def _update_quotation_total_cost(self, quotation_id: int, conn=None):
        """Update quotation total cost based on items"""
        if conn is None:
            with self.db.get_connection() as new_conn:
                cursor = new_conn.cursor()
                cursor.execute('''
                    UPDATE quotations 
                    SET total_cost = (
                        SELECT COALESCE(SUM(total_cost), 0) 
                        FROM quotation_items 
                        WHERE quotation_id = ?
                    ), updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quotation_id, quotation_id))
                new_conn.commit()
        else:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE quotations 
                SET total_cost = (
                    SELECT COALESCE(SUM(total_cost), 0) 
                    FROM quotation_items 
                    WHERE quotation_id = ?
                ), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (quotation_id, quotation_id))


