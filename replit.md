# Blood Bank Management System

## Overview

This is a comprehensive Blood Bank Management System built with Streamlit that facilitates blood donation and request management. The application provides a web-based interface for donors, receivers, and administrators to manage blood inventory, track donations, and locate nearby blood banks through an interactive mapping system.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for rapid web application development
- **UI Components**: Native Streamlit widgets and components
- **Visualization**: Plotly for charts and graphs, Folium for interactive maps
- **Layout**: Multi-page application with modular component structure

### Backend Architecture
- **Data Storage**: JSON file-based persistence (no database server required)
- **Authentication**: Simple hash-based authentication using SHA256
- **Session Management**: Streamlit's built-in session state
- **Business Logic**: Modular Python modules for different functionalities

### Data Storage Solutions
- **File-based Storage**: JSON files for all data persistence
- **Data Structure**: Organized into separate files for users, inventory, donations, requests, and blood bank locations
- **No External Database**: Self-contained system with local file storage

## Key Components

### 1. Authentication System (`auth.py`)
- User registration and login functionality
- Password hashing using SHA256
- Support for different user types (donor, receiver, admin)
- Session state management for user authentication

### 2. Blood Management (`blood_management.py`)
- Blood inventory tracking with 8 blood group types (A+, A-, B+, B-, AB+, AB-, O+, O-)
- Donation recording and management
- Blood request processing
- Real-time inventory updates

### 3. Dashboard (`dashboard.py`)
- Analytics and visualization dashboard
- Key metrics display (total donors, receivers, donations, requests)
- Interactive charts using Plotly
- Blood inventory visualization

### 4. Interactive Maps (`maps.py`)
- Integration with Folium for interactive mapping
- Blood bank location display
- Popup information with contact details
- Geographic visualization of blood bank network

### 5. Main Application (`app.py`)
- Central application orchestration
- Page routing and navigation
- Data directory initialization
- Streamlit configuration

## Data Flow

1. **User Registration/Login**: Users authenticate through the auth module, with credentials stored in `users.json`
2. **Blood Donation**: Donors can record donations, updating both `donations.json` and `blood_inventory.json`
3. **Blood Requests**: Receivers can submit requests, stored in `requests.json`
4. **Inventory Management**: Real-time tracking of blood availability across all blood groups
5. **Analytics**: Dashboard aggregates data from all JSON files for visualization
6. **Location Services**: Map component displays blood bank locations from `blood_banks.json`

## External Dependencies

### Python Packages
- **streamlit**: Core web application framework
- **plotly**: Data visualization and charting
- **folium**: Interactive mapping capabilities
- **streamlit-folium**: Streamlit integration for Folium maps
- **pandas**: Data manipulation and analysis
- **json**: Built-in JSON handling
- **hashlib**: Password hashing functionality
- **datetime**: Date and time operations

### Data Dependencies
- Pre-populated blood bank locations across major Indian cities
- Initial blood inventory structure for all blood groups
- Empty data files for users, donations, and requests

## Deployment Strategy

### Local Development
- File-based storage eliminates database setup requirements
- All data persisted in local `data/` directory
- Streamlit's built-in development server for rapid prototyping

### Production Considerations
- JSON file storage suitable for small to medium-scale deployments
- Consider migration to proper database (PostgreSQL) for larger scale
- Data directory needs persistent volume in containerized deployments
- Environment-specific configuration for different deployment stages

### Scalability Notes
- Current architecture suitable for single-instance deployments
- File-based storage may become bottleneck with high concurrent users
- Future migration path available to database-backed storage

## Changelog

```
Changelog:
- July 07, 2025. Initial setup with basic functionality
- July 07, 2025. Added simplified authentication features:
  * Immediate registration with welcome email (all OTP verification removed)
  * Local email notification system showing actual email content
  * Password reset with secure reset links and tokens via email
  * Change password feature integrated into dashboard home page
  * Notification history viewing for users
  * Beautiful medical-themed background with SVG graphics
- July 07, 2025. Added blood request management system:
  * Automatic donor notification when blood requests are submitted
  * Blood compatibility matching and donor filtering
  * Donor response system (accept/decline with messages)
  * Request tracking with unique IDs
  * Real-time response notifications to requesters
  * Complete donor-requester communication workflow
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Technical Decisions

### File-based Storage Choice
- **Problem**: Need simple, lightweight data persistence
- **Solution**: JSON file storage in local directory
- **Rationale**: Eliminates database setup complexity, suitable for small-scale deployments
- **Trade-offs**: Limited scalability but faster development and deployment

### Streamlit Framework Choice
- **Problem**: Need rapid web application development
- **Solution**: Streamlit for Python-based web apps
- **Rationale**: Allows focus on business logic rather than frontend development
- **Trade-offs**: Limited customization but significantly faster development

### Modular Architecture
- **Problem**: Organize complex functionality
- **Solution**: Separate modules for auth, blood management, dashboard, and maps
- **Rationale**: Maintainable code structure with clear separation of concerns
- **Benefits**: Easy testing, debugging, and feature additions

### Password Security
- **Problem**: Secure user authentication and password management
- **Solution**: SHA256 hashing for password storage with multi-factor authentication
- **Rationale**: Prevents plain text password storage and adds verification layers
- **Features**: Email/SMS OTP verification, password reset tokens, change password functionality
- **Note**: Production systems should consider more robust hashing (bcrypt, scrypt)

### Notification System
- **Problem**: User communication and verification needs
- **Solution**: Local notification storage system simulating email/SMS services
- **Rationale**: Provides authentication feedback without external service dependencies
- **Features**: Registration confirmations, OTP delivery, password reset instructions
- **Trade-offs**: Local storage only but enables full workflow testing

### Multi-Step Registration
- **Problem**: Need secure user onboarding with verification
- **Solution**: Four-step registration process with email and phone verification
- **Rationale**: Ensures valid contact information and prevents spam registrations
- **Benefits**: Enhanced security, better user data quality, professional user experience