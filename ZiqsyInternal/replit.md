# Ziqsy Internal Admin System

## Overview

This is a comprehensive internal web application for Ziqsy that unifies multiple operational workflows, tools, and repositories into a single admin system. The application provides a flexible page-based architecture where users can create different types of pages (Link Operations, Lists, Datasets, Repositories) to manage various business processes and data.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11+) with SQLAlchemy ORM
- **Database**: PostgreSQL with dynamic table creation capabilities
- **File Processing**: Pandas for CSV/Excel handling, support for JSON and Markdown
- **Authentication**: Session-based authentication with hardcoded demo credentials
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask
- **Styling**: Bootstrap 5 + custom CSS with beige/mauve theme
- **JavaScript**: Vanilla JavaScript with Chart.js for data visualization
- **Icons**: Font Awesome for consistent iconography
- **Layout**: Responsive sidebar navigation with main content area

### Database Design
- **Static Tables**: Users, Sections, Pages, DynamicTable metadata
- **Dynamic Tables**: Created on-demand based on uploaded CSV files
- **Relationships**: Hierarchical structure (Sections → Pages → Dynamic Tables)

## Key Components

### Authentication System
- Simple email/password authentication (demo: admin@ziqsy.com / ziqsy2025)
- Session-based user management
- Login/logout functionality with flash messaging

### Navigation System
- Collapsible left sidebar with sections and pages
- Hierarchical organization: Sections contain Pages
- Dynamic page creation with type-specific functionality

### Page Types
1. **Link Operations**: Category-based navigation with card display and edit panel
2. **List**: Flat table structure with inline CRUD operations
3. **Dataset**: Advanced data management with charts and analysis tools
4. **Repository**: File management with cloud folder integration

### Dynamic Table Management
- Automatic table creation from CSV uploads
- Column sanitization and data type handling
- CRUD operations on dynamically created tables
- Export functionality back to CSV format

### File Processing Pipeline
- Multi-format support (CSV, Excel, JSON, Markdown)
- Secure file upload with size and type validation
- Temporary file storage in uploads directory
- Data transformation and cleaning utilities

## Data Flow

1. **User Authentication**: Login → Session Creation → Dashboard Access
2. **Content Creation**: Section Creation → Page Creation → Type Selection
3. **Data Upload**: File Upload → Schema Detection → Table Creation → Data Import
4. **Data Management**: View → Edit → Update/Delete → Export
5. **File Management**: Upload → Storage → Metadata Tracking → Access

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: ORM and database operations
- **Pandas**: Data processing and file handling
- **Psycopg2-binary**: PostgreSQL database adapter
- **Gunicorn**: Production WSGI server
- **Werkzeug**: WSGI utilities and security
- **OpenPyXL/XlRD**: Excel file processing

### Frontend Libraries
- **Bootstrap 5**: UI components and responsive layout
- **Font Awesome**: Icon library
- **Chart.js**: Data visualization and charting

### System Dependencies
- **PostgreSQL**: Primary database server
- **OpenSSL**: Secure connections and cryptography

## Deployment Strategy

### Development Environment
- Python 3.11 with Nix package management
- Local PostgreSQL instance
- Flask development server with debug mode
- File-based uploads directory

### Production Deployment
- Gunicorn WSGI server with autoscale configuration
- Bind to 0.0.0.0:5000 with port reuse and reload capabilities
- Environment variable configuration for database and secrets
- ProxyFix middleware for proper header handling

### Database Configuration
- Connection pooling with 300-second recycle time
- Pre-ping enabled for connection health checks
- Environment-based connection string configuration
- Automatic table creation on application startup

## Changelog
- June 17, 2025: Initial setup with PostgreSQL database and Flask backend
- June 17, 2025: Added mobile-responsive category filters (dropdown on mobile, cards on desktop)
- June 17, 2025: Implemented centered dashboard welcome layout with larger text for better readability
- June 17, 2025: Added comprehensive database error handling to prevent crashes during connection issues
- June 17, 2025: Enhanced UI layout - Dashboard button positioned below logo, standardized spacing between tabs
- June 17, 2025: Fixed JavaScript file input errors and 'dict' object attribute issues in file processing
- June 17, 2025: Improved error handling for temporary storage fallback during database connection issues
- June 17, 2025: Complete dark theme transformation with blue-gray background (#1a202c), white text, and teal accents (#14b8a6)
- June 17, 2025: Fixed sidebar text visibility issues and removed dashboard welcome message for cleaner interface
- June 18, 2025: Implemented comprehensive theme system with 6 color schemes (Dark, Light, Modern, Old School, Steel, Gold)
- June 18, 2025: Enhanced link operations page with column-based edit form layout and improved field sizing
- June 18, 2025: Added theme selector to sidebar footer with localStorage persistence across all pages
- June 18, 2025: Built cloud folder browser for repository pages with AI-generated file descriptions and user note system
- June 18, 2025: Successfully deployed cloud folder tree interface with file selection, details panel, and color-coded file type icons
- June 18, 2025: Integrated authentic OneDrive file structure display with real folder and file names from user's Affiliates directory
- June 18, 2025: Standardized sidebar typography, spacing, and layout consistency across all themes with enhanced gradient backgrounds
- June 18, 2025: Added Steel and Gold themes to complete 6-theme system with corresponding sidebar gradients and color schemes
- June 18, 2025: Enhanced all themes with transparency effects and high contrast text for improved readability and modern glass-morphism design
- June 18, 2025: Implemented collapsible sidebar with toggle button and adjusted header height for better logo integration
- June 18, 2025: Updated theme color schemes - Gold (modern gold/white/beige), Old School (black/white), Dark (navy/white/blue), Modern (dark slate/teal)
- June 18, 2025: Verified all 6 themes (Dark, Light, Modern, Old School, Steel, Gold) are available across all page templates with consistent theme selector functionality
- June 18, 2025: Implemented comprehensive mobile responsiveness across all pages with hamburger menu functionality, mobile overlay, and responsive layouts
- June 18, 2025: Added hero section to dashboard with DNA helix SVG design and sections/pages overview in colorful cards
- June 18, 2025: Fixed sidebar icon layout with proper 2-column structure (icon | text) that collapses to icon-only when minimized
- June 18, 2025: Removed duplicate hamburger icons, keeping only the toggle button in sidebar header
- June 18, 2025: Created unique login page theme with purple gradient background, floating animations, and hero SVG image
- June 18, 2025: Enhanced login page with glass-morphism design, animated background shapes, and improved form styling
- June 18, 2025: Standardized all icons, fonts, and sizes across all page templates with consistent 18px icons and 0.9rem text
- June 18, 2025: Updated hero images with advanced admin system visualizations for both dashboard and login pages
- June 18, 2025: Ensured complete consistency across all page templates: sidebar buttons, navigation, logout links, and dashboard access
- June 18, 2025: Applied consistent 2-column icon/text layout that collapses properly when sidebar is minimized across all pages
- June 18, 2025: Removed duplicate hamburger menu toggles from top of all pages, keeping only the sidebar header toggle button
- June 18, 2025: Created comprehensive documentation system with DATA_DICTIONARY.md and CODE_DICTIONARY.md for development team reference
- June 18, 2025: Added documentation navigation with 5 complete reference guides and markdown download functionality
- June 18, 2025: Implemented responsive sidebar width control with slider, session persistence, and consistent resizing across all pages
- June 18, 2025: Created Site Navigation & Definitions document with complete UI reference and user flow documentation
- June 18, 2025: Implemented comprehensive user management system with admin-only access for @ziqsy.com and @technicologyltd.com domains
- June 18, 2025: Added user-specific preferences storage (sidebar width, theme) with database persistence and session management
- June 18, 2025: Removed demo credentials from login page and implemented secure password generation for new users
- June 18, 2025: Created resizable container system with responsive elements that adapt to changed container dimensions
- June 18, 2025: Replaced sidebar width slider control with intuitive drag-to-resize functionality on sidebar edge
- June 18, 2025: Applied drag resize universally across all page templates for consistent user experience
- June 18, 2025: Moved dashboard, documentation, and user management to top navigation panel across all pages, removed from sidebar for cleaner design
- June 18, 2025: Fixed template error in admin_users.html preventing page loading and added proper datetime handling
- June 18, 2025: Completed top navigation implementation with icon-only buttons in top-right corner, applied CSS styling, and removed old navigation items from all page sidebars
- June 18, 2025: Comprehensive mobile responsiveness review and implementation - enhanced responsive design for all pages, improved mobile navigation, optimized layouts for mobile devices, and ensured consistency across all templates
- June 20, 2025: Fixed critical mobile display issues - replaced top header bar with floating navigation icons, made logo clickable for home navigation, resolved JavaScript variable conflicts, and optimized mobile viewport handling
- June 20, 2025: Enhanced AI Dataset Assistant with real LLM integration - added OpenAI and Anthropic API support, LLM model dropdown selection, dataset context provision to AI, and comprehensive analysis capabilities
- June 18, 2025: Fixed critical mobile display issues - implemented fixed header positioning, proper viewport meta tag, prevented horizontal scroll, optimized touch interactions, and enhanced mobile-specific breakpoints for phones and small screens

## User Preferences

Preferred communication style: Simple, everyday language.