import streamlit as st
import folium
from streamlit_folium import st_folium
import json

def load_blood_banks():
    """Load blood bank locations from JSON file"""
    try:
        with open("data/blood_banks.json", 'r') as f:
            return json.load(f)
    except:
        return []

def show_blood_bank_map():
    """Display interactive map with blood bank locations"""
    st.header("🗺️ Find Nearby Blood Banks")
    
    # Load blood bank data
    blood_banks = load_blood_banks()
    
    if not blood_banks:
        st.error("No blood bank data available.")
        return
    
    # Create map centered on India
    center_lat = 20.5937
    center_lng = 78.9629
    
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add markers for each blood bank
    for bank in blood_banks:
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="color: #d63384; margin-bottom: 10px;">{bank['name']}</h4>
            <p><strong>📍 Address:</strong><br>{bank['address']}</p>
            <p><strong>📞 Contact:</strong><br>{bank['contact']}</p>
            <hr style="margin: 10px 0;">
            <p style="font-size: 12px; color: #666;">
                Click for directions or call for blood availability
            </p>
        </div>
        """
        
        # Add marker with custom icon
        folium.Marker(
            location=[bank['lat'], bank['lng']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=bank['name'],
            icon=folium.Icon(
                color='red',
                icon='plus',
                prefix='fa'
            )
        ).add_to(m)
    
    # Display the map
    map_data = st_folium(m, width=700, height=500)
    
    st.markdown("---")
    
    # Blood Bank Directory
    st.subheader("📋 Blood Bank Directory")
    
    # Search functionality
    search_term = st.text_input("🔍 Search blood banks by name or location:")
    
    # Filter blood banks based on search
    if search_term:
        filtered_banks = [
            bank for bank in blood_banks 
            if search_term.lower() in bank['name'].lower() or 
               search_term.lower() in bank['address'].lower()
        ]
    else:
        filtered_banks = blood_banks
    
    # Display blood banks in cards
    for i, bank in enumerate(filtered_banks):
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**🏥 {bank['name']}**")
                st.markdown(f"📍 {bank['address']}")
            
            with col2:
                st.markdown(f"📞 **Contact:** {bank['contact']}")
                st.markdown(f"🧭 **Coordinates:** {bank['lat']}, {bank['lng']}")
            
            with col3:
                # Create directions link (Google Maps)
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={bank['lat']},{bank['lng']}"
                st.markdown(f"[🗺️ Get Directions]({directions_url})")
        
        if i < len(filtered_banks) - 1:
            st.markdown("---")
    
    # Add new blood bank section (for admin users - simplified version)
    if st.session_state.get('user_type') == 'donor':
        st.markdown("---")
        st.subheader("➕ Suggest a Blood Bank")
        
        with st.expander("Add Blood Bank Location"):
            with st.form("add_blood_bank"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Blood Bank Name")
                    address = st.text_area("Address")
                
                with col2:
                    contact = st.text_input("Contact Number")
                    col_lat, col_lng = st.columns(2)
                    with col_lat:
                        lat = st.number_input("Latitude", format="%.6f", value=0.0)
                    with col_lng:
                        lng = st.number_input("Longitude", format="%.6f", value=0.0)
                
                submitted = st.form_submit_button("Suggest Blood Bank")
                
                if submitted:
                    if name and address and contact and lat != 0.0 and lng != 0.0:
                        # Add new blood bank (in a real app, this would need admin approval)
                        new_bank = {
                            'name': name,
                            'address': address,
                            'contact': contact,
                            'lat': lat,
                            'lng': lng
                        }
                        
                        blood_banks.append(new_bank)
                        
                        try:
                            with open("data/blood_banks.json", 'w') as f:
                                json.dump(blood_banks, f, indent=2)
                            st.success("Blood bank suggestion submitted successfully!")
                            st.rerun()
                        except:
                            st.error("Failed to save blood bank information.")
                    else:
                        st.error("Please fill in all fields with valid information.")

def get_distance_between_points(lat1, lng1, lat2, lng2):
    """Calculate distance between two points using Haversine formula"""
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng/2) * math.sin(delta_lng/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def find_nearby_blood_banks(user_lat, user_lng, radius_km=50):
    """Find blood banks within specified radius"""
    blood_banks = load_blood_banks()
    nearby_banks = []
    
    for bank in blood_banks:
        distance = get_distance_between_points(
            user_lat, user_lng, bank['lat'], bank['lng']
        )
        
        if distance <= radius_km:
            bank['distance'] = round(distance, 2)
            nearby_banks.append(bank)
    
    # Sort by distance
    nearby_banks.sort(key=lambda x: x['distance'])
    return nearby_banks
