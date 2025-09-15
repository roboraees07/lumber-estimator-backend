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
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..database.auth_models import AuthDatabaseManager, UserAuthManager, UserRole, AccountStatus

# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize database and auth manager
auth_db = AuthDatabaseManager()
auth_manager = UserAuthManager(auth_db)

# Simple in-memory OTP storage (in production, use Redis or database)
otp_storage = {}

# Email configuration (you should set these in environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@lumberestimator.com")

# Security scheme
security = HTTPBearer()

# Helper functions for OTP and email
def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "Password Reset OTP - Lumber Estimator"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You have requested to reset your password for your Lumber Estimator account.</p>
            <p>Your OTP code is: <strong style="font-size: 24px; color: #007bff;">{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you did not request this password reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Lumber Estimator Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        if SMTP_USERNAME and SMTP_PASSWORD and SMTP_USERNAME.strip() and SMTP_PASSWORD.strip():
            try:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                text = msg.as_string()
                server.sendmail(FROM_EMAIL, email, text)
                server.quit()
                print(f"OTP email sent successfully to {email}")
                return True
            except Exception as smtp_error:
                print(f"SMTP Error: {str(smtp_error)}")
                # Fall through to development mode
        else:
            print(f"SMTP credentials not configured, using development mode")
        
        # For development/testing - just print the OTP
        print(f"=== DEVELOPMENT MODE ===")
        print(f"OTP for {email}: {otp}")
        print(f"========================")
        return True
            
    except Exception as e:
        print(f"Error in send_otp_email: {str(e)}")
        return False

def store_otp(email: str, otp: str):
    """Store OTP with expiration time"""
    otp_storage[email] = {
        'otp': otp,
        'expires_at': datetime.now() + timedelta(minutes=10),
        'attempts': 0
    }

def verify_otp(email: str, provided_otp: str) -> bool:
    """Verify OTP and check expiration"""
    if email not in otp_storage:
        return False
    
    stored_data = otp_storage[email]
    
    # Check if OTP has expired
    if datetime.now() > stored_data['expires_at']:
        del otp_storage[email]
        return False
    
    # Check attempts limit
    if stored_data['attempts'] >= 3:
        del otp_storage[email]
        return False
    
    # Increment attempts
    stored_data['attempts'] += 1
    
    # Verify OTP
    if stored_data['otp'] == provided_otp:
        del otp_storage[email]  # Remove OTP after successful verification
        return True
    
    return False

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
    username: Optional[str] = None
    email: Optional[EmailStr] = None
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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
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
            detail="Pending Approval"
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
    """Update current user's profile including username and email"""
    try:
        user_id = current_user['id']
        update_data = profile_data.dict(exclude_unset=True)
        
        # Check if username or email is being changed
        if 'username' in update_data or 'email' in update_data:
            # Check for uniqueness of username and email
            if 'username' in update_data:
                existing_user = auth_manager.get_user_by_username(update_data['username'])
                if existing_user and existing_user['id'] != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already exists"
                    )
            
            if 'email' in update_data:
                existing_user = auth_manager.get_user_by_email(update_data['email'])
                if existing_user and existing_user['id'] != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
        
        # Update the profile
        success = auth_manager.update_user_profile(user_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

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

@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(request: ForgotPasswordRequest):
    """Send OTP to email for password reset"""
    try:
        # Check if user exists with this email
        user = auth_manager.get_user_by_email(request.email)
        if not user:
            # Only send OTP if email is registered
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email address"
            )
        
        # Generate and store OTP
        otp = generate_otp()
        store_otp(request.email, otp)
        
        # Send OTP via email
        email_sent = send_otp_email(request.email, otp)
        
        if email_sent:
            return {
                "success": True,
                "message": "OTP sent to your email address"
            }
        else:
            # If email sending fails, still return success but mention the OTP
            return {
                "success": True,
                "message": f"OTP generated: {otp}. Please check your email or contact support if you don't receive it."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process forgot password request: {str(e)}"
        )

@router.post("/verify-otp", response_model=Dict[str, Any])
async def verify_otp_endpoint(request: VerifyOTPRequest):
    """Verify OTP for password reset"""
    try:
        is_valid = verify_otp(request.email, request.otp)
        
        if is_valid:
            return {
                "success": True,
                "message": "OTP verified successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )

@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(request: ResetPasswordRequest):
    """Reset password for user"""
    try:
        # Validate password confirmation
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Validate password strength (basic validation)
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Get user by email
        user = auth_manager.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        success = auth_manager.update_password(user['id'], request.new_password)
        
        if success:
            return {
                "success": True,
                "message": "Password reset successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
