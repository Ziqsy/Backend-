# Ziqsy Internal Admin System - Site Navigation & Definitions

## Navigation Structure

### Primary Navigation (Sidebar)
The sidebar provides hierarchical access to all system functions and is consistently available across all pages.

#### Header Section
- **Ziqsy Logo**: Returns to dashboard when clicked
- **Hamburger Menu**: Toggles sidebar collapse/expand
- **Dashboard Button**: Direct access to main dashboard

#### Content Sections
- **Categories Header**: Visual separator for organizational content
- **New Section Button**: Creates new organizational sections
- **Add Page Button**: Adds new pages to existing sections

#### Section Management
- **Section Items**: Expandable containers for related pages
- **Page Links**: Direct navigation to specific page types
- **Page Icons**: Visual indicators for page functionality

#### Footer Controls
- **Theme Selector**: 6 available themes (Dark, Light, Modern, Old School, Steel, Gold)
- **Logout Button**: Secure session termination

### Page Types & Functions

#### Dashboard (Home)
**Purpose**: Central hub providing system overview and quick access
**Features**:
- Hero section with system introduction
- Visual sections/pages overview with cards
- Statistics and usage metrics
- Quick action buttons

#### Page Types

**1. Link Operations**
- **Icon**: Link symbol (🔗)
- **Purpose**: Category-based navigation system
- **Features**: Card-based display, filtering, bulk operations
- **Use Cases**: External resource management, bookmark organization

**2. List Pages**
- **Icon**: List symbol (📄)
- **Purpose**: Flat table structure with CRUD operations
- **Features**: Inline editing, row management, data export
- **Use Cases**: Simple data tables, contact lists, inventory

**3. Dataset Pages**
- **Icon**: Chart symbol (📊)
- **Purpose**: Advanced data analysis and visualization
- **Features**: Charts, AI assistant, statistical analysis
- **Use Cases**: Data analysis, reporting, business intelligence

**4. Repository Pages**
- **Icon**: Folder symbol (📁)
- **Purpose**: File and cloud folder management
- **Features**: File browser, AI descriptions, user notes
- **Use Cases**: Document management, file organization

### URL Structure

```
/ → Dashboard (main page)
/login → Authentication page
/page/{id} → Specific page view (type determined by page.page_type)
/api/page/{id}/data → Data API endpoint
/api/repository/files → File management API
/health → System health check
```

### Access Control

#### Authentication
- Email/password authentication required
- Session-based user management
- Automatic logout on session expiry

#### Authorization
- Single-user system (admin access)
- No role-based permissions currently implemented
- All authenticated users have full system access

## Page Definitions

### Dashboard Features

**Hero Section**
- Welcome message with system branding
- DNA helix SVG visualization
- System purpose description

**Overview Cards**
- Section count with creation button
- Page count with management links
- Color-coded by page type
- Direct navigation to items

**Quick Actions**
- Create new sections
- Add pages to sections
- Access recent items

### Page Management Interface

**Content Header**
- Page title with type badge
- Action buttons (Export, Add Row, etc.)
- Upload form for data import
- Breadcrumb navigation

**Data Display Areas**
- Table view for structured data
- Card view for link operations
- Chart view for datasets
- File tree for repositories

**Interactive Elements**
- Inline editing capabilities
- Sorting and filtering
- Pagination for large datasets
- Search functionality

### Theme System

**Available Themes**
1. **Dark**: Navy background, white text, teal accents
2. **Light**: White background, dark text, blue accents
3. **Modern**: Dark slate background, teal highlights
4. **Old School**: Black/white classic design
5. **Steel**: Gray metallic theme with blue accents
6. **Gold**: Modern gold/white/beige palette

**Theme Persistence**
- Settings stored in browser localStorage
- Automatic theme application on page load
- Consistent across all pages and sessions

### Mobile Responsiveness

**Breakpoints**
- Desktop: > 768px (full sidebar visible)
- Tablet: 768px - 480px (collapsible sidebar)
- Mobile: < 480px (overlay sidebar)

**Mobile Features**
- Hamburger menu activation
- Touch-friendly buttons and controls
- Responsive table layouts
- Mobile-optimized forms

### Data Flow Patterns

**File Upload Process**
1. User selects file via upload form
2. File validated for type and size
3. Data processed and table created
4. Success confirmation displayed
5. Page refreshed with new data

**Navigation Flow**
1. User accesses sidebar navigation
2. Selects section or page
3. System routes to appropriate view
4. Page-specific interface loads
5. Data and features become available

**Theme Change Flow**
1. User selects theme from dropdown
2. CSS variables updated via JavaScript
3. Theme preference saved to localStorage
4. All page elements adapt to new theme
5. Selection persists across sessions

### Error Handling

**User-Facing Errors**
- File upload failures with clear messages
- Database connection issues with fallback
- Invalid data format notifications
- Session expiry warnings

**Technical Errors**
- Graceful degradation for missing features
- API endpoint error responses
- Database transaction rollbacks
- Temporary storage fallbacks

### Performance Considerations

**Optimization Features**
- Lazy loading for large datasets
- Pagination to limit data transfer
- Client-side caching for static content
- Debounced search and filter operations

**Resource Management**
- Connection pooling for database
- Automatic cleanup of temporary files
- Memory management for large uploads
- Efficient query patterns

### Security Features

**Data Protection**
- Password hashing with Werkzeug
- SQL injection prevention via ORM
- File upload type restrictions
- Session management security

**Access Security**
- HTTPS enforcement (production)
- CSRF protection on forms
- Secure session configuration
- Input sanitization and validation

### Integration Points

**External Services**
- OpenAI API for AI descriptions (optional)
- Cloud storage for file repositories
- Email services for notifications (future)
- Analytics tracking (configurable)

**API Endpoints**
- RESTful data access
- JSON response formats
- Authentication required
- Error handling and logging

### Maintenance Access

**Administrative Functions**
- Database schema management
- User account administration
- System configuration updates
- Backup and restore operations

**Monitoring Capabilities**
- Health check endpoints
- Performance metrics
- Error logging and tracking
- Usage analytics and reporting

### Future Expansion

**Planned Features**
- Multi-user support with roles
- Advanced AI integration
- Real-time collaboration
- Enhanced reporting tools

**Architecture Scalability**
- Modular page type system
- Plugin architecture potential
- API-first design approach
- Cloud deployment readiness