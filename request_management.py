import json
import streamlit as st
from datetime import datetime
from auth import get_users_by_type, get_user_info
from blood_management import get_compatible_donors, load_requests, save_requests
from notifications import send_email_notification, send_sms_notification

def load_request_responses():
    """Load request responses from JSON file"""
    try:
        with open("data/request_responses.json", 'r') as f:
            return json.load(f)
    except:
        return []

def save_request_responses(responses):
    """Save request responses to JSON file"""
    try:
        with open("data/request_responses.json", 'w') as f:
            json.dump(responses, f, indent=2)
        return True
    except:
        return False

def notify_compatible_donors(request_data):
    """Notify donors who can fulfill a blood request"""
    requester_blood_group = request_data['blood_group']
    compatible_donor_groups = get_compatible_donors(requester_blood_group)
    
    # Get all donors with compatible blood groups
    all_donors = get_users_by_type('donor')
    compatible_donors = [
        donor for donor in all_donors 
        if donor.get('blood_group') in compatible_donor_groups
    ]
    
    notifications_sent = 0
    
    for donor in compatible_donors:
        # Create notification message
        email_subject = "Blood Request Match - Your Help Needed!"
        email_message = f"""
Dear {donor['username']},

A blood request has been submitted that matches your blood group!

REQUEST DETAILS:
- Blood Group Needed: {request_data['blood_group']}
- Quantity: {request_data['quantity']} ml
- Urgency: {request_data['urgency']}
- Required By: {request_data['required_date']}
- Reason: {request_data['reason']}
- Requester: {request_data['requester']}

Your blood group ({donor['blood_group']}) is compatible with this request.

Please log into the Blood Bank Management System to respond to this request and help save a life!

Thank you for being a life-saver!

Best regards,
Blood Bank Management Team
"""

        sms_message = f"Blood Request Alert! {request_data['blood_group']} blood needed urgently. Your {donor['blood_group']} blood can help! Login to respond. Quantity: {request_data['quantity']}ml"
        
        # Send notifications
        if send_email_notification(donor['email'], email_subject, email_message):
            notifications_sent += 1
        
        send_sms_notification(donor['phone'], sms_message)
    
    return notifications_sent, len(compatible_donors)

def get_pending_requests_for_donor(donor_username):
    """Get blood requests that a donor can fulfill"""
    donor_info = get_user_info(donor_username)
    if not donor_info or not donor_info.get('blood_group'):
        return []
    
    donor_blood_group = donor_info['blood_group']
    requests = load_requests()
    
    # Filter requests that this donor can fulfill
    compatible_requests = []
    for request in requests:
        if request['status'] == 'pending':
            # Check if donor's blood is compatible with request
            recipient_blood_group = request['blood_group']
            compatible_groups = get_compatible_donors(recipient_blood_group)
            
            if donor_blood_group in compatible_groups:
                compatible_requests.append(request)
    
    return compatible_requests

def respond_to_request(request_id, donor_username, response_type, message="", quantity_offered=0):
    """Record donor's response to a blood request"""
    responses = load_request_responses()
    
    response = {
        'request_id': request_id,
        'donor_username': donor_username,
        'response_type': response_type,  # 'accept', 'decline'
        'message': message,
        'quantity_offered': quantity_offered,
        'response_date': datetime.now().isoformat(),
        'status': 'pending_approval'
    }
    
    responses.append(response)
    
    if save_request_responses(responses):
        # Notify the requester about the response
        requests = load_requests()
        request_data = None
        for req in requests:
            if req.get('id') == request_id:
                request_data = req
                break
        
        if request_data:
            requester_info = get_user_info(request_data['requester'])
            donor_info = get_user_info(donor_username)
            
            if requester_info and donor_info:
                if response_type == 'accept':
                    subject = "Good News! Donor Found for Your Blood Request"
                    email_message = f"""
Dear {requester_info['username']},

Great news! A donor has responded to your blood request:

DONOR DETAILS:
- Donor: {donor_info['username']}
- Blood Group: {donor_info['blood_group']}
- Quantity Offered: {quantity_offered} ml
- Contact: {donor_info['phone']}

ORIGINAL REQUEST:
- Blood Group: {request_data['blood_group']}
- Quantity Needed: {request_data['quantity']} ml
- Urgency: {request_data['urgency']}

DONOR MESSAGE:
{message if message else 'No additional message'}

Please coordinate with the donor for the blood donation. The blood bank staff will facilitate the process.

Thank you for using our service!

Best regards,
Blood Bank Management Team
"""
                    
                    sms_message = f"Great news! Donor found for your {request_data['blood_group']} blood request. {quantity_offered}ml offered. Contact: {donor_info['phone']}"
                else:
                    subject = "Update on Your Blood Request"
                    email_message = f"""
Dear {requester_info['username']},

A donor has responded to your blood request but is unable to donate at this time.

DONOR MESSAGE:
{message if message else 'No message provided'}

Don't worry - we are still searching for other compatible donors for your request.

Best regards,
Blood Bank Management Team
"""
                    sms_message = f"Update on your {request_data['blood_group']} blood request. Still searching for donors. Stay hopeful!"
                
                send_email_notification(requester_info['email'], subject, email_message)
                send_sms_notification(requester_info['phone'], sms_message)
        
        return True
    
    return False

def get_responses_for_request(request_id):
    """Get all donor responses for a specific request"""
    responses = load_request_responses()
    return [r for r in responses if r['request_id'] == request_id]

def update_request_status(request_id, new_status):
    """Update the status of a blood request"""
    requests = load_requests()
    
    for request in requests:
        if request.get('id') == request_id:
            request['status'] = new_status
            request['updated_at'] = datetime.now().isoformat()
            break
    
    return save_requests(requests)

def generate_request_id():
    """Generate a unique request ID"""
    import time
    return f"REQ_{int(time.time() * 1000)}"

def get_donor_response_history(donor_username):
    """Get response history for a donor"""
    responses = load_request_responses()
    return [r for r in responses if r['donor_username'] == donor_username]

def get_requester_notifications(requester_username):
    """Get all responses received for a requester's blood requests"""
    requests = load_requests()
    requester_requests = [r for r in requests if r['requester'] == requester_username]
    
    all_responses = []
    for request in requester_requests:
        request_id = request.get('id')
        if request_id:
            responses = get_responses_for_request(request_id)
            for response in responses:
                response['request_details'] = request
                all_responses.append(response)
    
    return all_responses

def get_pending_requests_for_donor(username):
    # Dummy implementation: returns a sample list
    return [
        {
            "id": 1,
            "blood_group": "A+",
            "quantity": 500,
            "urgency": "High",
            "recipient": "user@example.com"
        }
    ]

def respond_to_request(request_id, donor_username, response):
    # Dummy implementation: just print/log the response
    print(f"Donor {donor_username} responded '{response}' to request {request_id}")