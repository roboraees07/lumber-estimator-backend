#!/usr/bin/env python3
"""
User Authentication Models for Lumber Estimator
Handles user accounts, roles, and approval workflow
"""

import sqlite3
import bcrypt
import jwt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CONTRACTOR = "contractor"
    ESTIMATOR = "estimator"

class AccountStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class AuthDatabaseManager:
    def __init__(self, db_path: str = "data/lumber_estimator.db"):
        """Initialize authentication database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.secret_key = "your-secret-key-change-in-production"  # In production, use environment variable
        self.init_auth_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_auth_database(self):
        """Create authentication tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table for authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'contractor', 'estimator')),
                    account_status TEXT NOT NULL DEFAULT 'pending' CHECK (account_status IN ('pending', 'approved', 'rejected', 'suspended')),
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    company_name TEXT,
                    business_license TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    profile_completed BOOLEAN DEFAULT 0,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    rejection_reason TEXT,
                    FOREIGN KEY (approved_by) REFERENCES users (id)
                )
            ''')
            
            # User sessions for JWT management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Password reset tokens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create default admin user if not exists
            self._create_default_admin(cursor)
            
            conn.commit()
    
    def _create_default_admin(self, cursor):
        """Create default admin user"""
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            # Create default admin: admin/admin123
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (
                    username, email, password_hash, role, account_status, 
                    first_name, last_name, profile_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 'admin@lumber-estimator.com', password_hash.decode('utf-8'),
                'admin', 'approved', 'System', 'Administrator', 1
            ))
            print("✅ Default admin user created: admin/admin123")

class UserAuthManager:
    def __init__(self, auth_db: AuthDatabaseManager):
        self.auth_db = auth_db
        self.secret_key = auth_db.secret_key
    
    def _format_date(self, date_value) -> str:
        """Helper method to format date values from SQLite"""
        if not date_value:
            return ''
        
        try:
            from datetime import datetime
            # SQLite returns datetime as string, so parse it first
            if isinstance(date_value, str):
                # Handle different datetime formats
                date_str = str(date_value)
                if 'T' in date_str:
                    # ISO format: 2024-01-15T10:30:00
                    dt = datetime.fromisoformat(date_str.replace('Z', ''))
                else:
                    # SQLite format: 2024-01-15 10:30:00
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%d %b. %Y')
            else:
                # If it's already a datetime object
                return date_value.strftime('%d %b. %Y')
        except (ValueError, AttributeError, TypeError):
            # Fallback: just use the date part of the string
            return str(date_value)[:10]
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """Create new user account"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Hash password
            password_hash = self.hash_password(user_data['password'])
            
            # Set account status based on role
            account_status = 'approved' if user_data['role'] == 'admin' else 'pending'
            
            cursor.execute('''
                INSERT INTO users (
                    username, email, password_hash, role, account_status,
                    first_name, last_name, phone, company_name, business_license,
                    address, city, state, zip_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['role'],
                account_status,
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('phone'),
                user_data.get('company_name'),
                user_data.get('business_license'),
                user_data.get('address'),
                user_data.get('city'),
                user_data.get('state'),
                user_data.get('zip_code')
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
    
    # Previously implemented but commented out for testing out new logic
    # def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
    #     """Authenticate user and return user data"""
    #     with self.auth_db.get_connection() as conn:
    #         cursor = conn.cursor()
            
    #         cursor.execute('''
    #             SELECT id, username, email, password_hash, role, account_status,
    #                    first_name, last_name, company_name, profile_completed
    #             FROM users WHERE username = ? OR email = ?
    #         ''', (username, username))
            
    #         row = cursor.fetchone()
    #         if not row:
    #             return None
            
    #         user_id, username, email, password_hash, role, account_status, first_name, last_name, company_name, profile_completed = row
            
    #         # Check if account is approved
    #         if account_status != 'approved':
    #             return None
            
    #         # Verify password
    #         if not self.verify_password(password, password_hash):
    #             return None
            
    #         # Update last login
    #         cursor.execute('''
    #             UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
    #         ''', (user_id,))
    #         conn.commit()
            
    #         return {
    #             'id': user_id,
    #             'username': username,
    #             'email': email,
    #             'role': role,
    #             'account_status': account_status,
    #             'first_name': first_name,
    #             'last_name': last_name,
    #             'company_name': company_name,
    #             'profile_completed': profile_completed
    #         }
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, role, account_status,
                    first_name, last_name, company_name, profile_completed
                FROM users WHERE username = ? OR email = ?
            ''', (username, username))
            
            row = cursor.fetchone()
            if not row:
                return None # User does not exist
            
            # Unpack all data from the row
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            
            # Verify password first
            if not self.verify_password(password, user['password_hash']):
                return None # Incorrect password
            
            # Password is correct, now update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            
            # Return the user data, including their status
            return user
    
    def generate_jwt_token(self, user_data: Dict) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_pending_approvals(self) -> List[Dict]:
        """Get list of users pending approval"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, role, first_name, last_name,
                       company_name, business_license, created_at
                FROM users 
                WHERE account_status = 'pending' AND role != 'admin'
                ORDER BY created_at ASC
            ''')
            
            rows = cursor.fetchall()
            columns = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 
                      'company_name', 'business_license', 'created_at']
            
            return [dict(zip(columns, row)) for row in rows]
    
    def update_user_status(self, user_id: int, admin_id: int, action: str, rejection_reason: str = None) -> bool:
        """Update user account status (approve or reject)"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            if action == "reject":
                # Reject user
                cursor.execute('''
                    UPDATE users 
                    SET account_status = 'rejected', approved_by = ?, 
                        approved_at = CURRENT_TIMESTAMP, rejection_reason = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND account_status = 'pending'
                ''', (admin_id, rejection_reason, user_id))
            elif action == "approve":
                # Approve user
                cursor.execute('''
                    UPDATE users 
                    SET account_status = 'approved', approved_by = ?, 
                        approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND account_status = 'pending'
                ''', (admin_id, user_id))
            else:
                return False
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, role, account_status, first_name, last_name,
                       company_name, business_license, address, city, state, zip_code,
                       phone, profile_completed, created_at, approved_at
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = ['id', 'username', 'email', 'role', 'account_status', 'first_name', 'last_name',
                      'company_name', 'business_license', 'address', 'city', 'state', 'zip_code',
                      'phone', 'profile_completed', 'created_at', 'approved_at']
            
            return dict(zip(columns, row))
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            for key, value in profile_data.items():
                if key in ['first_name', 'last_name', 'phone', 'company_name', 'business_license', 
                          'address', 'city', 'state', 'zip_code']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            values.append(user_id)
            set_clause = ', '.join(update_fields)
            
            cursor.execute(f'''
                UPDATE users 
                SET {set_clause}, profile_completed = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Hash the new password
            new_password_hash = self.hash_password(new_password)
            
            # Update the password
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_password_hash, user_id))
            
            conn.commit()
            return cursor.rowcount > 0

    def get_all_users(self) -> List[Dict]:
        """Get a list of all users (excluding admin users)"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, role, account_status, first_name, last_name,
                    company_name, profile_completed, created_at, last_login
                FROM users
                WHERE role != 'admin'
                ORDER BY created_at DESC
            ''')

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_users_with_filters(
        self, 
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get users with filtering, search, and pagination"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the base query - exclude admin users
            base_query = '''
                SELECT id, username, email, role, account_status, first_name, last_name,
                    company_name, profile_completed, created_at, last_login
                FROM users
                WHERE role != 'admin'
            '''
            
            # Build count query for total - exclude admin users
            count_query = 'SELECT COUNT(*) FROM users WHERE role != \'admin\''
            
            params = []
            
            # Add search filter (name or email)
            if search:
                search_param = f'%{search}%'
                base_query += ' AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR username LIKE ?)'
                count_query += ' AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR username LIKE ?)'
                params.extend([search_param, search_param, search_param, search_param])
            
            # Add role filter (exclude admin from filter options)
            if role and role.lower() in ['contractor', 'estimator']:
                base_query += ' AND role = ?'
                count_query += ' AND role = ?'
                params.append(role.lower())
            
            # Add status filter
            if status and status.lower() in ['pending', 'approved', 'rejected', 'suspended']:
                base_query += ' AND account_status = ?'
                count_query += ' AND account_status = ?'
                params.append(status.lower())
            
            # Add ordering and pagination
            base_query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            
            # Get total count
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Get paginated results
            cursor.execute(base_query, params + [limit, offset])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            users = []
            for row in rows:
                user = dict(zip(columns, row))
                # Format the user data for the frontend
                formatted_user = {
                    'id': user['id'],
                    'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user['username'],
                    'email': user['email'],
                    'date': self._format_date(user['created_at']),
                    'role': user['role'].title(),
                    'status': user['account_status'].title(),
                    'profile_picture_url': None,  # Could be added later
                    'username': user['username'],
                    'company_name': user.get('company_name'),
                    'profile_completed': user.get('profile_completed', False),
                    'last_login': user.get('last_login')
                }
                users.append(formatted_user)
            
            return {
                'users': users,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(users) < total_count
            }
    
    def approve_user(self, user_id: int, approved_by: int) -> bool:
        """Approve a user account"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET account_status = 'approved', approved_by = ?, approved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND account_status = 'pending'
            ''', (approved_by, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def reject_user(self, user_id: int, rejected_by: int, rejection_reason: str = None) -> bool:
        """Reject a user account"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET account_status = 'rejected', approved_by = ?, approved_at = CURRENT_TIMESTAMP,
                    rejection_reason = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND account_status = 'pending'
            ''', (rejected_by, rejection_reason, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user account"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_pending_requests_count(self) -> int:
        """Get count of pending user signups waiting for approval"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE account_status = ?', ('pending',))
            return cursor.fetchone()[0]
    
    def get_active_users_count(self) -> int:
        """Get count of all approved users"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE account_status = ?', ('approved',))
            return cursor.fetchone()[0]
    
    def get_user_signups_by_date_range(self, start_date: str, end_date: str) -> Dict[str, int]:
        """Get total user signups by role within date range"""
        with self.auth_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total signups for contractors and estimators within date range
            cursor.execute('''
                SELECT 
                    role,
                    COUNT(*) as signup_count
                FROM users 
                WHERE created_at >= ? 
                AND created_at <= ? 
                AND role IN ('contractor', 'estimator')
                GROUP BY role
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            
            # Process the data into a simple format
            result = {'contractor': 0, 'estimator': 0}
            for row in rows:
                role, count = row
                result[role] = count
            
            return result