import json
import hashlib
import streamlit as st
from datetime import datetime

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
    """Register a new user"""
    users = load_users()
    
    # Check if username already exists
    if any(user['username'] == username for user in users):
        return False
    
    # Create new user
    new_user = {
        'username': username,
        'email': email,
        'phone': phone,
        'password': hash_password(password),
        'user_type': user_type,
        'registration_date': datetime.now().isoformat(),
        'blood_group': blood_group,
        'age': age
    }
    
    users.append(new_user)
    return save_users(users)

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
