from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased for MySQL
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sidebar_width = db.Column(db.Integer, default=280)
    theme_preference = db.Column(db.String(20), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_domain_allowed(self):
        allowed_domains = ['@ziqsy.com', '@technicologyltd.com']
        return any(self.email.endswith(domain) for domain in allowed_domains)

class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to pages
    pages = db.relationship('Page', backref='section', lazy=True, cascade='all, delete-orphan')

class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    page_type = db.Column(db.String(50), nullable=False)  # link_operations, list, dataset, repository
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    table_name = db.Column(db.String(100), nullable=True)  # For dynamic tables
    config = db.Column(db.Text, nullable=True)  # JSON config for page-specific settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_config(self):
        if self.config:
            return json.loads(self.config)
        return {}

    def set_config(self, config_dict):
        self.config = json.dumps(config_dict)

class DynamicTable(db.Model):
    __tablename__ = 'dynamic_table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String(100), unique=True, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    columns_info = db.Column(db.Text, nullable=True)  # JSON info about columns
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_columns_info(self):
        if self.columns_info:
            return json.loads(self.columns_info)
        return {}

    def set_columns_info(self, columns_dict):
        self.columns_info = json.dumps(columns_dict)

class FileRepository(db.Model):
    __tablename__ = 'file_repository'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ai_description = db.Column(db.Text, nullable=True)  # AI-generated description
    user_notes = db.Column(db.Text, nullable=True)  # User notes about the file/folder
    file_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    is_folder = db.Column(db.Boolean, default=False)  # True if this is a folder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CloudFolder(db.Model):
    __tablename__ = 'cloud_folder'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    folder_path = db.Column(db.String(1000), nullable=False)
    folder_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserInvitation(db.Model):
    __tablename__ = 'user_invitation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(255), nullable=False)  # Reduced for MySQL
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)


