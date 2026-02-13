"""
Helper functions for ETL operations
"""
import psycopg2
from datetime import datetime, timedelta
import requests
import json

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ecommerce_dw',
    'user': 'user',
    'password': 'password'
}

def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(**DB_CONFIG)

def populate_dim_date(start_date, end_date):
    """Populate dim_date table with date range"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        is_weekend = day_of_week >= 5
        
        cur.execute("""
            INSERT INTO dim_date (
                full_date, year, quarter, month, month_name, 
                week, day, day_of_week, day_name, is_weekend
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (full_date) DO NOTHING
        """, (
            current_date,
            current_date.year,
            (current_date.month - 1) // 3 + 1,
            current_date.month,
            current_date.strftime('%B'),
            current_date.isocalendar()[1],
            current_date.day,
            day_of_week,
            current_date.strftime('%A'),
            is_weekend
        ))
        
        current_date += timedelta(days=1)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Populated dim_date from {start_date} to {end_date}")

def populate_dim_product_from_api():
    """Populate dim_product from Fake Store API"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch products from API
    response = requests.get('https://fakestoreapi.com/products')
    products = response.json()
    
    for product in products:
        cur.execute("""
            INSERT INTO dim_product (product_id, product_title, category, price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (product_id) 
            DO UPDATE SET 
                product_title = EXCLUDED.product_title,
                category = EXCLUDED.category,
                price = EXCLUDED.price,
                updated_at = CURRENT_TIMESTAMP
        """, (
            product['id'],
            product['title'],
            product['category'],
            product['price']
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Populated {len(products)} products")

def populate_dim_user_from_api():
    """Populate dim_user from Fake Store API"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch users from API
    response = requests.get('https://fakestoreapi.com/users')
    users = response.json()
    
    for user in users:
        address = user.get('address', {})
        name = user.get('name', {})
        
        cur.execute("""
            INSERT INTO dim_user (
                user_id, username, email, first_name, last_name, 
                phone, address_city, address_street, address_zipcode
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET
                username = EXCLUDED.username,
                email = EXCLUDED.email,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user['id'],
            user.get('username'),
            user.get('email'),
            name.get('firstname'),
            name.get('lastname'),
            user.get('phone'),
            address.get('city'),
            address.get('street'),
            address.get('zipcode')
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Populated {len(users)} users")

def populate_dim_category():
    """Populate dim_category from existing products"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO dim_category (category_name)
        SELECT DISTINCT category
        FROM dim_product
        ON CONFLICT (category_name) DO NOTHING
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Populated dim_category")

if __name__ == "__main__":
    print("Starting ETL - Populating dimensions...")
    
    # Populate date dimension (3 years: 2024-2026)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 12, 31)
    populate_dim_date(start, end)
    
    # Populate product and user dimensions
    populate_dim_product_from_api()
    populate_dim_user_from_api()
    populate_dim_category()
    
    print("\nAll dimensions populated successfully!")
