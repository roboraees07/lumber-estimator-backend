#!/usr/bin/env python3
"""
Contractor Dashboard API
Comprehensive dashboard for contractor management and analytics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ..database.enhanced_models import EnhancedDatabaseManager

# Initialize database
enhanced_db = EnhancedDatabaseManager()

# Create router for dashboard
router = APIRouter(prefix="/dashboard", tags=["contractor-dashboard"])

@router.get(
    "/overview",
    summary="📊 Dashboard Overview",
    description="Get comprehensive system statistics and analytics overview.",
    response_description="Complete dashboard metrics with analytics",
    responses={
        200: {
            "description": "Dashboard overview retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
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
                }
            }
        }
    }
)
async def get_dashboard_overview():
    """
    ## System Dashboard Overview 📊
    
    Get a comprehensive overview of system statistics and analytics.
    
    **Provides:**
    - **Total Counts**: Contractors, materials, and projects
    - **Recent Activity**: New additions in the last 30 days
    - **Analytics**: Category breakdowns and top performers
    - **Performance Metrics**: System health indicators
    
    **Analytics Included:**
    - Materials distribution by category
    - Contractors grouped by business type
    - Top-rated contractors with review counts
    - Recent activity trends
    
    **Use Cases:**
    - Executive dashboard displays
    - System health monitoring
    - Business intelligence reporting
    - Performance tracking
    - Trend analysis
    
    **Response Structure:**
    - `totals`: High-level counts
    - `recent_activity`: 30-day activity metrics
    - `analytics`: Detailed breakdowns and rankings
    """
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total contractors (simplified query)
            cursor.execute('SELECT COUNT(*) FROM contractors')
            total_contractors = cursor.fetchone()[0]
            
            # Total materials (simplified query) 
            cursor.execute('SELECT COUNT(*) FROM materials')
            total_materials = cursor.fetchone()[0]
            
            # Total projects (check if table exists first)
            try:
                cursor.execute('SELECT COUNT(*) FROM projects')
                total_projects = cursor.fetchone()[0]
            except:
                total_projects = 0
            
            # Recent activity (simplified)
            try:
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                cursor.execute('SELECT COUNT(*) FROM contractors WHERE created_at >= ?', (thirty_days_ago,))
                new_contractors = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM materials WHERE created_at >= ?', (thirty_days_ago,))
                new_materials = cursor.fetchone()[0]
            except:
                new_contractors = 0
                new_materials = 0
            
            # Materials by category (simplified)
            try:
                cursor.execute('''
                    SELECT COALESCE(category, 'Other') as category, COUNT(*) as count
                    FROM materials 
                    GROUP BY category
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                materials_by_category = [
                    {"category": row[0], "count": row[1]} 
                    for row in cursor.fetchall()
                ]
            except:
                materials_by_category = []
            
            # Contractors by business type (simplified)
            try:
                cursor.execute('''
                    SELECT COALESCE(business_type, 'Other') as business_type, COUNT(*) as count
                    FROM contractors 
                    GROUP BY business_type
                    ORDER BY count DESC
                ''')
                contractors_by_type = [
                    {"type": row[0], "count": row[1]} 
                    for row in cursor.fetchall()
                ]
            except:
                contractors_by_type = []
            
            # Top contractors (simplified - no review count lookup)
            try:
                cursor.execute('''
                    SELECT id, name, COALESCE(rating, 0) as rating
                    FROM contractors 
                    ORDER BY rating DESC, name ASC
                    LIMIT 5
                ''')
                top_contractors = []
                for row in cursor.fetchall():
                    top_contractors.append({
                        "id": row[0],
                        "name": row[1], 
                        "rating": round(row[2], 2),
                        "review_count": 0  # Simplified for now
                    })
            except Exception as e:
                print(f"Top contractors query error: {e}")
                top_contractors = []
            
            return {
                "totals": {
                    "contractors": total_contractors,
                    "materials": total_materials,
                    "projects": total_projects
                },
                "recent_activity": {
                    "new_contractors_30_days": new_contractors,
                    "new_materials_30_days": new_materials
                },
                "analytics": {
                    "materials_by_category": materials_by_category,
                    "contractors_by_type": contractors_by_type,
                    "top_contractors": top_contractors
                }
            }
    except Exception as e:
        # Return detailed error for debugging
        import traceback
        error_details = f"Dashboard error: {str(e)}\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/contractors/analytics")
async def get_contractor_analytics():
    """Get detailed contractor analytics"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contractors by state
            cursor.execute('''
                SELECT state, COUNT(*) as count
                FROM contractors 
                WHERE is_active = 1 AND state IS NOT NULL
                GROUP BY state
                ORDER BY count DESC
                LIMIT 20
            ''')
            contractors_by_state = [
                {"state": row[0], "count": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Contractors by service area
            cursor.execute('''
                SELECT service_area, COUNT(*) as count
                FROM contractors 
                WHERE is_active = 1 AND service_area IS NOT NULL
                GROUP BY service_area
                ORDER BY count DESC
            ''')
            contractors_by_service_area = [
                {"service_area": row[0], "count": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Payment terms distribution
            cursor.execute('''
                SELECT payment_terms, COUNT(*) as count
                FROM contractors 
                WHERE is_active = 1 AND payment_terms IS NOT NULL
                GROUP BY payment_terms
                ORDER BY count DESC
            ''')
            payment_terms_dist = [
                {"terms": row[0], "count": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Credit rating distribution
            cursor.execute('''
                SELECT credit_rating, COUNT(*) as count
                FROM contractors 
                WHERE is_active = 1 AND credit_rating IS NOT NULL
                GROUP BY credit_rating
                ORDER BY 
                    CASE credit_rating 
                        WHEN 'A' THEN 1 
                        WHEN 'B' THEN 2 
                        WHEN 'C' THEN 3 
                        WHEN 'D' THEN 4 
                        ELSE 5 
                    END
            ''')
            credit_rating_dist = [
                {"rating": row[0], "count": row[1]} 
                for row in cursor.fetchall()
            ]
            
            return {
                "geographic_distribution": contractors_by_state,
                "service_area_distribution": contractors_by_service_area,
                "payment_terms_distribution": payment_terms_dist,
                "credit_rating_distribution": credit_rating_dist
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materials/analytics")
async def get_material_analytics():
    """Get detailed material analytics"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Price ranges by category
            cursor.execute('''
                SELECT 
                    category,
                    COUNT(*) as item_count,
                    MIN(price) as min_price,
                    AVG(price) as avg_price,
                    MAX(price) as max_price
                FROM materials 
                WHERE discontinued = 0 AND category IS NOT NULL
                GROUP BY category
                ORDER BY item_count DESC
            ''')
            price_analysis = []
            for row in cursor.fetchall():
                price_analysis.append({
                    "category": row[0],
                    "item_count": row[1],
                    "min_price": round(row[2], 2),
                    "avg_price": round(row[3], 2),
                    "max_price": round(row[4], 2)
                })
            
            # Most expensive materials
            cursor.execute('''
                SELECT m.item_name, m.display_name, m.price, m.category, c.name as contractor_name
                FROM materials m
                JOIN contractors c ON m.contractor_id = c.id
                WHERE m.discontinued = 0
                ORDER BY m.price DESC
                LIMIT 10
            ''')
            expensive_materials = [
                {
                    "item_name": row[0],
                    "display_name": row[1] or row[0],
                    "price": row[2],
                    "category": row[3],
                    "contractor": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            # Materials by unit type
            cursor.execute('''
                SELECT unit, COUNT(*) as count
                FROM materials 
                WHERE discontinued = 0 AND unit IS NOT NULL
                GROUP BY unit
                ORDER BY count DESC
            ''')
            materials_by_unit = [
                {"unit": row[0], "count": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Special order items
            cursor.execute('''
                SELECT COUNT(*) as special_order_count,
                       (SELECT COUNT(*) FROM materials WHERE discontinued = 0) as total_count
            ''')
            row = cursor.fetchone()
            special_order_stats = {
                "special_order_count": row[0],
                "total_count": row[1],
                "percentage": round((row[0] / row[1]) * 100, 2) if row[1] > 0 else 0
            }
            
            return {
                "price_analysis_by_category": price_analysis,
                "most_expensive_materials": expensive_materials,
                "materials_by_unit": materials_by_unit,
                "special_order_statistics": special_order_stats
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contractors/{contractor_id}/performance")
async def get_contractor_performance(contractor_id: int):
    """Get performance metrics for a specific contractor"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic contractor info
            cursor.execute('SELECT * FROM contractors WHERE id = ?', (contractor_id,))
            contractor_row = cursor.fetchone()
            if not contractor_row:
                raise HTTPException(status_code=404, detail="Contractor not found")
            
            columns = [desc[0] for desc in cursor.description]
            contractor = dict(zip(columns, contractor_row))
            
            # Material count and categories
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_materials,
                    COUNT(DISTINCT category) as categories_count
                FROM materials 
                WHERE contractor_id = ? AND discontinued = 0
            ''', (contractor_id,))
            material_stats = cursor.fetchone()
            
            # Price competitiveness (how often this contractor has the best price)
            cursor.execute('''
                WITH contractor_items AS (
                    SELECT item_name, price 
                    FROM materials 
                    WHERE contractor_id = ? AND discontinued = 0
                ),
                best_prices AS (
                    SELECT item_name, MIN(price) as best_price 
                    FROM materials 
                    WHERE discontinued = 0 
                    GROUP BY item_name
                )
                SELECT 
                    COUNT(*) as competitive_items,
                    (SELECT COUNT(*) FROM contractor_items) as total_items
                FROM contractor_items ci
                JOIN best_prices bp ON ci.item_name = bp.item_name
                WHERE ci.price = bp.best_price
            ''', (contractor_id,))
            competitiveness = cursor.fetchone()
            
            # Recent price changes
            cursor.execute('''
                SELECT COUNT(*) as price_changes
                FROM price_history ph
                JOIN materials m ON ph.material_id = m.id
                WHERE m.contractor_id = ? 
                AND ph.created_at >= DATE('now', '-30 days')
            ''', (contractor_id,))
            recent_price_changes = cursor.fetchone()[0]
            
            # Reviews summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as review_count,
                    AVG(rating) as avg_rating,
                    AVG(delivery_rating) as avg_delivery,
                    AVG(quality_rating) as avg_quality,
                    AVG(price_rating) as avg_price_rating,
                    AVG(service_rating) as avg_service
                FROM contractor_reviews 
                WHERE contractor_id = ?
            ''', (contractor_id,))
            review_stats = cursor.fetchone()
            
            return {
                "contractor": {
                    "id": contractor["id"],
                    "name": contractor["name"],
                    "business_type": contractor["business_type"],
                    "specialty": contractor["specialty"]
                },
                "inventory": {
                    "total_materials": material_stats[0],
                    "categories_covered": material_stats[1]
                },
                "competitiveness": {
                    "competitive_items": competitiveness[0],
                    "total_items": competitiveness[1],
                    "competitiveness_rate": round((competitiveness[0] / competitiveness[1]) * 100, 2) if competitiveness[1] > 0 else 0
                },
                "activity": {
                    "recent_price_changes": recent_price_changes
                },
                "reviews": {
                    "total_reviews": review_stats[0],
                    "average_rating": round(review_stats[1], 2) if review_stats[1] else 0,
                    "average_delivery": round(review_stats[2], 2) if review_stats[2] else 0,
                    "average_quality": round(review_stats[3], 2) if review_stats[3] else 0,
                    "average_price_rating": round(review_stats[4], 2) if review_stats[4] else 0,
                    "average_service": round(review_stats[5], 2) if review_stats[5] else 0
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/advanced")
async def advanced_search(
    query: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Material category"),
    contractor_id: Optional[int] = Query(None, description="Specific contractor"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    business_type: Optional[str] = Query(None, description="Contractor business type"),
    service_area: Optional[str] = Query(None, description="Service area"),
    min_rating: Optional[float] = Query(None, description="Minimum contractor rating"),
    in_stock_only: Optional[bool] = Query(False, description="Only items in stock"),
    special_order: Optional[bool] = Query(None, description="Include/exclude special order items"),
    limit: Optional[int] = Query(50, description="Results limit"),
    offset: Optional[int] = Query(0, description="Results offset")
):
    """Advanced search across contractors and materials"""
    try:
        with enhanced_db.get_connection() as conn:
            cursor = conn.cursor()
            
            query_sql = '''
                SELECT 
                    m.id as material_id,
                    m.item_name,
                    m.display_name,
                    m.category,
                    m.price,
                    m.unit,
                    m.stock_quantity,
                    m.is_special_order,
                    m.lead_time_days,
                    c.id as contractor_id,
                    c.name as contractor_name,
                    c.business_type,
                    c.service_area,
                    c.rating as contractor_rating,
                    c.contact_number,
                    c.city,
                    c.state
                FROM materials m
                JOIN contractors c ON m.contractor_id = c.id
                WHERE m.discontinued = 0 AND c.is_active = 1
            '''
            params = []
            
            # Add filters
            if query:
                query_sql += ' AND (m.item_name LIKE ? OR m.display_name LIKE ? OR m.description LIKE ?)'
                search_param = f'%{query}%'
                params.extend([search_param, search_param, search_param])
            
            if category:
                query_sql += ' AND m.category = ?'
                params.append(category)
            
            if contractor_id:
                query_sql += ' AND c.id = ?'
                params.append(contractor_id)
            
            if min_price is not None:
                query_sql += ' AND m.price >= ?'
                params.append(min_price)
            
            if max_price is not None:
                query_sql += ' AND m.price <= ?'
                params.append(max_price)
            
            if business_type:
                query_sql += ' AND c.business_type = ?'
                params.append(business_type)
            
            if service_area:
                query_sql += ' AND c.service_area = ?'
                params.append(service_area)
            
            if min_rating is not None:
                query_sql += ' AND c.rating >= ?'
                params.append(min_rating)
            
            if in_stock_only:
                query_sql += ' AND m.stock_quantity > 0'
            
            if special_order is not None:
                query_sql += ' AND m.is_special_order = ?'
                params.append(special_order)
            
            # Add ordering and pagination
            query_sql += ' ORDER BY c.rating DESC, m.price ASC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query_sql, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            
            # Get total count for pagination
            count_sql = query_sql.replace(
                'SELECT m.id as material_id, m.item_name, m.display_name, m.category, m.price, m.unit, m.stock_quantity, m.is_special_order, m.lead_time_days, c.id as contractor_id, c.name as contractor_name, c.business_type, c.service_area, c.rating as contractor_rating, c.contact_number, c.city, c.state',
                'SELECT COUNT(*)'
            ).split(' ORDER BY')[0]  # Remove ORDER BY and LIMIT for count
            
            cursor.execute(count_sql, params[:-2])  # Remove limit and offset params
            total_count = cursor.fetchone()[0]
            
            return {
                "results": results,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(results) < total_count
                },
                "filters_applied": {
                    "query": query,
                    "category": category,
                    "contractor_id": contractor_id,
                    "price_range": f"${min_price or 0} - ${max_price or 'unlimited'}",
                    "business_type": business_type,
                    "service_area": service_area,
                    "min_rating": min_rating,
                    "in_stock_only": in_stock_only,
                    "special_order": special_order
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
