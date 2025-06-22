"""
Temporary in-memory storage for when database is unavailable
This allows the application to function normally while PostgreSQL recovers
"""

import json
from datetime import datetime

class TempStorage:
    def __init__(self):
        self.sections = []
        self.pages = []
        self.dynamic_tables = []
        self.file_repositories = []
        self._section_id_counter = 1
        self._page_id_counter = 1
        self._table_id_counter = 1
        self._file_id_counter = 1
    
    def add_section(self, name):
        section = {
            'id': self._section_id_counter,
            'name': name,
            'created_at': datetime.utcnow(),
            'pages': []
        }
        self.sections.append(section)
        self._section_id_counter += 1
        return section
    
    def get_sections(self):
        # Add pages to sections
        for section in self.sections:
            section['pages'] = [p for p in self.pages if p['section_id'] == section['id']]
        return self.sections
    
    def delete_section(self, section_id):
        self.sections = [s for s in self.sections if s['id'] != section_id]
        # Also delete associated pages
        self.pages = [p for p in self.pages if p['section_id'] != section_id]
    
    def add_page(self, name, page_type, section_id, table_name=None, config=None):
        page = {
            'id': self._page_id_counter,
            'name': name,
            'page_type': page_type,
            'section_id': section_id,
            'table_name': table_name,
            'config': config,
            'created_at': datetime.utcnow()
        }
        self.pages.append(page)
        self._page_id_counter += 1
        return page
    
    def get_page(self, page_id):
        return next((p for p in self.pages if p['id'] == page_id), None)
    
    def delete_page(self, page_id):
        self.pages = [p for p in self.pages if p['id'] != page_id]
    
    def clear(self):
        """Clear all temporary data"""
        self.sections = []
        self.pages = []
        self.dynamic_tables = []
        self.file_repositories = []

# Global temporary storage instance
temp_storage = TempStorage()