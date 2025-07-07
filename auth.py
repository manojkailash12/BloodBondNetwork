import json
import hashlib
import streamlit as st
from datetime import datetime
from notifications import (
    generate_otp, send_sms_notification, store_otp, verify_otp, 
    is_otp_verified, send_registration_email, generate_reset_token,
    store_reset_token, send_password_reset_email, verify_reset_token
)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    try:
        with open("data/users.json", 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    """Save users to JSON file"""
    try:
        with open("data/users.json", 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except:
        return False

def register_user(username, email, phone, password, user_type, blood_group=None, age=None):
    """Register a new user with OTP verification"""
    users = load_users()
    
    # Check if username or email already exists
    if any(user['username'] == username for user in users):
        return {'success': False, 'error': 'Username already exists'}
    
    if any(user['email'] == email for user in users):
        return {'success': False, 'error': 'Email already registered'}
    
    # No OTP verification required during registration
    
    # Create new user
    new_user = {
        'username': username,
        'email': email,
        'phone': phone,
        'password': hash_password(password),
        'user_type': user_type,
        'registration_date': datetime.now().isoformat(),
        'blood_group': blood_group,
        'age': age,
        'email_verified': False,
        'phone_verified': False
    }
    
    users.append(new_user)
    success = save_users(users)
    
    if success:
        # Send registration confirmation email
        send_registration_email(email, username)
        return {'success': True, 'message': 'Registration successful'}
    else:
        return {'success': False, 'error': 'Failed to save user data'}

def send_email_otp(email):
    """Send OTP to email"""
    otp = generate_otp()
    
    # Store OTP
    if store_otp(f"email_{email}", otp, 'email_verification'):
        # Simulate sending email (in real app, this would use SendGrid)
        subject = "Email Verification - Blood Bank System"
        message = f"Your email verification OTP is: {otp}. This OTP will expire in 10 minutes."
        
        # Store the "sent" email notification
        from notifications import send_email_notification
        send_email_notification(email, subject, message)
        
        return {'success': True, 'otp': otp}  # In real app, don't return OTP
    
    return {'success': False, 'error': 'Failed to generate OTP'}

def send_phone_otp(phone):
    """Send OTP to phone"""
    otp = generate_otp()
    
    # Store OTP
    if store_otp(f"phone_{phone}", otp, 'phone_verification'):
        # Simulate sending SMS (in real app, this would use Twilio)
        message = f"Your phone verification OTP is: {otp}. This OTP will expire in 10 minutes."
        
        # Store the "sent" SMS notification
        send_sms_notification(phone, message)
        
        return {'success': True, 'otp': otp}  # In real app, don't return OTP
    
    return {'success': False, 'error': 'Failed to generate OTP'}

def verify_email_otp(email, otp):
    """Verify email OTP"""
    return verify_otp(f"email_{email}", otp)

def verify_phone_otp(phone, otp):
    """Verify phone OTP"""
    return verify_otp(f"phone_{phone}", otp)

def initiate_password_reset(email):
    """Initiate password reset process"""
    users = load_users()
    
    # Check if email exists
    user = None
    for u in users:
        if u['email'] == email:
            user = u
            break
    
    if not user:
        return {'success': False, 'error': 'Email not found'}
    
    # Generate reset token
    reset_token = generate_reset_token()
    
    # Store reset token
    if store_reset_token(email, reset_token):
        # Send reset email with link
        send_password_reset_email(email, user['username'], reset_token)
        return {'success': True, 'message': 'Password reset link sent to your email', 'token': reset_token}
    
    return {'success': False, 'error': 'Failed to initiate password reset'}

def reset_password(email, token, new_password):
    """Reset password using token"""
    if not verify_reset_token(email, token):
        return {'success': False, 'error': 'Invalid or expired reset token'}
    
    users = load_users()
    
    # Find and update user password
    for user in users:
        if user['email'] == email:
            user['password'] = hash_password(new_password)
            if save_users(users):
                return {'success': True, 'message': 'Password reset successfully'}
            else:
                return {'success': False, 'error': 'Failed to update password'}
    
    return {'success': False, 'error': 'User not found'}

def change_password(username, current_password, new_password):
    """Change password with current password verification"""
    users = load_users()
    
    # Find user and verify current password
    for user in users:
        if user['username'] == username:
            if user['password'] == hash_password(current_password):
                user['password'] = hash_password(new_password)
                if save_users(users):
                    return {'success': True, 'message': 'Password changed successfully'}
                else:
                    return {'success': False, 'error': 'Failed to update password'}
            else:
                return {'success': False, 'error': 'Current password is incorrect'}
    
    return {'success': False, 'error': 'User not found'}

def login_user(username, password, user_type):
    """Authenticate user login"""
    users = load_users()
    hashed_password = hash_password(password)
    
    for user in users:
        if (user['username'] == username and 
            user['password'] == hashed_password and 
            user['user_type'] == user_type):
            
            # Update session state
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_type = user_type
            return True
    
    return False

def logout_user():
    """Log out current user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_type = None

def get_user_info(username):
    """Get user information"""
    users = load_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

def get_total_users():
    """Get total number of registered users"""
    users = load_users()
    return len(users)

def get_users_by_type(user_type):
    """Get users by type (donor/receiver)"""
    users = load_users()
    return [user for user in users if user['user_type'] == user_type]
