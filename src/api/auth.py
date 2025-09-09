#!/usr/bin/env python3
"""
Authentication API Endpoints for Lumber Estimator
Handles user registration, login, and account approval
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import os

from ..database.auth_models import AuthDatabaseManager, UserAuthManager, UserRole, AccountStatus

# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize database and auth manager
auth_db = AuthDatabaseManager()
auth_manager = UserAuthManager(auth_db)

# Security scheme
security = HTTPBearer()

# Pydantic models for request/response
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    business_license: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    business_license: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class UserApprovalRequest(BaseModel):
    user_id: int
    approved: bool
    rejection_reason: Optional[str] = None

class QuotationApprovalRequest(BaseModel):
    quotation_id: int
    approved: bool
    rejection_reason: Optional[str] = None

class ProjectActionRequest(BaseModel):
    project_id: int
    approved: bool
    rejection_reason: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    new_password: str
    confirm_password: str

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = auth_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_manager.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Dependency to check if user is admin
async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Check if current user is admin"""
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dependency to check if user is contractor
async def get_contractor_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Check if current user is contractor"""
    if current_user['role'] != 'contractor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contractor access required"
        )
    return current_user

# Dependency to check if user is estimator
async def get_estimator_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Check if current user is estimator"""
    if current_user['role'] != 'estimator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Estimator access required"
        )
    return current_user

@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserRegistration):
    """Register new user account"""
    try:
        # Validate role restrictions
        if user_data.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin accounts cannot be created via registration"
            )
        
        # Create user
        user_id = auth_manager.create_user(user_data.dict())
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "status": "pending_approval" if user_data.role != UserRole.ADMIN else "approved",
            "note": "Your account is pending admin approval" if user_data.role != UserRole.ADMIN else "Account created successfully"
        }
    
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    # This function now correctly returns user data if the password is valid
    user = auth_manager.authenticate_user(login_data.username, login_data.password)
    
    # Case 1: User is None (means username not found or password was wrong)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )
    
    # Case 2: User exists and password is correct, but account is not approved
    if user['account_status'] != 'approved':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user['account_status']}. Please wait for admin approval."
        )
    
    # Case 3: Success! User exists, password is correct, and account is approved
    access_token = auth_manager.generate_jwt_token(user)
    
    return LoginResponse(
        access_token=access_token,
        user=user
    )

@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user's profile"""
    success = auth_manager.update_user_profile(current_user['id'], profile_data.dict(exclude_unset=True))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    return {"message": "Profile updated successfully"}

@router.put("/change-password", response_model=Dict[str, Any])
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change current user's password"""
    try:
        # Validate new password length
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )
        
        # Check if passwords match
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password do not match"
            )
        
        # Update password using user ID from token
        success = auth_manager.update_password(current_user['id'], password_data.new_password)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        message = "Your password has been updated successfully"
        
        return {
            "success": True,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password update failed: {str(e)}"
        )


@router.get("/pending-approvals", response_model=List[Dict[str, Any]])
async def get_pending_approvals(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """Get list of users pending approval (Admin only)"""
    return auth_manager.get_pending_approvals()

@router.post("/approve-user", response_model=Dict[str, Any])
async def approve_user_account(
    approval_request: UserApprovalRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Approve or reject user account (Admin only)"""
    if approval_request.approved:
        success = auth_manager.approve_user(approval_request.user_id, admin_user['id'])
        message = "User approved successfully"
    else:
        if not approval_request.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required when rejecting a user"
            )
        success = auth_manager.approve_user(approval_request.user_id, admin_user['id'], approval_request.rejection_reason)
        message = "User rejected successfully"
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process approval request"
        )
    
    return {"message": message}

# Previouis onely planned but not implemented endpoint
# @router.get("/users", response_model=List[Dict[str, Any]])
# async def get_all_users(admin_user: Dict[str, Any] = Depends(get_admin_user)):
#     """Get all users (Admin only)"""
#     # This would need to be implemented in the auth manager
#     # For now, return a placeholder
#     return {"message": "User list endpoint - to be implemented"}
@router.get("/users", response_model=Dict[str, Any])
async def get_all_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Get all users with filtering and pagination (Admin only) - excludes admin users"""
    try:
        result = auth_manager.get_users_with_filters(
            search=search,
            role=role,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "message": "Users retrieved successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user_details(
    user_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Get detailed information about a specific user (Admin only)"""
    try:
        user = auth_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Format user data for admin view
        formatted_user = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'].title(),
            'status': user['account_status'].title(),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'phone': user.get('phone'),
            'company_name': user.get('company_name'),
            'business_license': user.get('business_license'),
            'address': user.get('address'),
            'city': user.get('city'),
            'state': user.get('state'),
            'zip_code': user.get('zip_code'),
            'profile_completed': user.get('profile_completed', False),
            'created_at': user['created_at'],
            'updated_at': user.get('updated_at'),
            'last_login': user.get('last_login'),
            'approved_by': user.get('approved_by'),
            'approved_at': user.get('approved_at'),
            'rejection_reason': user.get('rejection_reason')
        }
        
        return {
            "success": True,
            "message": "User details retrieved successfully",
            "data": formatted_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/action", response_model=Dict[str, Any])
async def user_action(
    user_id: int,
    action_request: UserApprovalRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Approve or reject a user account (Admin only)"""
    try:
        if action_request.user_id != user_id:
            raise HTTPException(status_code=400, detail="User ID in URL and request body must match")
        
        # Determine action and validate rejection reason if needed
        action = "approve" if action_request.approved else "reject"
        
        if action == "reject" and not action_request.rejection_reason:
            raise HTTPException(
                status_code=400, 
                detail="Rejection reason is required when rejecting a user"
            )
        
        # Update user status
        success = auth_manager.update_user_status(
            user_id, 
            admin_user['id'], 
            action, 
            action_request.rejection_reason
        )
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="User not found or already processed"
            )
        
        # Return appropriate response
        if action == "approve":
            return {
                "success": True,
                "message": "User approved successfully",
                "data": {"user_id": user_id, "status": "approved"}
            }
        else:
            return {
                "success": True,
                "message": "User rejected successfully",
                "data": {
                    "user_id": user_id, 
                    "status": "rejected", 
                    "rejection_reason": action_request.rejection_reason
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}", response_model=Dict[str, Any])
async def delete_user(
    user_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete a user account (Admin only)"""
    try:
        # Prevent admin from deleting themselves
        if user_id == admin_user['id']:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        success = auth_manager.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": "User deleted successfully",
            "data": {"user_id": user_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", response_model=Dict[str, Any])
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (invalidate token)"""
    # In a production system, you'd add the token to a blacklist
    # For now, just return success
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return current_user
