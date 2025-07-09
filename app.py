import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import base64

# Import custom modules
from auth import (
    login_user, logout_user, send_email_otp, send_phone_otp,
    verify_email_otp, verify_phone_otp, register_user,
    initiate_password_reset, reset_password, change_password
)
from blood_management import donate_blood, request_blood, get_blood_inventory
from dashboard import show_dashboard
from maps import show_blood_bank_map
from notifications import load_otps
from request_management import (
    get_pending_requests_for_donor,
    respond_to_request,
    get_requester_notifications
)

# ------------------------------
# Utility: init data
# ------------------------------
def init_data_dirs():
    os.makedirs("data", exist_ok=True)
    files = [
        "data/users.json", "data/blood_inventory.json", "data/donations.json",
        "data/requests.json", "data/blood_banks.json", "data/otps.json",
        "data/notifications.json", "data/request_responses.json"
    ]
    for file_path in files:
        if not os.path.exists(file_path):
            if "blood_banks.json" in file_path:
                sample_data = [
                    {"name": "City Blood Bank", "lat": 28.6139, "lng": 77.2090, "address": "Delhi, India", "contact": "+91-9876543210"},
                    {"name": "Central Hospital Blood Bank", "lat": 19.0760, "lng": 72.8777, "address": "Mumbai, India", "contact": "+91-9876543211"},
                    {"name": "Metro Blood Center", "lat": 12.9716, "lng": 77.5946, "address": "Bangalore, India", "contact": "+91-9876543212"},
                    {"name": "Regional Blood Bank", "lat": 13.0827, "lng": 80.2707, "address": "Chennai, India", "contact": "+91-9876543213"}
                ]
            elif "blood_inventory.json" in file_path:
                sample_data = {bg: 0 for bg in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]}
            elif "otps.json" in file_path:
                sample_data = {}
            else:
                sample_data = []
            with open(file_path, "w") as f:
                json.dump(sample_data, f, indent=2)

# ------------------------------
# Background SVG Utility
# ------------------------------
def get_base64_svg(svg_file):
    try:
        with open(svg_file, "r") as f:
            svg_content = f.read()
        return base64.b64encode(svg_content.encode()).decode()
    except:
        return None

def add_bg_from_local(svg_file):
    svg_base64 = get_base64_svg(svg_file)
    if svg_base64:
        st.markdown(f"""
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
        </style>
        """, unsafe_allow_html=True)

# ------------------------------
# Main Function
# ------------------------------
def main():
    st.set_page_config(page_title="Blood Bond Network", layout="wide", page_icon="🩸")
    add_bg_from_local("static/background.svg")
    init_data_dirs()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.username = None

    if st.session_state.logged_in:
        st.sidebar.success(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            logout_user()
            st.rerun()
        show_dashboard()
    else:
        st.title("🩸 Blood Bond Network Login")
        login_form()
        st.markdown("---")
        register_form()
        st.markdown("---")
        forgot_password_form()

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    main()
