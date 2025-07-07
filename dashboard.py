import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from blood_management import (
    get_blood_inventory, get_total_donations, get_total_requests,
    get_donations_by_blood_group, get_requests_by_blood_group,
    load_donations, load_requests
)
from auth import get_total_users, get_users_by_type

def show_dashboard():
    """Display the main dashboard with analytics"""
    st.header("📊 Blood Bank Dashboard")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_donors = len(get_users_by_type('donor'))
        st.metric("Total Donors", total_donors, delta=None)
    
    with col2:
        total_receivers = len(get_users_by_type('receiver'))
        st.metric("Total Receivers", total_receivers, delta=None)
    
    with col3:
        total_donated = get_total_donations()
        st.metric("Total Blood Donated", f"{total_donated:,} ml", delta=None)
    
    with col4:
        total_requested = get_total_requests()
        st.metric("Total Blood Requested", f"{total_requested:,} ml", delta=None)
    
    st.markdown("---")
    
    # Blood Inventory Section
    st.subheader("🩸 Current Blood Inventory")
    
    inventory = get_blood_inventory()
    
    # Create inventory visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart of blood inventory
        blood_groups = list(inventory.keys())
        quantities = list(inventory.values())
        
        fig_inventory = px.bar(
            x=blood_groups,
            y=quantities,
            labels={'x': 'Blood Group', 'y': 'Quantity (ml)'},
            title="Blood Inventory by Group",
            color=quantities,
            color_continuous_scale='Reds'
        )
        fig_inventory.update_layout(showlegend=False)
        st.plotly_chart(fig_inventory, use_container_width=True)
    
    with col2:
        # Inventory details
        st.markdown("**Inventory Details:**")
        for blood_group, quantity in inventory.items():
            status = "🟢" if quantity > 1000 else "🟡" if quantity > 500 else "🔴"
            st.write(f"{status} **{blood_group}**: {quantity:,} ml")
    
    st.markdown("---")
    
    # Donations vs Requests Comparison
    st.subheader("📈 Donations vs Requests Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Donations by blood group
        donations_by_group = get_donations_by_blood_group()
        if donations_by_group:
            fig_donations = px.pie(
                values=list(donations_by_group.values()),
                names=list(donations_by_group.keys()),
                title="Donations by Blood Group"
            )
            st.plotly_chart(fig_donations, use_container_width=True)
        else:
            st.info("No donation data available yet.")
    
    with col2:
        # Requests by blood group
        requests_by_group = get_requests_by_blood_group()
        if requests_by_group:
            fig_requests = px.pie(
                values=list(requests_by_group.values()),
                names=list(requests_by_group.keys()),
                title="Requests by Blood Group"
            )
            st.plotly_chart(fig_requests, use_container_width=True)
        else:
            st.info("No request data available yet.")
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("🕒 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Recent Donations**")
        donations = load_donations()
        if donations:
            # Sort by date and get last 5
            recent_donations = sorted(donations, key=lambda x: x['timestamp'], reverse=True)[:5]
            
            for donation in recent_donations:
                date = datetime.fromisoformat(donation['timestamp']).strftime("%Y-%m-%d %H:%M")
                st.write(f"• {donation['donor']} donated {donation['quantity']}ml of {donation['blood_group']} on {date}")
        else:
            st.info("No recent donations.")
    
    with col2:
        st.markdown("**Recent Requests**")
        requests = load_requests()
        if requests:
            # Sort by date and get last 5
            recent_requests = sorted(requests, key=lambda x: x['date'], reverse=True)[:5]
            
            for request in recent_requests:
                date = datetime.fromisoformat(request['date']).strftime("%Y-%m-%d %H:%M")
                urgency_color = {
                    'Low': '🟢',
                    'Medium': '🟡', 
                    'High': '🟠',
                    'Critical': '🔴'
                }
                urgency_icon = urgency_color.get(request['urgency'], '⚪')
                st.write(f"{urgency_icon} {request['requester']} requested {request['quantity']}ml of {request['blood_group']} on {date}")
        else:
            st.info("No recent requests.")
    
    st.markdown("---")
    
    # Blood Group Compatibility Matrix
    if st.expander("🔬 Blood Group Compatibility Reference"):
        st.markdown("**Universal Donors and Recipients:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Universal Donors:**
            - O- : Can donate to all blood groups
            - O+ : Can donate to O+, A+, B+, AB+
            """)
        
        with col2:
            st.markdown("""
            **Universal Recipients:**
            - AB+ : Can receive from all blood groups
            - AB- : Can receive from O-, A-, B-, AB-
            """)
        
        # Compatibility matrix
        compatibility_data = {
            'Recipient': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'O-': ['✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅'],
            'O+': ['❌', '✅', '❌', '✅', '❌', '✅', '❌', '✅'],
            'A-': ['❌', '❌', '✅', '✅', '❌', '❌', '✅', '✅'],
            'A+': ['❌', '❌', '❌', '✅', '❌', '❌', '❌', '✅'],
            'B-': ['❌', '❌', '❌', '❌', '✅', '✅', '✅', '✅'],
            'B+': ['❌', '❌', '❌', '❌', '❌', '✅', '❌', '✅'],
            'AB-': ['❌', '❌', '❌', '❌', '❌', '❌', '✅', '✅'],
            'AB+': ['❌', '❌', '❌', '❌', '❌', '❌', '❌', '✅']
        }
        
        df_compatibility = pd.DataFrame(compatibility_data)
        st.markdown("**Donor → Recipient Compatibility Matrix:**")
        st.dataframe(df_compatibility, use_container_width=True)
    
    st.markdown("---")
    
    # Change Password Section
    if st.expander("🔒 Change Password"):
        from auth import change_password
        
        st.markdown("**Update your account password**")
        
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
                        st.error("New password must be at least 6 characters long.")
                    elif current_password == new_password:
                        st.error("New password must be different from current password.")
                    else:
                        result = change_password(st.session_state.username, current_password, new_password)
                        if result['success']:
                            st.success("Password changed successfully!")
                            st.balloons()
                        else:
                            st.error(result['error'])
                else:
                    st.error("Please fill in all fields.")

def show_admin_analytics():
    """Show detailed analytics for admin users"""
    # This function can be expanded for admin-specific analytics
    pass
