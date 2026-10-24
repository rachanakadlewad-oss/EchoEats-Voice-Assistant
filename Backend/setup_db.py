import os
import django
from pathlib import Path

# Setup Django environment if not already setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
try:
    django.setup()
except RuntimeError:
    pass  # Already setup

from django.db import connection

def initialize_database():
    try:
        vendor = connection.vendor
        is_postgres = (vendor == 'postgresql')
        is_sqlite = (vendor == 'sqlite')

        pk_col = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        timestamp_default = "CURRENT_TIMESTAMP"

        with connection.cursor() as cursor:
            # 1. Create FoodItems table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS "FoodItems" (
                    FoodID {pk_col},
                    FoodName VARCHAR(100) NOT NULL,
                    Description TEXT,
                    Price DECIMAL(10, 2) NOT NULL,
                    Category VARCHAR(50),
                    ImageName VARCHAR(255),
                    IsAvailable INTEGER DEFAULT 1,
                    Rating DECIMAL(2, 1) DEFAULT 4.5,
                    DateAdded TIMESTAMP DEFAULT {timestamp_default},
                    Quantity INTEGER DEFAULT 0,
                    Stock INTEGER DEFAULT 50
                )
            """)

            # Also create lowercase fooditems table/alias if case-sensitivity requires
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS fooditems (
                    foodid {pk_col},
                    foodname VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50),
                    imagename VARCHAR(255),
                    isavailable INTEGER DEFAULT 1,
                    rating DECIMAL(2, 1) DEFAULT 4.5,
                    dateadded TIMESTAMP DEFAULT {timestamp_default},
                    quantity INTEGER DEFAULT 0,
                    stock INTEGER DEFAULT 50
                )
            """)

            # 2. Create users table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id {pk_col},
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_logged_in INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT {timestamp_default}
                )
            """)

            # 3. Create orders table with user_id
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS orders (
                    id {pk_col},
                    user_id VARCHAR(100),
                    order_id VARCHAR(100) UNIQUE NOT NULL,
                    razorpay_order_id VARCHAR(100),
                    payment_id VARCHAR(100),
                    amount DECIMAL(10, 2) NOT NULL,
                    currency VARCHAR(10) DEFAULT 'INR',
                    payment_method VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'placed',
                    items TEXT,
                    customer_details TEXT,
                    signature VARCHAR(255),
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    updated_at TIMESTAMP DEFAULT {timestamp_default}
                )
            """)

            # Check if user_id column exists on orders table, add it if missing
            try:
                cursor.execute("SELECT * FROM orders LIMIT 0")
                existing_cols = [c[0].lower() for c in cursor.description]
                if 'user_id' not in existing_cols:
                    cursor.execute("ALTER TABLE orders ADD COLUMN user_id VARCHAR(100)")
                    print("[EchoEats] Added missing user_id column to orders table.")
            except Exception as col_err:
                print(f"[EchoEats] Note verifying orders columns: {col_err}")

            # 4. Create session_carts table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS session_carts (
                    id {pk_col},
                    session_id VARCHAR(255) NOT NULL,
                    food_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    updated_at TIMESTAMP DEFAULT {timestamp_default}
                )
            """)

            # 5. Seed FoodItems if empty
            try:
                cursor.execute('SELECT COUNT(*) FROM "FoodItems"')
                count = cursor.fetchone()[0]
            except Exception:
                cursor.execute('SELECT COUNT(*) FROM fooditems')
                count = cursor.fetchone()[0]

            items = [
                (1, "Margherita Pizza", "Classic delight with 100% real mozzarella cheese, basil leaves, and herb-infused tomato sauce on a hand-tossed crust.", 199.00, "Pizza", "01_Margherita.jpeg", 1, 4.8, 0, 50),
                (2, "Farmhouse Pizza", "Crispy hand-stretched crust overloaded with crunchy bell peppers, juicy golden corn, mushrooms, and diced onions.", 249.00, "Pizza", "02_Farmhouse.jpeg", 1, 4.7, 0, 45),
                (3, "Pepperoni Pizza", "Loaded with savory spiced pepperoni slices, smothered with premium melted cheese and rich oregano sprinkles.", 299.00, "Pizza", "03_Pepperoni.jpeg", 1, 4.9, 0, 35),
                (4, "Veggie Burger", "Crisp golden vegetable patty layered with fresh iceberg lettuce, sliced tomatoes, gherkins, and house special sauce.", 129.00, "Burger", "04_VeggieBurger.jpeg", 1, 4.6, 0, 60),
                (5, "Chicken Burger", "Tender, seasoned chicken patty flame-grilled to perfection, topped with crisp slaw, cheese, and creamy garlic dressing.", 169.00, "Burger", "05_ChickenBurger.jpeg", 1, 4.8, 0, 40),
                (6, "Cheese Burger", "Double melted cheddar slices over a seasoned savory patty with caramelised onions, pickles, and smoky barbecue aioli.", 149.00, "Burger", "06_CheeseBurger.jpeg", 1, 4.7, 0, 50),
                (7, "Chicken Biryani", "Slow-cooked fragrant dum basmati rice layered with succulent marinated chicken, saffron, mint, and whole aromatic spices.", 249.00, "Main Course", "07_ChickenBiryani.jpeg", 1, 4.9, 0, 30),
                (8, "Special Indian Thali", "A royal platter with 2 butter rotis, dal makhani, paneer butter masala, jeera rice, salad, raita, and hot gulab jamun.", 199.00, "Main Course", "08_Thali.jpeg", 1, 4.8, 0, 25),
                (9, "Crispy Masala Dosa", "Paper-thin golden South Indian fermented rice crepe filled with fragrant spiced potato masala, served with chutneys.", 99.00, "Snacks", "09_MasalaDosa.jpeg", 1, 4.9, 0, 70),
                (10, "Sweet Obbattu", "Traditional festive sweet flatbread with a melt-in-mouth filling of chana dal, jaggery, cardamom, and pure desi ghee.", 79.00, "Dessert", "10_Obbattu.jpeg", 1, 4.7, 0, 40),
                (11, "Authentic Vangi Bath", "Classic Karnataka spiced brinjal rice prepared with freshly roasted spice blend, curry leaves, and crunchy roasted peanuts.", 119.00, "Main Course", "11_VangiBath.jpeg", 1, 4.6, 0, 50),
            ]

            if count == 0:
                for item in items:
                    cursor.execute("""
                        INSERT INTO "FoodItems" (FoodID, FoodName, Description, Price, Category, ImageName, IsAvailable, Rating, Quantity, Stock)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, item)
                if is_postgres:
                    try:
                        cursor.execute("SELECT setval(pg_get_serial_sequence('\"FoodItems\"', 'foodid'), (SELECT MAX(FoodID) FROM \"FoodItems\"))")
                    except Exception:
                        pass

            # 6. Seed demo user if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ["alex@echoeats.com"])
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO users (name, email, password, is_logged_in)
                    VALUES (%s, %s, %s, %s)
                """, ["Alex Turner", "alex@echoeats.com", "password123", 0])

        print(f"[EchoEats] Database ({vendor}) initialized successfully!")
    except Exception as e:
        print(f"[EchoEats] Database initialization error: {e}")

if __name__ == '__main__':
    initialize_database()
