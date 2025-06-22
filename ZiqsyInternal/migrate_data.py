import csv
import mysql.connector
from datetime import datetime
import os

# MySQL connection configuration
MYSQL_CONFIG = {
    'host': 'your-hostinger-mysql-host',
    'user': 'your-mysql-username',
    'password': 'your-mysql-password',
    'database': 'ziqsy_internal',
    'charset': 'utf8mb4'
}

def connect_mysql():
    return mysql.connector.connect(**MYSQL_CONFIG)

def migrate_table_data(csv_file, table_name, column_mapping):
    """Migrate data from CSV to MySQL table"""
    conn = connect_mysql()
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Convert data types for MySQL
            converted_row = {}
            for csv_col, mysql_col in column_mapping.items():
                value = row.get(csv_col, '')
                
                # Handle boolean conversion
                if value in ['t', 'true', 'True', '1']:
                    converted_row[mysql_col] = True
                elif value in ['f', 'false', 'False', '0']:
                    converted_row[mysql_col] = False
                elif value == '' or value == 'NULL':
                    converted_row[mysql_col] = None
                else:
                    converted_row[mysql_col] = value
            
            # Build INSERT query
            columns = list(converted_row.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            try:
                cursor.execute(query, list(converted_row.values()))
            except Exception as e:
                print(f"Error inserting row into {table_name}: {e}")
                print(f"Row data: {converted_row}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Migrated data to {table_name}")

# Define column mappings (PostgreSQL -> MySQL)
COLUMN_MAPPINGS = {
    'users': {
        'id': 'id',
        'email': 'email',
        'password_hash': 'password_hash',
        'is_admin': 'is_admin',
        'is_active': 'is_active',
        'sidebar_width': 'sidebar_width',
        'theme_preference': 'theme_preference',
        'created_at': 'created_at',
        'last_login': 'last_login'
    },
    'sections': {
        'id': 'id',
        'name': 'name',
        'created_at': 'created_at'
    },
    'pages': {
        'id': 'id',
        'name': 'name',
        'page_type': 'page_type',
        'section_id': 'section_id',
        'table_name': 'table_name',
        'config': 'config',
        'created_at': 'created_at'
    }
    # Add other tables as needed
}

if __name__ == "__main__":
    # Migrate each table
    for table_name, mapping in COLUMN_MAPPINGS.items():
        csv_file = f"{table_name}.csv"
        if os.path.exists(csv_file):
            migrate_table_data(csv_file, table_name, mapping)
        else:
            print(f"CSV file {csv_file} not found, skipping {table_name}")


