from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import requests
import uuid
from pathlib import Path
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db import crud, models, schemas
from db.crud import get_password_hash
from db.database import SessionLocal, engine

load_dotenv()

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# Frontend Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Backend Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_password_reset_email(email: str, reset_link: str):
    """Send password reset email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "BharatLaw AI - Password Reset Request"

        # Email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">BharatLaw AI</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Legal Excellence & Innovation</p>
            </div>

            <div style="background: #f8fafc; padding: 30px; border-radius: 10px; border-left: 4px solid #3b82f6;">
                <h2 style="color: #1e293b; margin-top: 0;">Password Reset Request</h2>
                <p style="color: #64748b; line-height: 1.6; margin-bottom: 20px;">
                    We received a request to reset your password for your BharatLaw AI account.
                    If you didn't make this request, you can safely ignore this email.
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}"
                       style="background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Reset Your Password
                    </a>
                </div>

                <p style="color: #64748b; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <strong>Security Notice:</strong> This link will expire in 1 hour for your security.
                    If the button doesn't work, copy and paste this link into your browser:
                </p>
                <p style="color: #475569; font-size: 12px; word-break: break-all; background: #f1f5f9; padding: 10px; border-radius: 4px;">
                    {reset_link}
                </p>
            </div>

            <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
                <p>If you have any questions, contact our support team.</p>
                <p style="margin-top: 10px;">
                    © 2025 BharatLaw AI. All rights reserved.<br>
                    <strong>⚖️ Not Legal Advice • Educational Use Only</strong>
                </p>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        text_body = f"""
        BharatLaw AI - Password Reset Request

        We received a request to reset your password. Click the link below to reset your password:

        {reset_link}

        This link will expire in 1 hour.

        If you didn't request this password reset, please ignore this email.

        © 2025 BharatLaw AI
        """

        # Attach parts
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Send email
        if SMTP_USERNAME and SMTP_PASSWORD:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, email, msg.as_string())
            server.quit()
            print(f"✅ Password reset email sent successfully to {email}")
            return True
        else:
            print(f"⚠️  Email configuration missing. Reset link for {email}: {reset_link}")
            return False

    except Exception as e:
        print(f"❌ Failed to send password reset email to {email}: {str(e)}")
        return False

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    # Add admin status based on email
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "phone_number": current_user.phone_number,
        "is_active": current_user.is_active,
        "email_verified": current_user.email_verified,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "is_admin": current_user.email == "aman2003sayyad@gmail.com",
        "role": "admin" if current_user.email == "aman2003sayyad@gmail.com" else "user"
    }
    return user_dict

@router.put("/users/me/", response_model=schemas.User)
def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.get("/users/me/stats")
def get_user_stats(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = crud.get_user_stats(db, current_user.id)
    return stats

# OAuth Endpoints
@router.get("/google")
async def google_login():
    """Redirect to Google OAuth"""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={API_BASE_URL}/auth/google/callback&"
        "scope=openid email profile&"
        "response_type=code&"
        "access_type=offline"
    )
    return RedirectResponse(google_auth_url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{API_BASE_URL}/auth/google/callback"
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if "error" in token_json:
        raise HTTPException(status_code=400, detail="OAuth authentication failed")

    # Get user info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token_json['access_token']}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_info = user_response.json()

    # Create or update user
    user = crud.get_user_by_email(db, email=user_info['email'])
    if not user:
        user = crud.create_oauth_user(db, {
            'email': user_info['email'],
            'full_name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'oauth_provider': 'google',
            'oauth_id': user_info['id']
        })

    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    # Redirect to frontend with token
    frontend_url = f"{FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(frontend_url, status_code=302)

# Password Reset Endpoints
from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If an account with this email exists, a password reset link has been sent."}

    # Create password reset token (expires in 1 hour)
    reset_token_expires = timedelta(hours=1)
    reset_token = create_access_token(
        data={"sub": user.email, "type": "password_reset"},
        expires_delta=reset_token_expires
    )

    # Generate reset link
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    # Send email
    email_sent = send_password_reset_email(request.email, reset_link)

    if email_sent:
        return {"message": "Password reset link has been sent to your email address."}
    else:
        # Fallback: show the link in response for development
        return {
            "message": "Password reset link generated. Check your email or use the link below:",
            "reset_link": reset_link,
            "note": "Email sending failed. Please configure SMTP settings in your environment variables."
        }

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if token_type != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Update password
        hashed_password = get_password_hash(request.new_password)
        user.hashed_password = hashed_password
        db.commit()

        return {"message": "Password has been reset successfully"}

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@router.post("/users/me/avatar")
async def upload_profile_avatar(
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and update user profile avatar"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.")

    # Validate file size (max 5MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    # Generate unique filename
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Use Railway Volume path
    uploads_dir = Path("/app/uploads/avatars")
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Save file to Railway Volume
        file_path = uploads_dir / unique_filename
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Generate avatar URL (accessible via Railway's static file serving)
        avatar_url = f"/uploads/avatars/{unique_filename}"

        # Update user in database
        updated_user = crud.update_user(db, current_user.id, {"avatar_url": avatar_url})

        if not updated_user:
            # Clean up uploaded file if database update fails
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail="Failed to update user profile")

        return updated_user

    except PermissionError as e:
        print(f"❌ PermissionError: {e}")
        print(f"   Uploads dir: {uploads_dir}")
        print(f"   Dir exists: {uploads_dir.exists()}")
        if uploads_dir.exists():
            print(f"   Dir permissions: {oct(uploads_dir.stat().st_mode)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Permission denied. Volume may not be properly mounted. Error: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/users/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not crud.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password (basic validation)
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")

    # Update password
    hashed_password = get_password_hash(request.new_password)
    user_update = {"hashed_password": hashed_password}
    updated_user = crud.update_user(db, current_user.id, user_update)

    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update password")

    return {"message": "Password changed successfully"}

@router.get("/users/me/download-data")
async def download_user_data(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download user data as JSON"""
    from fastapi.responses import JSONResponse

    # Get user conversations and messages
    conversations = crud.get_conversations(db, current_user.id)

    # Get user stats
    stats = crud.get_user_stats(db, current_user.id)

    # Prepare user data
    user_data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "bio": current_user.bio,
            "phone_number": current_user.phone_number,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        },
        "statistics": stats,
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "messages": [
                    {
                        "id": msg.id,
                        "type": msg.type,
                        "content": msg.content,
                        "source": msg.source,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    } for msg in crud.get_messages_for_conversation(db, conv.id)
                ]
            } for conv in conversations
        ]
    }

    # Return as downloadable JSON file
    return JSONResponse(
        content=user_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"
        }
    )

@router.delete("/users/me/delete-account")
async def delete_user_account(
    request: DeleteAccountRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account permanently"""
    # Verify password
    if not crud.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Password is incorrect")

    # Delete user (this will cascade delete conversations and messages)
    success = crud.delete_user(db, current_user.id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")

    return {"message": "Account deleted successfully"}

@router.get("/github")
async def github_login():
    """Redirect to GitHub OAuth"""
    github_auth_url = (
        "https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={API_BASE_URL}/auth/github/callback&"
        "scope=user:email&"
        "response_type=code"
    )
    return RedirectResponse(github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback with improved error handling for emails"""
    try:
        # Exchange code for access token
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{API_BASE_URL}/auth/github/callback"
        }
        # Ask for JSON response
        token_response = requests.post(token_url, data=token_data, headers={"Accept": "application/json"})
        token_json = token_response.json()
        print("GitHub token response:", token_json)

        access_token = token_json.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail=f"Failed to get access token: {token_json}")

        headers = {"Authorization": f"token {access_token}", "Accept": "application/vnd.github+json"}

        # Get primary user info (may include email if public)
        user_url = "https://api.github.com/user"
        user_response = requests.get(user_url, headers=headers)
        user_info = user_response.json()
        print("GitHub /user response:", user_info)

        # Try to fetch emails (preferred) - requires user:email scope for OAuth apps
        email_url = "https://api.github.com/user/emails"
        email_response = requests.get(email_url, headers=headers)
        emails = email_response.json()
        print("GitHub /user/emails response:", emails)

        primary_email = None

        # Handle a variety of responses
        if isinstance(emails, list) and emails:
            # prefer primary verified email
            primary_email = next((e.get("email") for e in emails if e.get("primary") and e.get("verified")), None)
            if not primary_email:
                # fallback to first verified email
                primary_email = next((e.get("email") for e in emails if e.get("verified")), emails[0].get("email"))
        elif isinstance(emails, dict):
            # Error from GitHub (e.g., Resource not accessible by integration)
            msg = emails.get("message")
            print("GitHub emails returned a dict with message:", msg)
            # If message indicates integration/403, fall back to user_info['email'] if present
            primary_email = user_info.get("email")
        else:
            # Unexpected format - fallback to user_info
            primary_email = user_info.get("email")

        # If we still don't have an email, give a helpful error
        if not primary_email:
            # Helpful error: suggest making email public or allow user:email scope
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not retrieve email from GitHub. "
                    "Possible reasons: user email is private, or the OAuth token lacks the user:email scope. "
                    "Ask the user to make their email public or ensure your GitHub OAuth app requests the user:email scope."
                ),
            )

        print(f"Using email: {primary_email}")

        # Create or update user
        user = crud.get_user_by_email(db, email=primary_email)
        if not user:
            user = crud.create_oauth_user(db, {
                'email': primary_email,
                'full_name': user_info.get('name') or user_info.get('login'),
                'avatar_url': user_info.get('avatar_url'),
                'oauth_provider': 'github',
                'oauth_id': str(user_info.get('id'))
            })

        # Create JWT token
        access_token_jwt = create_access_token(data={"sub": user.email})

        # Redirect to frontend with token
        frontend_url = f"{FRONTEND_URL}/auth/callback?token={access_token_jwt}"
        return RedirectResponse(frontend_url, status_code=302)

    except HTTPException:
        # Re-raise HTTPExceptions so FastAPI handles them
        raise
    except Exception as e:
        print(f"GitHub OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth processing failed: {str(e)}")

