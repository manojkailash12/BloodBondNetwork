import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Import custom modules
from auth import login_user, register_user, logout_user
from blood_management import donate_blood, request_blood, get_blood_inventory
from dashboard import show_dashboard
from maps import show_blood_bank_map

# Initialize data directories
def init_data_dirs():
    os.makedirs("data", exist_ok=True)
    
    # Initialize empty data files if they don't exist
    files = [
        "data/users.json",
        "data/blood_inventory.json", 
        "data/donations.json",
        "data/requests.json",
        "data/blood_banks.json"
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
            else:
                sample_data = []
            
            with open(file_path, 'w') as f:
                json.dump(sample_data, f, indent=2)

def main():
    st.set_page_config(
        page_title="Blood Bank Management System",
        page_icon="🩸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize data
    init_data_dirs()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
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
            menu_options = ["Dashboard", "Donate Blood", "Blood Bank Map", "My Donations"]
        elif st.session_state.user_type == "receiver":
            menu_options = ["Dashboard", "Request Blood", "Blood Bank Map", "My Requests"]
        else:
            menu_options = ["Dashboard", "Blood Bank Map"]
            
        selected_page = st.sidebar.selectbox("Navigation", menu_options)
        
        # Main content area
        if selected_page == "Dashboard":
            show_dashboard()
        elif selected_page == "Donate Blood":
            donate_blood_page()
        elif selected_page == "Request Blood":
            request_blood_page()
        elif selected_page == "Blood Bank Map":
            show_blood_bank_map()
        elif selected_page == "My Donations":
            show_my_donations()
        elif selected_page == "My Requests":
            show_my_requests()
    else:
        # Login/Register interface
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            login_form()
        
        with auth_tab2:
            register_form()

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
    
    with st.form("register_form"):
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
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if username and email and phone and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    if register_user(username, email, phone, password, user_type, blood_group, age):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists.")
            else:
                st.error("Please fill in all required fields.")

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
                if request_blood(st.session_state.username, blood_group, quantity, urgency, required_date, reason, contact_info):
                    st.success("Blood request submitted successfully!")
                    st.info("You will be contacted once matching blood is available.")
                else:
                    st.error("Failed to submit request. Please try again.")
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
