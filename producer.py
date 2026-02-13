import json
import time
import random
import requests
from kafka import KafkaProducer

# User pool that grows over time (simulates new registrations)
active_users = list(range(1, 11))  # Start with 10 users from API
next_user_id = 11
max_users = 200  # Cap at 200 users

def get_products():
    response = requests.get('https://fakestoreapi.com/products')
    return response.json()

def create_producer():
    # Wait for Kafka to start
    time.sleep(10)
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def register_new_user():
    """Simulate new user registration"""
    global next_user_id, active_users
    
    if next_user_id <= max_users:
        active_users.append(next_user_id)
        print(f"🆕 New user registered: user_id={next_user_id}")
        next_user_id += 1

def choose_user():
    """Choose user with weighted distribution (some users order more often)"""
    # 20% of users are heavy buyers (VIP candidates)
    # 30% are regular buyers
    # 50% are casual buyers  
    
    if len(active_users) < 20:
        return random.choice(active_users)
    
    # Create weighted pool
    heavy_buyers = active_users[:int(len(active_users) * 0.2)]
    regular_buyers = active_users[int(len(active_users) * 0.2):int(len(active_users) * 0.5)]
    casual_buyers = active_users[int(len(active_users) * 0.5):]
    
    # Weighted selection: 50% heavy, 30% regular, 20% casual
    pool = (heavy_buyers * 5) + (regular_buyers * 3) + (casual_buyers * 2)
    
    return random.choice(pool)

def main():
    print("🚀 Starting E-Commerce Event Producer...")
    products = get_products()
    producer = create_producer()
    topic = 'ecommerce_events'

    print(f"✓ Loaded {len(products)} products")
    print(f"✓ Started with {len(active_users)} users")
    print(f"📤 Streaming events to '{topic}'...\n")

    event_count = 0
    
    while True:
        try:
            # Periodically register new users (every 20-50 events)
            if event_count > 0 and event_count % random.randint(20, 50) == 0:
                register_new_user()
            
            # Simulate an order
            product = random.choice(products)
            user_id = choose_user()
            
            event = {
                'order_id': random.randint(10000, 99999),
                'user_id': user_id,
                'product_id': product['id'],
                'product_title': product['title'],
                'category': product['category'],
                'price': product['price'],
                'quantity': random.randint(1, 5),
                'timestamp': time.time()
   }
            
            event['revenue'] = round(event['price'] * event['quantity'], 2)
            
            producer.send(topic, event)
            
            event_count += 1
            
            # Print summary every 50 events
            if event_count % 50 == 0:
                print(f"📊 Sent {event_count} events | Active users: {len(active_users)}")
            else:
                print(f"📤 Sent event: order_id={event['order_id']}, user_id={user_id}, product={product['title'][:30]}, price={event['revenue']}")
            
            # Simulate random delay between orders (0.5-2 seconds)
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
