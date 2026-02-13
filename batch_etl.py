"""
Batch ETL Consumer: Kafka -> PostgreSQL fact_sales
Reads from ecommerce_events topic and loads into data warehouse
"""
import json
import time
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_values

import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'ecommerce_dw'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap_servers': [os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
    'group_id': 'batch_etl_consumer',
    'auto_offset_reset': 'latest',  # Read only new messages
    'enable_auto_commit': True,
    'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
}


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def ensure_user_exists(conn, user_id):
    """Create synthetic user if user_id doesn't exist in dim_user"""
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT 1 FROM dim_user WHERE user_id = %s", (user_id,))
    if cur.fetchone():
        cur.close()
        return  # User already exists
    
    # Create synthetic user
    username = f"user{user_id}"
    email = f"user{user_id}@example.com"
    
    cur.execute("""
        INSERT INTO dim_user (user_id, email, username, first_name, last_name, phone, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, email, username, f"User", f"{user_id}", "000-000-0000"))
    
    conn.commit()
    cur.close()
    print(f"🆕 Created new user: user_id={user_id}")



def get_date_id(conn, timestamp):
    """Get date_id from dim_date based on timestamp"""
    date = datetime.fromtimestamp(timestamp).date()
    with conn.cursor() as cur:
        cur.execute("SELECT date_id FROM dim_date WHERE full_date = %s", (date,))
        result = cur.fetchone()
        if not result:
            print(f"[WARNING] No date_id found for date: {date}")
        return result[0] if result else None


def insert_fact_sales(conn, events):
    """Batch insert events into fact_sales"""
    if not events:
        return 0
    
    # Ensure all users exist in dim_user (create synthetic if needed)
    for event in events:
        ensure_user_exists(conn, event['user_id'])
    
    # Prepare data for batch insert
    sales_data = []
    for event in events:
        date_id = get_date_id(conn, event['timestamp'])
        if date_id:  # Only insert if date exists in dimension
            sales_data.append((
                event['order_id'],
                event['user_id'],
                event['product_id'],
                date_id,
                event['quantity'],
                event['price'],
                event['price'] * event['quantity']  # revenue
            ))
    
    if not sales_data:
        return 0
    
    # Batch insert with ON CONFLICT to avoid duplicates
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO fact_sales (order_id, user_id, product_id, date_id, quantity, unit_price, revenue)
            VALUES %s
            ON CONFLICT (order_id, product_id) DO NOTHING
            """,
            sales_data
        )
    
    conn.commit()
    return len(sales_data)


def main():
    print("Starting Batch ETL Consumer...")
    print(f"Connecting to Kafka: {KAFKA_CONFIG['bootstrap_servers']}")
    print(f"Connecting to PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    # Create Kafka consumer
    consumer = KafkaConsumer('ecommerce_events', **KAFKA_CONFIG)
    
    # Database connection
    conn = get_db_connection()
    
    print("Connected! Waiting for events...")
    
    batch = []
    batch_size = 10  # Insert every 10 events
    total_inserted = 0
    
    # Metrics tracking
    start_time = time.time()
    events_processed = 0
    batches_inserted = 0
    errors = 0
    
    try:
        for message in consumer:
            event = message.value
            print(f"[DEBUG] Received event: order_id={event.get('order_id')}, timestamp={event.get('timestamp')}")
            batch.append(event)
            events_processed += 1
            
            # Insert batch when size is reached
            if len(batch) >= batch_size:
                print(f"[DEBUG] Processing batch of {len(batch)} events...")
                try:
                    inserted = insert_fact_sales(conn, batch)
                    total_inserted += inserted
                    batches_inserted += 1
                    
                    if inserted > 0:
                        print(f"✅ Inserted {inserted} sales records. Total: {total_inserted}")
                    else:
                        print(f"⚠️ No records inserted from batch (date lookup failed?)")
                        errors += 1
                    
                    # Log metrics every 10 batches
                    if batches_inserted % 10 == 0:
                        elapsed = time.time() - start_time
                        events_per_sec = events_processed / elapsed if elapsed > 0 else 0
                        print(f"📊 Metrics: {events_processed} events, "
                              f"{batches_inserted} batches, "
                              f"{events_per_sec:.2f} events/sec, "
                              f"{errors} errors, "
                              f"runtime: {elapsed/60:.1f}m")
                
                except Exception as e:
                    print(f"❌ Error inserting batch: {e}")
                    conn.rollback()  # Rollback failed transaction
                    errors += 1

                
                batch = []
        
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
        # Insert remaining events
        if batch:
            inserted = insert_fact_sales(conn, batch)
            total_inserted += inserted
            print(f"Inserted final {inserted} sales records. Total: {total_inserted}")
    
    finally:
        consumer.close()
        conn.close()
        
        # Final metrics
        elapsed = time.time() - start_time
        events_per_sec = events_processed / elapsed if elapsed > 0 else 0
        print(f"\n📈 Final Metrics:")
        print(f"   Total events processed: {events_processed}")
        print(f"   Total records inserted: {total_inserted}")
        print(f"   Batches processed: {batches_inserted}")
        print(f"   Errors: {errors}")
        print(f"   Average rate: {events_per_sec:.2f} events/sec")
        print(f"   Total runtime: {elapsed/60:.1f} minutes")
        print(f"Consumer stopped.")


if __name__ == "__main__":
    main()
