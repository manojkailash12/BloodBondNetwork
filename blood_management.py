import json
import streamlit as st
from datetime import datetime

def load_blood_inventory():
    """Load blood inventory from JSON file"""
    try:
        with open("data/blood_inventory.json", 'r') as f:
            return json.load(f)
    except:
        return {"A+": 0, "A-": 0, "B+": 0, "B-": 0, "AB+": 0, "AB-": 0, "O+": 0, "O-": 0}

def save_blood_inventory(inventory):
    """Save blood inventory to JSON file"""
    try:
        with open("data/blood_inventory.json", 'w') as f:
            json.dump(inventory, f, indent=2)
        return True
    except:
        return False

def load_donations():
    """Load donations from JSON file"""
    try:
        with open("data/donations.json", 'r') as f:
            return json.load(f)
    except:
        return []

def save_donations(donations):
    """Save donations to JSON file"""
    try:
        with open("data/donations.json", 'w') as f:
            json.dump(donations, f, indent=2)
        return True
    except:
        return False

def load_requests():
    """Load blood requests from JSON file"""
    try:
        with open("data/requests.json", 'r') as f:
            return json.load(f)
    except:
        return []

def save_requests(requests):
    """Save blood requests to JSON file"""
    try:
        with open("data/requests.json", 'w') as f:
            json.dump(requests, f, indent=2)
        return True
    except:
        return False

def donate_blood(donor, blood_group, quantity, donation_date, blood_bank, notes=""):
    """Record a blood donation"""
    # Load current data
    donations = load_donations()
    inventory = load_blood_inventory()
    
    # Create donation record
    donation = {
        'donor': donor,
        'blood_group': blood_group,
        'quantity': quantity,
        'date': donation_date.isoformat(),
        'blood_bank': blood_bank,
        'notes': notes,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to donations
    donations.append(donation)
    
    # Update inventory
    inventory[blood_group] = inventory.get(blood_group, 0) + quantity
    
    # Save both files
    return save_donations(donations) and save_blood_inventory(inventory)

def request_blood(requester, blood_group, quantity, urgency, required_date, reason, contact_info):
    """Submit a blood request and notify compatible donors"""
    from request_management import generate_request_id, notify_compatible_donors
    
    requests = load_requests()
    
    # Create request record with unique ID
    request = {
        'id': generate_request_id(),
        'requester': requester,
        'blood_group': blood_group,
        'quantity': quantity,
        'urgency': urgency,
        'required_date': required_date.isoformat(),
        'reason': reason,
        'contact_info': contact_info,
        'date': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    requests.append(request)
    
    if save_requests(requests):
        # Notify compatible donors about this request
        try:
            notifications_sent, total_compatible = notify_compatible_donors(request)
            return {
                'success': True,
                'request_id': request['id'],
                'notifications_sent': notifications_sent,
                'total_compatible': total_compatible
            }
        except Exception as e:
            # Even if notifications fail, the request was saved
            return {
                'success': True,
                'request_id': request['id'],
                'notifications_sent': 0,
                'total_compatible': 0,
                'error': str(e)
            }
    
    return {'success': False, 'error': 'Failed to save request'}

def get_blood_inventory():
    """Get current blood inventory"""
    return load_blood_inventory()

def get_total_donations():
    """Get total blood donations"""
    donations = load_donations()
    return sum(donation['quantity'] for donation in donations)

def get_total_requests():
    """Get total blood requests"""
    requests = load_requests()
    return sum(request['quantity'] for request in requests)

def get_donations_by_blood_group():
    """Get donations grouped by blood group"""
    donations = load_donations()
    blood_groups = {}
    
    for donation in donations:
        bg = donation['blood_group']
        blood_groups[bg] = blood_groups.get(bg, 0) + donation['quantity']
    
    return blood_groups

def get_requests_by_blood_group():
    """Get requests grouped by blood group"""
    requests = load_requests()
    blood_groups = {}
    
    for request in requests:
        bg = request['blood_group']
        blood_groups[bg] = blood_groups.get(bg, 0) + request['quantity']
    
    return blood_groups

def check_blood_compatibility(donor_group, recipient_group):
    """Check if donor blood is compatible with recipient"""
    compatibility_matrix = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }
    
    return recipient_group in compatibility_matrix.get(donor_group, [])

def get_compatible_donors(recipient_blood_group):
    """Get list of compatible donor blood groups for a recipient"""
    compatibility_matrix = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
    }
    
    return compatibility_matrix.get(recipient_blood_group, [])
