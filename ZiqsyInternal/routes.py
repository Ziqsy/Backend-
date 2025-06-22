from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Section, Page, DynamicTable, FileRepository, CloudFolder, UserInvitation
from temp_storage import temp_storage
from datetime import datetime, timedelta
from utils import (
    create_dynamic_table, 
    insert_csv_data, 
    get_dynamic_table_data,
    update_dynamic_table_row,
    delete_dynamic_table_row,
    export_table_to_csv,
    process_uploaded_file
)
import os
import markdown
from datetime import datetime
from ai_service import generate_file_description, generate_folder_description, get_available_models, analyze_dataset_with_ai
import pandas as pd
import json

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = User.query.filter_by(email=email, is_active=True).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                session['sidebar_width'] = user.sidebar_width
                session['theme_preference'] = user.theme_preference
                
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials', 'error')
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            flash('Login system temporarily unavailable', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

# Main dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        sections = Section.query.all()
    except Exception as e:
        app.logger.error(f"Database error in dashboard: {e}")
        sections = temp_storage.get_sections()
        flash('Using temporary storage while database recovers.', 'info')
    
    return render_template('dashboard.html', sections=sections)

# Section management
@app.route('/create_section', methods=['POST'])
def create_section():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    if name:
        try:
            section = Section(name=name)
            db.session.add(section)
            db.session.commit()
            flash(f'Section "{name}" created successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Database error creating section: {e}")
            # Use temporary storage as fallback
            temp_storage.add_section(name)
            flash(f'Section "{name}" created in temporary storage!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_section/<int:section_id>')
def delete_section(section_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        section = Section.query.get_or_404(section_id)
        db.session.delete(section)
        db.session.commit()
        flash(f'Section "{section.name}" deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Database error deleting section: {e}")
        temp_storage.delete_section(section_id)
        flash('Section deleted from temporary storage!', 'success')
    
    return redirect(url_for('dashboard'))

# Page management
@app.route('/create_page', methods=['POST'])
def create_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    page_type = request.form.get('page_type')
    section_id = request.form.get('section_id')
    
    if name and page_type and section_id:
        try:
            page = Page(name=name, page_type=page_type, section_id=int(section_id))
            db.session.add(page)
            db.session.commit()
            flash(f'Page "{name}" created successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Database error creating page: {e}")
            # Use temporary storage as fallback
            temp_storage.add_page(name, page_type, int(section_id))
            flash(f'Page "{name}" created in temporary storage!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_page/<int:page_id>')
def delete_page(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        page = Page.query.get_or_404(page_id)
        db.session.delete(page)
        db.session.commit()
        flash(f'Page "{page.name}" deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Database error deleting page: {e}")
        temp_storage.delete_page(page_id)
        flash('Page deleted from temporary storage!', 'success')
    
    return redirect(url_for('dashboard'))

# Page views
@app.route('/page/<int:page_id>')
def view_page(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        page = Page.query.get_or_404(page_id)
        sections = Section.query.all()  # For sidebar
    except Exception as e:
        app.logger.error(f"Database error in view_page: {e}")
        # Use temporary storage as fallback
        page = temp_storage.get_page(page_id)
        sections = temp_storage.get_sections()
        
        if not page:
            flash('Page not found in temporary storage.', 'error')
            return redirect(url_for('dashboard'))
        
        flash('Viewing page from temporary storage.', 'info')
    
    # Check page type properly for both dict and object types
    page_type = None
    if isinstance(page, dict):
        page_type = page.get('page_type')
    elif hasattr(page, 'page_type'):
        page_type = page.page_type
    
    if page_type == 'link_operations':
        return render_template('page_link_operations.html', page=page, sections=sections)
    elif page_type == 'list':
        return render_template('page_list.html', page=page, sections=sections)
    elif page_type == 'dataset':
        return render_template('page_dataset.html', page=page, sections=sections)
    elif page_type == 'repository':
        # Get cloud folder for repository page
        cloud_folder = None
        try:
            cloud_folder = CloudFolder.query.filter_by(page_id=page_id).first()
        except Exception as e:
            app.logger.error(f"Error loading cloud folder: {e}")
        
        return render_template('page_repository.html', page=page, sections=sections, cloud_folder=cloud_folder)
    
    return redirect(url_for('dashboard'))

# File upload handling
@app.route('/upload_file/<int:page_id>', methods=['POST'])
def upload_file(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        page = Page.query.get_or_404(page_id)
    except Exception as e:
        app.logger.error(f"Database error in upload_file: {e}")
        page = temp_storage.get_page(page_id)
        if not page:
            flash('Page not found.', 'error')
            return redirect(url_for('dashboard'))
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('view_page', page_id=page_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('view_page', page_id=page_id))
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the uploaded file based on page type
            result = process_uploaded_file(filepath, page)
            if result['success']:
                flash(result['message'], 'success')
            else:
                flash(result['message'], 'error')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return redirect(url_for('view_page', page_id=page_id))

# API endpoints for dynamic data
@app.route('/api/page/<int:page_id>/data', methods=['GET'])
def get_page_data(page_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        page = Page.query.get_or_404(page_id)
        table_name = page.table_name
    except Exception as e:
        app.logger.error(f"Database error in get_page_data: {e}")
        page = temp_storage.get_page(page_id)
        if not page:
            return jsonify([])
        table_name = page.get('table_name') if isinstance(page, dict) else None
    
    try:
        if table_name:
            data = get_dynamic_table_data(table_name)
            return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error loading table data: {e}")
        return jsonify([])
    
    return jsonify([])

@app.route('/api/page/<int:page_id>/data', methods=['POST'])
def update_page_data(page_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    page = Page.query.get_or_404(page_id)
    data = request.json
    
    try:
        if data and data.get('action') == 'update':
            result = update_dynamic_table_row(page.table_name, data['id'], data['values'])
        elif data and data.get('action') == 'delete':
            result = delete_dynamic_table_row(page.table_name, data['id'])
        else:
            result = {'success': False, 'message': 'Invalid action'}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/export/<int:page_id>')
def export_page_data(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = Page.query.get_or_404(page_id)
    
    if page.table_name:
        try:
            filepath = export_table_to_csv(page.table_name, page.name)
            return send_file(filepath, as_attachment=True, download_name=f'{page.name}_export.csv')
        except Exception as e:
            flash(f'Error exporting data: {str(e)}', 'error')
    
    return redirect(url_for('view_page', page_id=page_id))

# Repository management
@app.route('/api/repository/<int:page_id>/files', methods=['GET', 'POST'])
def manage_repository_files(page_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    page = Page.query.get_or_404(page_id)
    
    if request.method == 'POST':
        data = request.json or {}
        file_repo = FileRepository(
            page_id=page_id,
            file_path=data.get('file_path', ''),
            file_name=data.get('file_name', ''),
            description=data.get('description', ''),
            file_url=data.get('file_url', ''),
            tags=data.get('tags', '')
        )
        db.session.add(file_repo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'File added successfully'})
    
    files = FileRepository.query.filter_by(page_id=page_id).all()
    return jsonify([{
        'id': f.id,
        'file_path': f.file_path,
        'file_name': f.file_name,
        'description': f.description,
        'file_url': f.file_url,
        'tags': f.tags,
        'created_at': f.created_at.isoformat()
    } for f in files])

@app.route('/api/repository/file/<int:file_id>', methods=['PUT', 'DELETE'])
def manage_repository_file(file_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    file_repo = FileRepository.query.get_or_404(file_id)
    
    if request.method == 'PUT':
        data = request.json
        file_repo.description = data.get('description', file_repo.description)
        file_repo.tags = data.get('tags', file_repo.tags)
        file_repo.file_url = data.get('file_url', file_repo.file_url)
        db.session.commit()
        return jsonify({'success': True, 'message': 'File updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(file_repo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'File deleted successfully'})

# Repository cloud folder management
@app.route('/page/<int:page_id>/set-cloud-folder', methods=['POST'])
def set_cloud_folder(page_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        page = Page.query.get_or_404(page_id)
        if page.page_type != 'repository':
            flash('Invalid page type', 'error')
            return redirect(url_for('view_page', page_id=page_id))
        
        folder_path = request.form.get('folder_path')
        folder_name = request.form.get('folder_name')
        
        if not folder_path or not folder_name:
            flash('Folder path and name are required', 'error')
            return redirect(url_for('view_page', page_id=page_id))
        
        # Check if cloud folder already exists for this page
        cloud_folder = CloudFolder.query.filter_by(page_id=page_id).first()
        if cloud_folder:
            cloud_folder.folder_path = folder_path
            cloud_folder.folder_name = folder_name
        else:
            cloud_folder = CloudFolder(
                page_id=page_id,
                folder_path=folder_path,
                folder_name=folder_name
            )
            db.session.add(cloud_folder)
        
        db.session.commit()
        flash('Cloud folder set successfully', 'success')
        
    except Exception as e:
        app.logger.error(f"Error setting cloud folder: {e}")
        flash('Error setting cloud folder', 'error')
    
    return redirect(url_for('view_page', page_id=page_id))

@app.route('/api/repository/<int:page_id>/files')
def get_repository_files(page_id):
    app.logger.info(f"Repository files API called for page {page_id}")
    
    # Direct file scanning without database dependency
    import os
    
    try:
        folder_path = '/home/runner/workspace'
        files = []
        
        if os.path.exists(folder_path):
            items = os.listdir(folder_path)
            app.logger.info(f"Found {len(items)} items in {folder_path}")
            
            for item in sorted(items):
                # Skip hidden files and system files
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(folder_path, item)
                is_folder = os.path.isdir(item_path)
                
                # Get file size if it's a file
                size = None
                if not is_folder:
                    try:
                        size = os.path.getsize(item_path)
                    except OSError:
                        size = 0
                
                files.append({
                    'name': item,
                    'path': item_path,
                    'is_folder': is_folder,
                    'size': size,
                    'url': f"file://{item_path}"
                })
            
            app.logger.info(f"Successfully processed {len(files)} files/folders")
            
            # Sort files: folders first, then files, both alphabetically
            files.sort(key=lambda x: (not x['is_folder'], x['name'].lower()))
            
            return jsonify({'files': files})
        else:
            return jsonify({'error': f'Folder {folder_path} does not exist'})
            
    except Exception as e:
        app.logger.error(f"Error scanning files: {e}")
        return jsonify({'error': f'Scanning error: {str(e)}'})


@app.route('/api/repository/file/ai-description', methods=['POST'])
def get_ai_description():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        file_name = data.get('file_name')
        is_folder = data.get('is_folder', False)
        
        if is_folder:
            description = generate_folder_description(file_path, file_name, [])
        else:
            file_extension = file_name.split('.')[-1] if '.' in file_name else ''
            description = generate_file_description(file_path, file_name, file_extension)
        
        return jsonify({'description': description})
        
    except Exception as e:
        app.logger.error(f"Error generating AI description: {e}")
        return jsonify({'description': 'Unable to generate description'})

@app.route('/api/repository/file/notes', methods=['POST'])
def save_file_notes():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        file_path = data.get('file_path')
        file_name = data.get('file_name')
        user_notes = data.get('user_notes', '')
        is_folder = data.get('is_folder', False)
        
        # Check if file record exists
        file_record = FileRepository.query.filter_by(
            page_id=page_id,
            file_path=file_path
        ).first()
        
        if file_record:
            file_record.user_notes = user_notes
        else:
            file_record = FileRepository(
                page_id=page_id,
                file_path=file_path,
                file_name=file_name,
                user_notes=user_notes,
                is_folder=is_folder
            )
            db.session.add(file_record)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error saving file notes: {e}")
        return jsonify({'error': 'Failed to save notes'}), 500

@app.route('/api/ai/models')
def get_ai_models():
    """Get available AI models"""
    try:
        models = get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        print(f"Error getting AI models: {e}")
        return jsonify({'models': {}, 'error': str(e)})

@app.route('/api/ai/analyze-dataset', methods=['POST'])
def ai_analyze_dataset():
    """Analyze dataset with AI"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        question = data.get('question')
        model_id = data.get('model_id', 'gpt-4o')
        
        if not page_id or not question:
            return jsonify({'error': 'Page ID and question are required'})
        
        # Get the page and its data
        page = Page.query.get_or_404(page_id)
        
        if not page.table_name:
            return jsonify({'error': 'No dataset available for this page'})
        
        # Get dataset data
        dataset_data = get_dynamic_table_data(page.table_name)
        
        if not dataset_data:
            return jsonify({'error': 'Dataset is empty'})
        
        # Convert to DataFrame for analysis
        import pandas as pd
        df = pd.DataFrame(dataset_data)
        
        # Analyze with AI
        result = analyze_dataset_with_ai(df, question, model_id)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in AI dataset analysis: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'})
        
    except Exception as e:
        app.logger.error(f"Error saving file notes: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Documentation routes
@app.route('/docs')
def documentation():
    """Main documentation hub page"""
    try:
        sections = Section.query.all()
    except:
        sections = temp_storage.get_sections()
    return render_template('documentation.html', sections=sections)

@app.route('/docs/<doc_type>')
def view_documentation(doc_type):
    """View specific documentation"""
    doc_files = {
        'data-dictionary': 'DATA_DICTIONARY.md',
        'code-dictionary': 'CODE_DICTIONARY.md',
        'deployment-guide': 'DEPLOYMENT_GUIDE.md',
        'troubleshooting': 'TROUBLESHOOTING.md',
        'site-navigation': 'SITE_NAVIGATION.md'
    }
    
    if doc_type not in doc_files:
        return "Documentation not found", 404
    
    file_path = doc_files[doc_type]
    if not os.path.exists(file_path):
        return "Documentation file not found", 404
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'codehilite'])
    
    try:
        sections = Section.query.all()
    except:
        sections = temp_storage.get_sections()
    
    return render_template('document_viewer.html', 
                         content=html_content, 
                         doc_type=doc_type,
                         doc_title=doc_type.replace('-', ' ').title(),
                         sections=sections)

@app.route('/docs/<doc_type>/download')
def download_documentation(doc_type):
    """Download documentation as markdown file"""
    doc_files = {
        'data-dictionary': 'DATA_DICTIONARY.md',
        'code-dictionary': 'CODE_DICTIONARY.md',
        'deployment-guide': 'DEPLOYMENT_GUIDE.md',
        'troubleshooting': 'TROUBLESHOOTING.md',
        'site-navigation': 'SITE_NAVIGATION.md'
    }
    
    if doc_type not in doc_files:
        return "Documentation not found", 404
    
    file_path = doc_files[doc_type]
    if not os.path.exists(file_path):
        return "Documentation file not found", 404
    
    filename = f"ziqsy_{doc_type}_{datetime.now().strftime('%Y%m%d')}.md"
    
    return send_file(file_path, 
                    as_attachment=True, 
                    download_name=filename,
                    mimetype='text/markdown')

# User preference management
@app.route('/api/sidebar/width', methods=['POST'])
def update_sidebar_width():
    """Update sidebar width preference"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        width = data.get('width', 280)
        
        # Validate width (between 200px and 500px)
        if not isinstance(width, (int, float)) or width < 200 or width > 500:
            return jsonify({'error': 'Invalid width value'}), 400
        
        # Update session
        session['sidebar_width'] = width
        
        # Update user preference in database
        user = User.query.get(session['user_id'])
        if user:
            user.sidebar_width = width
            db.session.commit()
        
        return jsonify({'success': True, 'width': width})
    
    except Exception as e:
        app.logger.error(f"Error updating sidebar width: {e}")
        return jsonify({'error': 'Failed to update width'}), 500

@app.route('/api/sidebar/width', methods=['GET'])
def get_sidebar_width():
    """Get current sidebar width preference"""
    if 'user_id' in session:
        width = session.get('sidebar_width', 280)
    else:
        width = 280  # Default for non-logged users
    return jsonify({'width': width})

@app.route('/api/theme', methods=['POST'])
def update_theme_preference():
    """Update theme preference"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        theme = data.get('theme', 'dark')
        
        valid_themes = ['dark', 'light', 'modern', 'oldschool', 'steel', 'gold']
        if theme not in valid_themes:
            return jsonify({'error': 'Invalid theme'}), 400
        
        # Update session
        session['theme_preference'] = theme
        
        # Update user preference in database
        user = User.query.get(session['user_id'])
        if user:
            user.theme_preference = theme
            db.session.commit()
        
        return jsonify({'success': True, 'theme': theme})
    
    except Exception as e:
        app.logger.error(f"Error updating theme: {e}")
        return jsonify({'error': 'Failed to update theme'}), 500

# Admin user management
@app.route('/admin/users')
def admin_users():
    """Admin-only user management page"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        invitations = UserInvitation.query.filter_by(is_used=False).order_by(UserInvitation.created_at.desc()).all()
        sections = Section.query.all()
    except:
        users = []
        invitations = []
        sections = temp_storage.get_sections()
    
    return render_template('admin_users.html', users=users, invitations=invitations, sections=sections)

@app.route('/admin/invite-user', methods=['POST'])
def invite_user():
    """Send invitation to new user"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        # Validate email domain
        allowed_domains = ['@ziqsy.com', '@technicologyltd.com']
        if not any(email.endswith(domain) for domain in allowed_domains):
            return jsonify({'error': 'Email must be from @ziqsy.com or @technicologyltd.com domain'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Check if invitation already sent
        existing_invitation = UserInvitation.query.filter_by(email=email, is_used=False).first()
        if existing_invitation:
            return jsonify({'error': 'Invitation already sent to this email'}), 400
        
        # Generate secure token and password
        import secrets
        import string
        
        token = secrets.token_urlsafe(32)
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Create user account immediately
        new_user = User(
            email=email,
            is_admin=False,
            is_active=True
        )
        new_user.set_password(temp_password)
        db.session.add(new_user)
        
        # Create invitation record
        invitation = UserInvitation(
            email=email,
            token=token,
            created_by=session['user_id'],
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(invitation)
        db.session.commit()
        
        # In a real implementation, you would send an email here
        # For demo purposes, we'll return the credentials
        return jsonify({
            'success': True,
            'message': 'User account created successfully',
            'email': email,
            'temporary_password': temp_password,
            'note': 'In production, these credentials would be sent via email'
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error inviting user: {e}")
        return jsonify({'error': 'Failed to create user account'}), 500

@app.route('/admin/toggle-user/<int:target_user_id>', methods=['POST'])
def toggle_user_status(target_user_id):
    """Toggle user active status"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user = User.query.get_or_404(target_user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == session['user_id']:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({'success': True, 'message': f'User {status} successfully'})
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error toggling user status: {e}")
        return jsonify({'error': 'Failed to update user status'}), 500

@app.route('/admin/reset-password/<int:target_user_id>', methods=['POST'])
def reset_user_password(target_user_id):
    """Reset user password"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user = User.query.get_or_404(target_user_id)
        
        # Generate new password
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully',
            'new_password': new_password,
            'note': 'In production, this would be sent via email'
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error resetting password: {e}")
        return jsonify({'error': 'Failed to reset password'}), 500
