import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Import custom modules
from auth import (
    login_user, logout_user, send_email_otp, send_phone_otp, 
    verify_email_otp, verify_phone_otp, register_user,
    initiate_password_reset, reset_password, change_password
)
from blood_management import donate_blood, request_blood, get_blood_inventory
from dashboard import show_dashboard
from maps import show_blood_bank_map
import base64

# Initialize data directories
def init_data_dirs():
    os.makedirs("data", exist_ok=True)
    
    # Initialize empty data files if they don't exist
    files = [
        "data/users.json",
        "data/blood_inventory.json", 
        "data/donations.json",
        "data/requests.json",
        "data/blood_banks.json",
        "data/otps.json",
        "data/notifications.json",
        "data/request_responses.json"
    ]
    
    for file_path in files:
        if not os.path.exists(file_path):
            if "blood_banks.json" in file_path:
                # Initialize with some sample blood bank locations
                sample_data = [
                    {"name": "City Blood Bank", "lat": 28.6139, "lng": 77.2090, "address": "Delhi, India", "contact": "+91-9876543210"},
                    {"name": "Central Hospital Blood Bank", "lat": 19.0760, "lng": 72.8777, "address": "Mumbai, India", "contact": "+91-9876543211"},
                    {"name": "Metro Blood Center", "lat": 12.9716, "lng": 77.5946, "address": "Bangalore, India", "contact": "+91-9876543212"},
                    {"name": "Regional Blood Bank", "lat": 13.0827, "lng": 80.2707, "address": "Chennai, India", "contact": "+91-9876543213"}
                ]
            elif "blood_inventory.json" in file_path:
                # Initialize blood inventory
                sample_data = {
                    "A+": 0, "A-": 0, "B+": 0, "B-": 0,
                    "AB+": 0, "AB-": 0, "O+": 0, "O-": 0
                }
            elif "otps.json" in file_path:
                sample_data = {}
            elif "notifications.json" in file_path or "request_responses.json" in file_path:
                sample_data = []
            else:
                sample_data = []
            
            with open(file_path, 'w') as f:
                json.dump(sample_data, f, indent=2)

def get_base64_svg(svg_file):
    """Convert SVG to base64 for embedding"""
    try:
        with open(svg_file, "r") as f:
            svg_content = f.read()
        return base64.b64encode(svg_content.encode()).decode()
    except:
        return None

def add_bg_from_local(svg_file):
    """Add background from local SVG file"""
    svg_base64 = get_base64_svg(svg_file)
    if svg_base64:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/svg+xml;base64,{svg_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .main .block-container {{
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                padding: 2rem;
                margin-top: 1rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .sidebar .sidebar-content {{
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

def main():
    st.set_page_config(
        page_title="Blood Bank Management System",
        page_icon="🩸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add background
    add_bg_from_local("static/background.svg")
    
    # Initialize data
    init_data_dirs()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email_verified' not in st.session_state:
        st.session_state.email_verified = False
    if 'phone_verified' not in st.session_state:
        st.session_state.phone_verified = False
    if 'registration_data' not in st.session_state:
        st.session_state.registration_data = {}
    
    # Main header
    st.title("🩸 Blood Bank Management System")
    st.markdown("---")
    
    # Sidebar navigation
    if st.session_state.logged_in:
        st.sidebar.success(f"Welcome, {st.session_state.username}!")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_type.title()}")
        
        if st.sidebar.button("Logout"):
            logout_user()
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Navigation menu
        if st.session_state.user_type == "donor":
            menu_options = ["Dashboard", "Donate Blood", "Blood Requests", "Blood Bank Map", "My Donations", "My Notifications", "Change Password"]
        elif st.session_state.user_type == "receiver":
            menu_options = ["Dashboard", "Request Blood", "Blood Bank Map", "My Requests", "Request Responses", "My Notifications", "Change Password"]
        else:
            menu_options = ["Dashboard", "Blood Bank Map", "My Notifications", "Change Password"]
            
        selected_page = st.sidebar.selectbox("Navigation", menu_options)
        
        # Main content area
        if selected_page == "Dashboard":
            show_dashboard()
        elif selected_page == "Donate Blood":
            donate_blood_page()
        elif selected_page == "Request Blood":
            request_blood_page()
        elif selected_page == "Blood Requests":
            show_blood_requests_for_donor()
        elif selected_page == "Request Responses":
            show_request_responses()
        elif selected_page == "Blood Bank Map":
            show_blood_bank_map()
        elif selected_page == "My Donations":
            show_my_donations()
        elif selected_page == "My Requests":
            show_my_requests()
        elif selected_page == "My Notifications":
            show_my_notifications()
        elif selected_page == "Change Password":
            change_password_page()
    else:
        # Login/Register interface
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["Login", "Register", "Forgot Password"])
        
        with auth_tab1:
            login_form()
        
        with auth_tab2:
            register_form()
        
        with auth_tab3:
            forgot_password_form()

def login_form():
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        user_type = st.selectbox("I am a:", ["donor", "receiver"])
        
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username and password:
                if login_user(username, password, user_type):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials or user type mismatch.")
            else:
                st.error("Please fill in all fields.")

def register_form():
    st.subheader("Create New Account")
    
    # Step 1: Basic Information
    if 'registration_step' not in st.session_state:
        st.session_state.registration_step = 1
    
    if st.session_state.registration_step == 1:
        st.markdown("### Step 1: Basic Information")
        
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
                
            with col2:
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                user_type = st.selectbox("I want to:", ["donor", "receiver"])
            
            # Additional fields for donors
            if user_type == "donor":
                st.markdown("**Additional Information for Donors:**")
                col3, col4 = st.columns(2)
                with col3:
                    blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                with col4:
                    age = st.number_input("Age", min_value=18, max_value=65, value=25)
            else:
                blood_group = None
                age = None
            
            submitted = st.form_submit_button("Proceed to Verification")
            
            if submitted:
                if username and email and phone and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        # Store registration data
                        st.session_state.registration_data = {
                            'username': username,
                            'email': email,
                            'phone': phone,
                            'password': password,
                            'user_type': user_type,
                            'blood_group': blood_group,
                            'age': age
                        }
                        st.session_state.registration_step = 2
                        st.rerun()
                else:
                    st.error("Please fill in all required fields.")
    
    elif st.session_state.registration_step == 2:
        st.markdown("### Step 2: Email Verification")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Send Email OTP"):
                result = send_email_otp(st.session_state.registration_data['email'])
                if result['success']:
                    st.success(f"OTP sent to {st.session_state.registration_data['email']}")
                    st.info(f"For demo purposes, your OTP is: **{result['otp']}**")
                else:
                    st.error(result['error'])
            
            email_otp = st.text_input("Enter Email OTP", max_chars=6)
            
            if st.button("Verify Email"):
                if email_otp:
                    if verify_email_otp(st.session_state.registration_data['email'], email_otp):
                        st.success("Email verified successfully!")
                        st.session_state.email_verified = True
                        st.session_state.registration_step = 3
                        st.rerun()
                    else:
                        st.error("Invalid or expired OTP.")
                else:
                    st.error("Please enter the OTP.")
        
        with col2:
            st.info(f"**Email:** {st.session_state.registration_data['email']}")
            if st.session_state.email_verified:
                st.success("✅ Email Verified")
    
    elif st.session_state.registration_step == 3:
        st.markdown("### Step 3: Phone Verification")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Send SMS OTP"):
                result = send_phone_otp(st.session_state.registration_data['phone'])
                if result['success']:
                    st.success(f"OTP sent to {st.session_state.registration_data['phone']}")
                    st.info(f"For demo purposes, your OTP is: **{result['otp']}**")
                else:
                    st.error(result['error'])
            
            phone_otp = st.text_input("Enter SMS OTP", max_chars=6)
            
            if st.button("Verify Phone"):
                if phone_otp:
                    if verify_phone_otp(st.session_state.registration_data['phone'], phone_otp):
                        st.success("Phone verified successfully!")
                        st.session_state.phone_verified = True
                        st.session_state.registration_step = 4
                        st.rerun()
                    else:
                        st.error("Invalid or expired OTP.")
                else:
                    st.error("Please enter the OTP.")
        
        with col2:
            st.info(f"**Phone:** {st.session_state.registration_data['phone']}")
            if st.session_state.phone_verified:
                st.success("✅ Phone Verified")
    
    elif st.session_state.registration_step == 4:
        st.markdown("### Step 4: Complete Registration")
        
        st.success("All verifications complete! Ready to create your account.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Email:** ✅ Verified")
            st.info("**Phone:** ✅ Verified")
        
        with col2:
            st.info(f"**Username:** {st.session_state.registration_data['username']}")
            st.info(f"**Type:** {st.session_state.registration_data['user_type'].title()}")
        
        if st.button("Create Account", type="primary"):
            data = st.session_state.registration_data
            result = register_user(
                data['username'], data['email'], data['phone'], 
                data['password'], data['user_type'], 
                data['blood_group'], data['age']
            )
            
            if result['success']:
                st.success("🎉 Registration successful! Please login to continue.")
                st.balloons()
                # Reset registration state
                st.session_state.registration_step = 1
                st.session_state.registration_data = {}
                st.session_state.email_verified = False
                st.session_state.phone_verified = False
            else:
                st.error(f"Registration failed: {result['error']}")
    
    # Reset button
    if st.session_state.registration_step > 1:
        if st.button("Start Over"):
            st.session_state.registration_step = 1
            st.session_state.registration_data = {}
            st.session_state.email_verified = False
            st.session_state.phone_verified = False
            st.rerun()

def forgot_password_form():
    st.subheader("Reset Your Password")
    
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1
    
    if st.session_state.reset_step == 1:
        st.markdown("### Step 1: Enter Email")
        
        with st.form("email_form"):
            email = st.text_input("Enter your registered email address")
            submitted = st.form_submit_button("Send Reset Instructions")
            
            if submitted:
                if email:
                    result = initiate_password_reset(email)
                    if result['success']:
                        st.success(result['message'])
                        st.session_state.reset_email = email
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error(result['error'])
                else:
                    st.error("Please enter your email address.")
    
    elif st.session_state.reset_step == 2:
        st.markdown("### Step 2: Enter Reset Token")
        st.info(f"Reset instructions sent to: {st.session_state.reset_email}")
        
        with st.form("reset_form"):
            token = st.text_input("Enter Reset Token")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submitted = st.form_submit_button("Reset Password")
            
            if submitted:
                if token and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        result = reset_password(st.session_state.reset_email, token, new_password)
                        if result['success']:
                            st.success(result['message'])
                            st.balloons()
                            # Reset state
                            st.session_state.reset_step = 1
                            if 'reset_email' in st.session_state:
                                del st.session_state.reset_email
                        else:
                            st.error(result['error'])
                else:
                    st.error("Please fill in all fields.")
        
        # Show demo token for testing
        from notifications import load_otps
        otps = load_otps()
        reset_key = f"reset_{st.session_state.reset_email}"
        if reset_key in otps:
            st.info(f"For demo purposes, your reset token is: **{otps[reset_key]['token']}**")
    
    if st.session_state.reset_step > 1:
        if st.button("Back to Email Entry"):
            st.session_state.reset_step = 1
            if 'reset_email' in st.session_state:
                del st.session_state.reset_email
            st.rerun()

def change_password_page():
    st.header("🔒 Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Change Password")
        
        if submitted:
            if current_password and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("New passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif current_password == new_password:
                    st.error("New password must be different from current password.")
                else:
                    result = change_password(st.session_state.username, current_password, new_password)
                    if result['success']:
                        st.success(result['message'])
                        st.balloons()
                    else:
                        st.error(result['error'])
            else:
                st.error("Please fill in all fields.")
    
    st.markdown("---")
    st.markdown("### Password Security Tips")
    st.markdown("""
    - Use at least 8 characters
    - Include uppercase and lowercase letters
    - Include numbers and special characters
    - Don't use personal information
    - Don't reuse passwords from other sites
    """)

def show_my_notifications():
    st.header("📬 My Notifications")
    
    # Get user email for notifications
    from auth import get_user_info
    user_info = get_user_info(st.session_state.username)
    
    if not user_info:
        st.error("Could not retrieve user information.")
        return
    
    # Get notifications for this user
    from notifications import get_user_notifications
    notifications = get_user_notifications(user_info['email'])
    
    if notifications:
        # Sort by timestamp, most recent first
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Display notifications
        for i, notification in enumerate(notifications):
            with st.expander(f"{notification['type'].upper()}: {notification['subject']}" if notification['type'] == 'email' else f"SMS: {notification['message'][:50]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if notification['type'] == 'email':
                        st.markdown(f"**To:** {notification['recipient']}")
                        st.markdown(f"**Subject:** {notification['subject']}")
                        st.markdown("**Message:**")
                        st.text(notification['message'])
                    else:  # SMS
                        st.markdown(f"**To:** {notification['recipient']}")
                        st.markdown("**Message:**")
                        st.text(notification['message'])
                
                with col2:
                    timestamp = datetime.fromisoformat(notification['timestamp'])
                    st.markdown(f"**Date:** {timestamp.strftime('%Y-%m-%d')}")
                    st.markdown(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
                    st.markdown(f"**Status:** ✅ {notification['status'].title()}")
        
        # Summary
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            email_count = len([n for n in notifications if n['type'] == 'email'])
            st.metric("Total Emails", email_count)
        with col2:
            sms_count = len([n for n in notifications if n['type'] == 'sms'])
            st.metric("Total SMS", sms_count)
        with col3:
            st.metric("Total Notifications", len(notifications))
    
    else:
        st.info("No notifications yet.")
        st.markdown("""
        **You will receive notifications for:**
        - Registration confirmation
        - Password reset requests  
        - OTP verification codes
        - Important system updates
        """)

def show_blood_requests_for_donor():
    """Show blood requests that the donor can fulfill"""
    st.header("🩸 Blood Requests You Can Help With")
    
    from request_management import get_pending_requests_for_donor, respond_to_request
    
    # Get compatible requests for this donor
    compatible_requests = get_pending_requests_for_donor(st.session_state.username)
    
    if compatible_requests:
        st.success(f"Found {len(compatible_requests)} blood requests you can help with!")
        
        for i, request in enumerate(compatible_requests):
            with st.expander(f"Request #{request.get('id', i+1)} - {request['blood_group']} - {request['urgency']} Priority"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Blood Group:** {request['blood_group']}")
                    st.markdown(f"**Quantity Needed:** {request['quantity']} ml")
                    st.markdown(f"**Urgency:** {request['urgency']}")
                    st.markdown(f"**Required By:** {request['required_date']}")
                    st.markdown(f"**Reason:** {request['reason']}")
                    st.markdown(f"**Requester:** {request['requester']}")
                    
                    request_date = datetime.fromisoformat(request['date'])
                    st.markdown(f"**Request Date:** {request_date.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    urgency_colors = {
                        'Low': '🟢',
                        'Medium': '🟡', 
                        'High': '🟠',
                        'Critical': '🔴'
                    }
                    urgency_icon = urgency_colors.get(request['urgency'], '⚪')
                    st.markdown(f"## {urgency_icon}")
                    st.markdown(f"**Priority:** {request['urgency']}")
                
                st.markdown("---")
                
                # Response form
                with st.form(f"response_form_{request.get('id', i)}"):
                    st.markdown("### Your Response:")
                    
                    response_type = st.radio("Your Decision:", ["accept", "decline"], key=f"response_{i}")
                    
                    if response_type == "accept":
                        quantity_offered = st.number_input(
                            "Quantity you can donate (ml):", 
                            min_value=100, 
                            max_value=request['quantity'], 
                            value=min(350, request['quantity']),
                            step=50,
                            key=f"quantity_{i}"
                        )
                    else:
                        quantity_offered = 0
                    
                    message = st.text_area("Message to requester (optional):", key=f"message_{i}")
                    
                    submitted = st.form_submit_button("Submit Response")
                    
                    if submitted:
                        result = respond_to_request(
                            request.get('id'), 
                            st.session_state.username, 
                            response_type, 
                            message, 
                            quantity_offered
                        )
                        
                        if result:
                            if response_type == "accept":
                                st.success("Thank you for accepting! The requester has been notified.")
                                st.balloons()
                            else:
                                st.info("Your response has been recorded. The requester has been notified.")
                            st.rerun()
                        else:
                            st.error("Failed to submit response. Please try again.")
    else:
        st.info("No blood requests match your blood group at this time.")
        st.markdown("""
        **When new requests come in that match your blood group, you will:**
        - Receive email notifications
        - Receive SMS alerts
        - See them listed here
        
        Thank you for being a registered donor! 🙏
        """)

def show_request_responses():
    """Show responses received for requester's blood requests"""
    st.header("📬 Responses to Your Blood Requests")
    
    from request_management import get_requester_notifications
    
    # Get all responses for this requester
    responses = get_requester_notifications(st.session_state.username)
    
    if responses:
        # Group responses by request
        requests_dict = {}
        for response in responses:
            request_id = response['request_details'].get('id')
            if request_id not in requests_dict:
                requests_dict[request_id] = {
                    'request': response['request_details'],
                    'responses': []
                }
            requests_dict[request_id]['responses'].append(response)
        
        for request_id, data in requests_dict.items():
            request = data['request']
            responses_list = data['responses']
            
            with st.expander(f"Request #{request_id} - {request['blood_group']} - {len(responses_list)} Response(s)"):
                # Show original request details
                st.markdown("### Original Request")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Blood Group:** {request['blood_group']}")
                    st.markdown(f"**Quantity:** {request['quantity']} ml")
                    st.markdown(f"**Urgency:** {request['urgency']}")
                
                with col2:
                    st.markdown(f"**Required By:** {request['required_date']}")
                    st.markdown(f"**Status:** {request['status'].title()}")
                
                st.markdown("---")
                
                # Show responses
                st.markdown("### Donor Responses")
                
                for response in responses_list:
                    response_date = datetime.fromisoformat(response['response_date'])
                    
                    if response['response_type'] == 'accept':
                        st.success(f"✅ **{response['donor_username']}** accepted your request")
                        st.markdown(f"**Quantity Offered:** {response['quantity_offered']} ml")
                        if response['message']:
                            st.markdown(f"**Message:** {response['message']}")
                        st.markdown(f"**Response Date:** {response_date.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.warning(f"❌ **{response['donor_username']}** declined your request")
                        if response['message']:
                            st.markdown(f"**Reason:** {response['message']}")
                        st.markdown(f"**Response Date:** {response_date.strftime('%Y-%m-%d %H:%M')}")
                    
                    st.markdown("---")
    else:
        st.info("No responses to your blood requests yet.")
        st.markdown("""
        **When donors respond to your requests, you will see:**
        - Acceptance or decline notifications
        - Donor contact information (if accepted)
        - Messages from donors
        - Quantity offered by donors
        """)

def donate_blood_page():
    st.header("🩸 Donate Blood")
    
    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            quantity = st.number_input("Quantity (ml)", min_value=100, max_value=500, value=350, step=50)
        
        with col2:
            donation_date = st.date_input("Donation Date", value=datetime.now().date())
            blood_bank = st.selectbox("Blood Bank", get_blood_bank_names())
        
        notes = st.text_area("Additional Notes (Optional)")
        
        submitted = st.form_submit_button("Submit Donation")
        
        if submitted:
            if donate_blood(st.session_state.username, blood_group, quantity, donation_date, blood_bank, notes):
                st.success("Blood donation recorded successfully!")
                st.balloons()
            else:
                st.error("Failed to record donation. Please try again.")

def request_blood_page():
    st.header("🔍 Request Blood")
    
    # Show current blood inventory
    st.subheader("Current Blood Availability")
    inventory = get_blood_inventory()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("A+", f"{inventory.get('A+', 0)} ml")
        st.metric("A-", f"{inventory.get('A-', 0)} ml")
    with col2:
        st.metric("B+", f"{inventory.get('B+', 0)} ml")
        st.metric("B-", f"{inventory.get('B-', 0)} ml")
    with col3:
        st.metric("AB+", f"{inventory.get('AB+', 0)} ml")
        st.metric("AB-", f"{inventory.get('AB-', 0)} ml")
    with col4:
        st.metric("O+", f"{inventory.get('O+', 0)} ml")
        st.metric("O-", f"{inventory.get('O-', 0)} ml")
    
    st.markdown("---")
    
    with st.form("request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            blood_group = st.selectbox("Blood Group Needed", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            quantity = st.number_input("Quantity Needed (ml)", min_value=100, max_value=2000, value=350, step=50)
        
        with col2:
            urgency = st.selectbox("Urgency Level", ["Low", "Medium", "High", "Critical"])
            required_date = st.date_input("Required By Date", value=datetime.now().date())
        
        reason = st.text_area("Reason for Blood Request")
        contact_info = st.text_input("Emergency Contact Number")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if reason and contact_info:
                result = request_blood(st.session_state.username, blood_group, quantity, urgency, required_date, reason, contact_info)
                if result['success']:
                    st.success("Blood request submitted successfully!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Request ID:** {result['request_id']}")
                        st.info(f"**Compatible Donors Found:** {result['total_compatible']}")
                    with col2:
                        st.info(f"**Notifications Sent:** {result['notifications_sent']}")
                        if result['total_compatible'] > 0:
                            st.success("Compatible donors have been notified!")
                        else:
                            st.warning("No compatible donors found at the moment. Your request is still active.")
                    
                    if 'error' in result:
                        st.warning(f"Note: {result['error']}")
                else:
                    st.error(f"Failed to submit request: {result.get('error', 'Unknown error')}")
            else:
                st.error("Please fill in all required fields.")

def show_my_donations():
    st.header("📊 My Donation History")
    
    # Load donations data
    try:
        with open("data/donations.json", 'r') as f:
            donations = json.load(f)
    except:
        donations = []
    
    # Filter donations for current user
    user_donations = [d for d in donations if d['donor'] == st.session_state.username]
    
    if user_donations:
        df = pd.DataFrame(user_donations)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Donations", len(user_donations))
        with col2:
            total_quantity = sum(d['quantity'] for d in user_donations)
            st.metric("Total Quantity", f"{total_quantity} ml")
        with col3:
            if user_donations:
                last_donation = max(d['date'] for d in user_donations)
                st.metric("Last Donation", last_donation.split('T')[0])
        
        st.markdown("---")
        
        # Donations table
        st.dataframe(
            df[['date', 'blood_group', 'quantity', 'blood_bank', 'notes']].rename(columns={
                'date': 'Date',
                'blood_group': 'Blood Group',
                'quantity': 'Quantity (ml)',
                'blood_bank': 'Blood Bank',
                'notes': 'Notes'
            }),
            use_container_width=True
        )
    else:
        st.info("You haven't made any donations yet.")

def show_my_requests():
    st.header("📋 My Blood Requests")
    
    # Load requests data
    try:
        with open("data/requests.json", 'r') as f:
            requests = json.load(f)
    except:
        requests = []
    
    # Filter requests for current user
    user_requests = [r for r in requests if r['requester'] == st.session_state.username]
    
    if user_requests:
        df = pd.DataFrame(user_requests)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Requests", len(user_requests))
        with col2:
            pending_requests = len([r for r in user_requests if r['status'] == 'pending'])
            st.metric("Pending Requests", pending_requests)
        
        st.markdown("---")
        
        # Requests table
        st.dataframe(
            df[['date', 'blood_group', 'quantity', 'urgency', 'status', 'reason']].rename(columns={
                'date': 'Date',
                'blood_group': 'Blood Group',
                'quantity': 'Quantity (ml)',
                'urgency': 'Urgency',
                'status': 'Status',
                'reason': 'Reason'
            }),
            use_container_width=True
        )
    else:
        st.info("You haven't made any blood requests yet.")

def get_blood_bank_names():
    try:
        with open("data/blood_banks.json", 'r') as f:
            blood_banks = json.load(f)
        return [bank['name'] for bank in blood_banks]
    except:
        return ["Default Blood Bank"]

if __name__ == "__main__":
    main()
