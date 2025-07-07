import json
import random
import string
from datetime import datetime, timedelta
import streamlit as st

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def generate_reset_token():
    """Generate a password reset token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def load_otps():
    """Load OTP data from JSON file"""
    try:
        with open("data/otps.json", 'r') as f:
            return json.load(f)
    except:
        return {}

def save_otps(otps):
    """Save OTP data to JSON file"""
    try:
        with open("data/otps.json", 'w') as f:
            json.dump(otps, f, indent=2)
        return True
    except:
        return False

def load_notifications():
    """Load notifications from JSON file"""
    try:
        with open("data/notifications.json", 'r') as f:
            return json.load(f)
    except:
        return []

def save_notifications(notifications):
    """Save notifications to JSON file"""
    try:
        with open("data/notifications.json", 'w') as f:
            json.dump(notifications, f, indent=2)
        return True
    except:
        return False

def send_email_notification(email, subject, message):
    """Store email notification locally (simulates sending email)"""
    notifications = load_notifications()
    
    notification = {
        'type': 'email',
        'recipient': email,
        'subject': subject,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'status': 'sent'
    }
    
    notifications.append(notification)
    return save_notifications(notifications)

def send_sms_notification(phone, message):
    """Store SMS notification locally (simulates sending SMS)"""
    notifications = load_notifications()
    
    notification = {
        'type': 'sms',
        'recipient': phone,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'status': 'sent'
    }
    
    notifications.append(notification)
    return save_notifications(notifications)

def store_otp(identifier, otp, purpose='registration'):
    """Store OTP for verification"""
    otps = load_otps()
    
    otp_data = {
        'otp': otp,
        'purpose': purpose,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat(),
        'verified': False
    }
    
    otps[identifier] = otp_data
    return save_otps(otps)

def verify_otp(identifier, entered_otp):
    """Verify OTP"""
    otps = load_otps()
    
    if identifier not in otps:
        return False
    
    otp_data = otps[identifier]
    current_time = datetime.now()
    expires_at = datetime.fromisoformat(otp_data['expires_at'])
    
    # Check if OTP is expired
    if current_time > expires_at:
        return False
    
    # Check if OTP matches
    if otp_data['otp'] == entered_otp:
        otps[identifier]['verified'] = True
        save_otps(otps)
        return True
    
    return False

def is_otp_verified(identifier):
    """Check if OTP is verified"""
    otps = load_otps()
    return otps.get(identifier, {}).get('verified', False)

def cleanup_expired_otps():
    """Remove expired OTPs"""
    otps = load_otps()
    current_time = datetime.now()
    
    expired_keys = []
    for identifier, otp_data in otps.items():
        expires_at = datetime.fromisoformat(otp_data['expires_at'])
        if current_time > expires_at:
            expired_keys.append(identifier)
    
    for key in expired_keys:
        del otps[key]
    
    if expired_keys:
        save_otps(otps)

def store_reset_token(email, token):
    """Store password reset token"""
    otps = load_otps()
    
    token_data = {
        'token': token,
        'purpose': 'password_reset',
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
        'used': False
    }
    
    otps[f"reset_{email}"] = token_data
    return save_otps(otps)

def verify_reset_token(email, token):
    """Verify password reset token"""
    otps = load_otps()
    identifier = f"reset_{email}"
    
    if identifier not in otps:
        return False
    
    token_data = otps[identifier]
    current_time = datetime.now()
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    
    # Check if token is expired or already used
    if current_time > expires_at or token_data['used']:
        return False
    
    # Check if token matches
    if token_data['token'] == token:
        otps[identifier]['used'] = True
        save_otps(otps)
        return True
    
    return False

def send_registration_email(email, username):
    """Send registration confirmation email"""
    subject = "Welcome to Blood Bank Management System"
    message = f"""
    Dear {username},

    Welcome to the Blood Bank Management System!

    Your account has been successfully created. You can now:
    - Donate blood and track your donations
    - Request blood when needed
    - Find nearby blood banks
    - View real-time blood inventory

    Thank you for joining our life-saving community!

    Best regards,
    Blood Bank Management Team
    """
    
    return send_email_notification(email, subject, message)

def send_password_reset_email(email, username, reset_token):
    """Send password reset email"""
    subject = "Password Reset Link - Blood Bank Management System"
    reset_link = f"https://bloodbank.replit.app/reset?token={reset_token}&email={email}"
    message = f"""
    Dear {username},

    You have requested to reset your password for the Blood Bank Management System.

    Please click the following link to reset your password:
    {reset_link}

    Or you can manually enter this reset token in the password reset form: {reset_token}

    This link and token will expire in 15 minutes. If you did not request this reset, please ignore this email.

    Best regards,
    Blood Bank Management Team
    """
    
    return send_email_notification(email, subject, message)

def get_user_notifications(email):
    """Get notifications for a specific user"""
    notifications = load_notifications()
    return [n for n in notifications if n['recipient'] == email]