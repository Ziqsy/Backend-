import mysql.connector
from werkzeug.security import generate_password_hash

MYSQL_CONFIG = {
    'host': 'your-hostinger-mysql-host',
    'user': 'your-mysql-username',
    'password': 'your-mysql-password',
    'database': 'ziqsy_internal',
    'charset': 'utf8mb4'
}

def create_admin_user():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # Check if admin user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@ziqsy.com',))
    if cursor.fetchone():
        print("Admin user already exists")
        return
    
    # Create admin user
    password_hash = generate_password_hash('ziqsy2025')
    query = """
    INSERT INTO users (email, password_hash, is_admin, is_active, sidebar_width, theme_preference)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = ('admin@ziqsy.com', password_hash, True, True, 280, 'dark')
    
    cursor.execute(query, values)
    conn.commit()
    
    print("Admin user created successfully")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_admin_user()


