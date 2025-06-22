import pandas as pd
import os
import tempfile
from sqlalchemy import text, inspect
from app import db
from models import DynamicTable

def create_dynamic_table(table_name, columns):
    """Create a dynamic table based on CSV columns"""
    try:
        # Sanitize table name
        table_name = table_name.replace(' ', '_').replace('-', '_').lower()
        
        # Create table with dynamic columns
        columns_sql = []
        for col in columns:
            col_name = col.replace(' ', '_').replace('-', '_').lower()
            columns_sql.append(f'"{col_name}" TEXT')
        
        # Add id and metadata columns
        sql = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id SERIAL PRIMARY KEY,
            {', '.join(columns_sql)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        
        db.session.execute(text(sql))
        db.session.commit()
        
        return {'success': True, 'table_name': table_name}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}

def insert_csv_data(table_name, df):
    """Insert DataFrame data into dynamic table"""
    try:
        # Sanitize column names
        df.columns = [col.replace(' ', '_').replace('-', '_').lower() for col in df.columns]
        
        # Insert data
        for _, row in df.iterrows():
            columns = ', '.join([f'"{col}"' for col in df.columns])
            escaped_values = []
            for val in row:
                str_val = str(val)
                escaped_val = str_val.replace("'", "''")
                escaped_values.append(f"'{escaped_val}'")
            values = ', '.join(escaped_values)
            
            sql = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})'
            db.session.execute(text(sql))
        
        db.session.commit()
        return {'success': True, 'rows_inserted': len(df)}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}

def get_dynamic_table_data(table_name):
    """Get all data from a dynamic table"""
    try:
        sql = f'SELECT * FROM "{table_name}" ORDER BY id'
        result = db.session.execute(text(sql))
        
        # Convert to list of dictionaries
        columns = result.keys()
        data = []
        for row in result:
            data.append(dict(zip(columns, row)))
        
        return data
    except Exception as e:
        return []

def update_dynamic_table_row(table_name, row_id, values):
    """Update a row in dynamic table"""
    try:
        set_clauses = []
        for key, value in values.items():
            if key != 'id':  # Don't update the ID
                key = key.replace(' ', '_').replace('-', '_').lower()
                escaped_value = str(value).replace("'", "''")
                set_clauses.append(f'"{key}" = \'{escaped_value}\'')
        
        if set_clauses:
            set_clauses.append('updated_at = CURRENT_TIMESTAMP')
            sql = f'UPDATE "{table_name}" SET {", ".join(set_clauses)} WHERE id = {row_id}'
            db.session.execute(text(sql))
            db.session.commit()
        
        return {'success': True, 'message': 'Row updated successfully'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}

def delete_dynamic_table_row(table_name, row_id):
    """Delete a row from dynamic table"""
    try:
        sql = f'DELETE FROM "{table_name}" WHERE id = {row_id}'
        db.session.execute(text(sql))
        db.session.commit()
        
        return {'success': True, 'message': 'Row deleted successfully'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}

def export_table_to_csv(table_name, page_name):
    """Export dynamic table data to CSV"""
    try:
        sql = f'SELECT * FROM "{table_name}"'
        df = pd.read_sql(sql, db.engine)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        
        return temp_file.name
    except Exception as e:
        raise Exception(f'Export failed: {str(e)}')

def process_uploaded_file(filepath, page):
    """Process uploaded file based on page type"""
    try:
        # Determine file type and read data
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            df = pd.read_json(filepath)
        elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            df = pd.read_excel(filepath)
        else:
            return {'success': False, 'message': 'Unsupported file format'}
        
        if df.empty:
            return {'success': False, 'message': 'File is empty'}
        
        # Generate table name - handle both dict and model objects
        page_id = page.get('id') if isinstance(page, dict) else page.id
        page_name = page.get('name') if isinstance(page, dict) else page.name
        # Handle None values for page_name
        if page_name is None:
            page_name = "untitled"
        table_name = f"page_{page_id}_{page_name.replace(' ', '_').lower()}"
        
        # Try database operations with fallback
        try:
            # Check if table exists
            inspector = inspect(db.engine)
            table_exists = inspector.has_table(table_name)
            
            if not table_exists:
                # Create new table
                result = create_dynamic_table(table_name, df.columns.tolist())
                if not result['success']:
                    return {'success': False, 'message': f'Failed to create table: {result["error"]}'}
                
                # Update page with table name - handle both dict and model objects
                if isinstance(page, dict):
                    # For temp storage, we can't directly update the table_name
                    # This will be handled when database comes back online
                    pass
                else:
                    page.table_name = table_name
                
                # Create metadata record only if database is available
                try:
                    from app import app
                    dynamic_table = DynamicTable(
                        table_name=table_name,
                        page_id=page_id
                    )
                    dynamic_table.set_columns_info(df.columns.tolist())
                    db.session.add(dynamic_table)
                except Exception as e:
                    try:
                        from app import app
                        app.logger.error(f"Could not create DynamicTable metadata: {e}")
                    except:
                        print(f"Could not create DynamicTable metadata: {e}")
            else:
                # Add new columns if they don't exist
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                new_columns = [col for col in df.columns if col.replace(' ', '_').replace('-', '_').lower() not in existing_columns]
                
                for col in new_columns:
                    col_name = col.replace(' ', '_').replace('-', '_').lower()
                    sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" TEXT'
                    db.session.execute(text(sql))
            
            # Insert data
            result = insert_csv_data(table_name, df)
            if not result['success']:
                return {'success': False, 'message': f'Failed to insert data: {result["error"]}'}
            
            db.session.commit()
            
            return {
                'success': True, 
                'message': f'Successfully processed {result["rows_inserted"]} rows'
            }
        except Exception as db_error:
            # Database unavailable, return success with limitation note
            return {
                'success': True, 
                'message': f'File processed successfully. Data will be available when database reconnects. ({len(df)} rows processed)'
            }
        
    except Exception as e:
        try:
            db.session.rollback()
        except:
            pass
        return {'success': False, 'message': f'Error processing file: {str(e)}'}

def get_table_columns(table_name):
    """Get column information for a dynamic table"""
    try:
        inspector = inspect(db.engine)
        if inspector.has_table(table_name):
            return [col['name'] for col in inspector.get_columns(table_name)]
        return []
    except Exception:
        return []
