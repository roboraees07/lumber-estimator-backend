# Admin User Management APIs

## Overview
This document describes the admin user management APIs that provide comprehensive user administration capabilities matching the interface shown in the image. These APIs allow admins to view, filter, search, and manage all users in the system.

## API Endpoints

### 1. Get All Users with Filtering
**Endpoint:** `GET /auth/users`

**Description:** Retrieve all users with advanced filtering, search, and pagination capabilities.

**Query Parameters:**
- `search` (optional): Search by user name or email
- `role` (optional): Filter by role (`admin`, `contractor`, `estimator`)
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`, `suspended`)
- `limit` (optional): Number of users per page (default: 100)
- `offset` (optional): Number of users to skip for pagination (default: 0)

**Headers:**
- `Authorization: Bearer <admin_token>`

**Example Request:**
```bash
GET /auth/users?search=john&role=contractor&status=pending&limit=50&offset=0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response:**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "id": 1,
        "user_name": "John Doe",
        "email": "john.doe@example.com",
        "date": "15 Jan. 2024",
        "role": "Contractor",
        "status": "Pending",
        "profile_picture_url": null,
        "username": "johndoe",
        "company_name": "Doe Construction",
        "profile_completed": false,
        "last_login": null
      },
      {
        "id": 2,
        "user_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "date": "14 Jan. 2024",
        "role": "Estimator",
        "status": "Approved",
        "profile_picture_url": null,
        "username": "janesmith",
        "company_name": "Smith Engineering",
        "profile_completed": true,
        "last_login": "2024-01-15T10:30:00"
      }
    ],
    "total_count": 12466,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### 2. Get User Details
**Endpoint:** `GET /auth/users/{user_id}`

**Description:** Get detailed information about a specific user.

**Path Parameters:**
- `user_id` (required): The ID of the user to retrieve

**Headers:**
- `Authorization: Bearer <admin_token>`

**Example Request:**
```bash
GET /auth/users/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response:**
```json
{
  "success": true,
  "message": "User details retrieved successfully",
  "data": {
    "id": 123,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "role": "Contractor",
    "status": "Pending",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-123-4567",
    "company_name": "Doe Construction",
    "business_license": "BL-12345-CA",
    "address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90210",
    "profile_completed": false,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "last_login": null,
    "approved_by": null,
    "approved_at": null,
    "rejection_reason": null
  }
}
```

### 3. User Action (Approve/Reject)
**Endpoint:** `PUT /auth/users/{user_id}/action`

**Description:** Approve or reject a pending user account.

**Path Parameters:**
- `user_id` (required): The ID of the user to approve or reject

**Request Body:**
```json
{
  "user_id": 123,
  "approved": true,
  "rejection_reason": "Optional reason for rejection (required when approved=false)"
}
```

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: application/json`

**Example Request - Approve User:**
```bash
PUT /auth/users/123/action
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "user_id": 123,
  "approved": true
}
```

**Example Request - Reject User:**
```bash
PUT /auth/users/123/action
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "user_id": 123,
  "approved": false,
  "rejection_reason": "Incomplete business license"
}
```

**Success Response - Approve:**
```json
{
  "success": true,
  "message": "User approved successfully",
  "data": {
    "user_id": 123,
    "status": "approved"
  }
}
```

**Success Response - Reject:**
```json
{
  "success": true,
  "message": "User rejected successfully",
  "data": {
    "user_id": 123,
    "status": "rejected",
    "rejection_reason": "Incomplete business license"
  }
}
```

### 4. Delete User
**Endpoint:** `DELETE /auth/users/{user_id}`

**Description:** Delete a user account permanently.

**Path Parameters:**
- `user_id` (required): The ID of the user to delete

**Headers:**
- `Authorization: Bearer <admin_token>`

**Example Request:**
```bash
DELETE /auth/users/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response:**
```json
{
  "success": true,
  "message": "User deleted successfully",
  "data": {
    "user_id": 123
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid parameters or cannot delete own account
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Non-admin user attempting admin operations
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server or database error

## Frontend Integration Examples

### JavaScript/TypeScript
```javascript
// Get users with filtering
const getUsers = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.role) params.append('role', filters.role);
  if (filters.status) params.append('status', filters.status);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  
  const response = await fetch(`/auth/users?${params}`, {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const result = await response.json();
  
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
};

// Approve user
const approveUser = async (userId) => {
  const response = await fetch(`/auth/users/${userId}/action`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      approved: true
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    showSuccessMessage('User approved successfully');
    refreshUserList();
  } else {
    showErrorMessage(result.message);
  }
};

// Reject user
const rejectUser = async (userId, reason) => {
  const response = await fetch(`/auth/users/${userId}/action`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      approved: false,
      rejection_reason: reason
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    showSuccessMessage('User rejected successfully');
    refreshUserList();
  } else {
    showErrorMessage(result.message);
  }
};

// Delete user
const deleteUser = async (userId) => {
  if (confirm('Are you sure you want to delete this user?')) {
    const response = await fetch(`/auth/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      showSuccessMessage('User deleted successfully');
      refreshUserList();
    } else {
      showErrorMessage(result.message);
    }
  }
};
```

### React Example
```jsx
import React, { useState, useEffect } from 'react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    role: '',
    status: '',
    limit: 100,
    offset: 0
  });
  const [totalCount, setTotalCount] = useState(0);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await fetch(`/auth/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setUsers(result.data.users);
        setTotalCount(result.data.total_count);
      } else {
        showError(result.message);
      }
    } catch (error) {
      showError('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId) => {
    try {
      const response = await fetch(`/auth/users/${userId}/action`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          approved: true
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        showSuccess('User approved successfully');
        fetchUsers(); // Refresh the list
      } else {
        showError(result.message);
      }
    } catch (error) {
      showError('Failed to approve user');
    }
  };

  const handleReject = async (userId, reason) => {
    try {
      const response = await fetch(`/auth/users/${userId}/action`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          approved: false,
          rejection_reason: reason
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        showSuccess('User rejected successfully');
        fetchUsers(); // Refresh the list
      } else {
        showError(result.message);
      }
    } catch (error) {
      showError('Failed to reject user');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const response = await fetch(`/auth/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          showSuccess('User deleted successfully');
          fetchUsers(); // Refresh the list
        } else {
          showError(result.message);
        }
      } catch (error) {
        showError('Failed to delete user');
      }
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [filters]);

  return (
    <div className="user-management">
      <h1>All Users ({totalCount})</h1>
      
      {/* Search and Filter Controls */}
      <div className="controls">
        <input
          type="text"
          placeholder="Search by Name or Email"
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
        />
        
        <select
          value={filters.role}
          onChange={(e) => setFilters({...filters, role: e.target.value})}
        >
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="contractor">Contractor</option>
          <option value="estimator">Estimator</option>
        </select>
        
        <select
          value={filters.status}
          onChange={(e) => setFilters({...filters, status: e.target.value})}
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>
      
      {/* User Table */}
      <table className="user-table">
        <thead>
          <tr>
            <th>User Name</th>
            <th>Email</th>
            <th>Date</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>
                <img src={user.profile_picture_url || '/default-avatar.png'} alt="Avatar" />
                {user.user_name}
              </td>
              <td>{user.email}</td>
              <td>{user.date}</td>
              <td>
                <span className={`role role-${user.role.toLowerCase()}`}>
                  {user.role}
                </span>
              </td>
              <td>
                <span className={`status status-${user.status.toLowerCase()}`}>
                  {user.status}
                </span>
              </td>
              <td>
                <button onClick={() => viewUserDetails(user.id)}>👁️</button>
                {user.status.toLowerCase() === 'pending' && (
                  <>
                    <button onClick={() => handleApprove(user.id)}>✅</button>
                    <button onClick={() => handleReject(user.id, 'Rejected by admin')}>❌</button>
                  </>
                )}
                <button onClick={() => handleDelete(user.id)}>🗑️</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Pagination */}
      <div className="pagination">
        <button 
          disabled={filters.offset === 0}
          onClick={() => setFilters({...filters, offset: Math.max(0, filters.offset - filters.limit)})}
        >
          ← Previous
        </button>
        <span>Page {Math.floor(filters.offset / filters.limit) + 1}</span>
        <button 
          disabled={!hasMore}
          onClick={() => setFilters({...filters, offset: filters.offset + filters.limit})}
        >
          Next →
        </button>
      </div>
    </div>
  );
};

export default UserManagement;
```

## Security Considerations

1. **Admin Authentication**: All endpoints require admin-level authentication
2. **Self-Protection**: Admins cannot delete their own accounts
3. **Input Validation**: All parameters are validated and sanitized
4. **SQL Injection Protection**: All queries use parameterized statements
5. **Rate Limiting**: Consider implementing rate limiting for admin operations

## Testing

Use the test script to verify all functionality:

```bash
python test_admin_user_apis.py
```

This will test:
- User filtering and search
- Pagination
- User management actions
- API response formats
- Error handling

