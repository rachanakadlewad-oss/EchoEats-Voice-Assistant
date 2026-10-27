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
from django.contrib.auth.hashers import make_password

ALL_FOOD_ITEMS = [
    # Baseline 11 items (matching exact original database names)
    (1, "Margherita Pizza", "Classic delight with 100% real mozzarella cheese, basil leaves, and herb-infused tomato sauce on a hand-tossed crust.", 199.00, "Pizza", "01_Margherita.jpeg", 1, 4.8, 0, 50),
    (2, "Farmhouse Pizza", "Crispy hand-stretched crust overloaded with crunchy bell peppers, juicy golden corn, mushrooms, and diced onions.", 249.00, "Pizza", "02_Farmhouse.jpeg", 1, 4.7, 0, 45),
    (3, "Pepperoni Pizza", "Loaded with savory spiced pepperoni slices, smothered with premium melted cheese and rich oregano sprinkles.", 299.00, "Pizza", "03_Pepperoni.jpeg", 1, 4.9, 0, 35),
    (4, "Veggie Burger", "Crisp golden vegetable patty layered with fresh iceberg lettuce, sliced tomatoes, gherkins, and house special sauce.", 129.00, "Burger", "04_VeggieBurger.jpeg", 1, 4.6, 0, 60),
    (5, "Chicken Burger", "Tender, seasoned chicken patty flame-grilled to perfection, topped with crisp slaw, cheese, and creamy garlic dressing.", 169.00, "Burger", "05_ChickenBurger.jpeg", 1, 4.8, 0, 40),
    (6, "Cheese Burst Burger", "Double melted cheddar slices over a seasoned savory patty with caramelised onions, pickles, and smoky barbecue aioli.", 149.00, "Burger", "06_CheeseBurger.jpeg", 1, 4.7, 0, 50),
    (7, "Chicken Biryani", "Slow-cooked fragrant dum basmati rice layered with succulent marinated chicken, saffron, mint, and whole aromatic spices.", 249.00, "Main Course", "07_ChickenBiryani.jpeg", 1, 4.9, 0, 30),
    (8, "South Indian Thali", "A royal platter with 2 butter rotis, dal makhani, paneer butter masala, jeera rice, salad, raita, and hot gulab jamun.", 199.00, "Main Course", "08_Thali.jpeg", 1, 4.8, 0, 25),
    (9, "Masala Dosa", "Paper-thin golden South Indian fermented rice crepe filled with fragrant spiced potato masala, served with chutneys.", 99.00, "Snacks", "09_MasalaDosa.jpeg", 1, 4.9, 0, 70),
    (10, "Obbattu", "Traditional festive sweet flatbread with a melt-in-mouth filling of chana dal, jaggery, cardamom, and pure desi ghee.", 79.00, "Dessert", "10_Obbattu.jpeg", 1, 4.7, 0, 40),
    (11, "Vangibath", "Classic Karnataka spiced brinjal rice prepared with freshly roasted spice blend, curry leaves, and crunchy roasted peanuts.", 119.00, "Main Course", "11_VangiBath.jpeg", 1, 4.6, 0, 50),

    # 5 New Items for Snacks
    (12, "Paneer Tikka Bites", "Tender cottage cheese cubes marinated in spiced hung curd, bell peppers, and grilled to smoky perfection.", 149.00, "Snacks", "12_PaneerTikka.jpeg", 1, 4.8, 0, 50),
    (13, "Crispy Vegetable Samosas", "Golden flaky pastry crusts stuffed with aromatic cumin-tempered mashed potatoes, green peas, and served with mint chutney.", 69.00, "Snacks", "13_VegSamosa.jpeg", 1, 4.7, 0, 60),
    (14, "Loaded Nachos Supreme", "Crispy stone-ground corn tortilla chips smothered in warm queso cheese, jalapenos, fresh tomato salsa, and sour cream.", 179.00, "Snacks", "14_LoadedNachos.jpeg", 1, 4.6, 0, 45),
    (15, "Chicken Cheese Balls", "Crunchy golden breaded bites packed with minced herb chicken and an oozing melted mozzarella center.", 189.00, "Snacks", "15_ChickenCheeseBalls.jpeg", 1, 4.9, 0, 40),
    (16, "Hara Bhara Kebab", "Nutritious and flavorful pan-seared patties prepared with fresh spinach, green peas, cottage cheese, and roasted spices.", 139.00, "Snacks", "16_HaraBharaKebab.jpeg", 1, 4.7, 0, 50),

    # 5 New Items for Main Course
    (17, "Paneer Butter Masala", "Soft cottage cheese cubes simmered in a velvety, rich tomato cashew gravy finished with fresh cream and kasuri methi.", 229.00, "Main Course", "17_PaneerButterMasala.jpeg", 1, 4.8, 0, 40),
    (18, "Dal Makhani with Jeera Rice", "Slow-cooked black lentils simmered overnight with butter and cream, served alongside aromatic cumin-tempered basmati rice.", 189.00, "Main Course", "18_DalMakhaniRice.jpeg", 1, 4.7, 0, 45),
    (19, "Butter Chicken Feast", "Tender roasted boneless chicken tikka cooked in an authentic creamy makhani gravy with aromatic whole spices.", 279.00, "Main Course", "19_ButterChicken.jpeg", 1, 4.9, 0, 35),
    (20, "Hyderabadi Veg Dum Biryani", "Fragrant long-grain basmati rice layered with garden-fresh vegetables, saffron, brown onions, and exotic spices.", 199.00, "Main Course", "20_VegDumBiryani.jpeg", 1, 4.6, 0, 40),
    (21, "Kadhai Chicken with Naan", "Juicy chicken cooked in a robust wok with freshly ground coriander, dry red chillies, crunchy bell peppers, and fluffy butter naan.", 269.00, "Main Course", "21_KadhaiChicken.jpeg", 1, 4.8, 0, 30),

    # 5 New Items for Pizza
    (22, "Paneer Tikka Pizza", "Hand-tossed crust topped with spicy tandoori paneer chunks, crisp bell peppers, red onions, and melted mozzarella.", 269.00, "Pizza", "22_PaneerTikkaPizza.jpeg", 1, 4.8, 0, 40),
    (23, "BBQ Chicken Pizza", "Smoked grilled chicken glazed with tangy barbecue sauce, caramelized red onions, fresh cilantro, and gooey cheddar.", 289.00, "Pizza", "23_BBQChickenPizza.jpeg", 1, 4.9, 0, 35),
    (24, "Four Cheese Gourmet Pizza", "A luxurious blend of mozzarella, aged cheddar, parmesan, and creamy gorgonzola on a garlic-brushed thin crust.", 319.00, "Pizza", "24_FourCheesePizza.jpeg", 1, 4.7, 0, 30),
    (25, "Fiery Jalapeno & Corn Pizza", "Zesty tomato sauce loaded with spicy pickled jalapenos, juicy sweet corn kernels, red paprika, and stretchy cheese.", 239.00, "Pizza", "25_JalapenoCornPizza.jpeg", 1, 4.6, 0, 45),
    (26, "Mushroom Truffle Pizza", "Sautéed garlic cremini mushrooms, caramelized onions, fresh rosemary, and a subtle drizzle of white truffle oil.", 299.00, "Pizza", "26_MushroomTrufflePizza.jpeg", 1, 4.8, 0, 30),

    # 5 New Items for Burger
    (27, "Crispy Paneer Supreme Burger", "Thick block of spiced batter-fried cottage cheese topped with spicy chipotle mayo, crunchy lettuce, and sliced tomatoes.", 159.00, "Burger", "27_CrispyPaneerBurger.jpeg", 1, 4.7, 0, 50),
    (28, "Smoky BBQ Bacon Burger", "Flame-broiled gourmet patty with crispy bacon rashers, smoky BBQ glaze, melted cheddar, and crisp onion rings.", 219.00, "Burger", "28_BBQBaconBurger.jpeg", 1, 4.8, 0, 40),
    (29, "Double Decker Chicken Burger", "Two juicy grilled chicken patties stacked with double melted cheese, garlic aioli, pickles, and shredded iceberg lettuce.", 229.00, "Burger", "29_DoubleChickenBurger.jpeg", 1, 4.9, 0, 35),
    (30, "Spicy Peri Peri Veg Burger", "Zesty golden vegetable patty seasoned with fiery African peri-peri spices, topped with creamy mint mayo and slaw.", 139.00, "Burger", "30_PeriPeriVegBurger.jpeg", 1, 4.6, 0, 55),
    (31, "Mushroom Swiss Melt Burger", "Savory patty blanketed with sautéed herb mushrooms, melted Swiss cheese, caramelized onions, and Dijon mustard sauce.", 179.00, "Burger", "31_MushroomSwissBurger.jpeg", 1, 4.8, 0, 40),

    # 5 New Items for Dessert
    (32, "Gulab Jamun with Rabri", "Warm, soft milk-solid dumplings soaked in rose-cardamom syrup, served over a bed of rich chilled thickened rabri.", 99.00, "Dessert", "32_GulabJamunRabri.jpeg", 1, 4.9, 0, 50),
    (33, "Sizzling Chocolate Brownie", "Decadent warm fudgy chocolate brownie topped with a scoop of creamy vanilla bean ice cream and hot chocolate fudge.", 149.00, "Dessert", "33_SizzlingBrownie.jpeg", 1, 4.8, 0, 45),
    (34, "Royal Rasmalai Delight", "Delicate flattened paneer discs steeped in fragrant saffron-infused milk garnished with sliced pistachios and almonds.", 119.00, "Dessert", "34_Rasmalai.jpeg", 1, 4.9, 0, 40),
    (35, "Classic New York Cheesecake", "Velvety smooth cream cheese filling over a buttery graham cracker crust, finished with a fresh strawberry compote.", 169.00, "Dessert", "35_Cheesecake.jpeg", 1, 4.7, 0, 35),
    (36, "Crispy Golden Jalebi with Rabri", "Freshly fried spiral golden jalebis soaked in saffron sugar syrup, paired with authentic traditional creamy rabri.", 89.00, "Dessert", "36_JalebiRabri.jpeg", 1, 4.8, 0, 45),
]

def seed_all_food_items(cursor=None, is_postgres=None):
    close_at_end = False
    if cursor is None:
        cursor = connection.cursor()
        close_at_end = True
        is_postgres = (connection.vendor == 'postgresql')
    elif is_postgres is None:
        is_postgres = (connection.vendor == 'postgresql')

    added_count = 0
    tables_to_seed = ['"FoodItems"', 'fooditems'] if is_postgres else ['FoodItems']

    for table_name in tables_to_seed:
        try:
            cursor.execute(f'SELECT 1 FROM {table_name} LIMIT 1')
        except Exception:
            if is_postgres:
                connection.rollback()
            continue

        for item in ALL_FOOD_ITEMS:
            item_id, name, desc, price, cat, img, avail, rating, qty, stock = item
            exists = False
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE LOWER(FoodName) = LOWER(%s)", [name])
                exists = (cursor.fetchone()[0] > 0)
            except Exception:
                if is_postgres:
                    connection.rollback()
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE LOWER(foodname) = LOWER(%s)", [name])
                    exists = (cursor.fetchone()[0] > 0)
                except Exception:
                    if is_postgres:
                        connection.rollback()
                    exists = False

            if not exists:
                avail_bool = True if avail else False
                try:
                    cursor.execute(f"""
                        INSERT INTO {table_name} (foodname, description, price, category, imagename, isavailable, rating, quantity, stock)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, desc, price, cat, img, avail_bool, rating, qty, stock))
                    added_count += 1
                except Exception:
                    if is_postgres:
                        connection.rollback()
                    try:
                        cursor.execute(f"""
                            INSERT INTO {table_name} (FoodName, Description, Price, Category, ImageName, IsAvailable, Rating, Quantity, Stock)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (name, desc, price, cat, img, avail_bool, rating, qty, stock))
                        added_count += 1
                    except Exception as ins_err2:
                        if is_postgres:
                            connection.rollback()
                        print(f"[EchoEats] Note inserting {name} into {table_name}: {ins_err2}")

    if is_postgres:
        for t_name in ['"FoodItems"', 'fooditems']:
            for col_name in ['FoodID', 'foodid']:
                try:
                    cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{t_name}', '{col_name}'),
                            COALESCE((SELECT MAX({col_name}) FROM {t_name}), 0) + 1,
                            false
                        )
                    """)
                except Exception:
                    connection.rollback()

    if close_at_end:
        cursor.close()

    return added_count


def initialize_database():
    try:
        vendor = connection.vendor
        is_postgres = (vendor == 'postgresql')
        is_sqlite = (vendor == 'sqlite')

        pk_col = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        timestamp_default = "CURRENT_TIMESTAMP"

        with connection.cursor() as cursor:
            # 1. Create FoodItems table
            try:
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
            except Exception as e:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note creating FoodItems table: {e}")

            # Also create lowercase fooditems table if case-sensitivity requires
            try:
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
            except Exception as e:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note creating fooditems table: {e}")

            # 2. Create users table
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id {pk_col},
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        is_logged_in INTEGER DEFAULT 0,
                        address TEXT,
                        created_at TIMESTAMP DEFAULT {timestamp_default}
                    )
                """)
            except Exception as e:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note creating users table: {e}")

            # Check if address column exists on users table, add it if missing
            try:
                cursor.execute("SELECT * FROM users LIMIT 0")
                existing_user_cols = [c[0].lower() for c in cursor.description]
                if 'address' not in existing_user_cols:
                    cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
                    print("[EchoEats] Added missing address column to users table.")
            except Exception as col_err:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note verifying users address column: {col_err}")

            # For PostgreSQL: verify and align is_logged_in column type
            if is_postgres:
                try:
                    cursor.execute("""
                        SELECT data_type FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'is_logged_in'
                    """)
                    row = cursor.fetchone()
                    if row and 'bool' in row[0].lower():
                        cursor.execute("""
                            ALTER TABLE users 
                            ALTER COLUMN is_logged_in DROP DEFAULT,
                            ALTER COLUMN is_logged_in TYPE INTEGER USING (CASE WHEN is_logged_in THEN 1 ELSE 0 END),
                            ALTER COLUMN is_logged_in SET DEFAULT 0
                        """)
                        print("[EchoEats] Successfully aligned users.is_logged_in to INTEGER")
                except Exception as col_err:
                    connection.rollback()
                    print(f"[EchoEats] Note checking is_logged_in type: {col_err}")

            # 3. Create orders table with user_id
            try:
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
            except Exception as e:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note creating orders table: {e}")

            # Check if user_id column exists on orders table, add it if missing
            try:
                cursor.execute("SELECT * FROM orders LIMIT 0")
                existing_cols = [c[0].lower() for c in cursor.description]
                if 'user_id' not in existing_cols:
                    cursor.execute("ALTER TABLE orders ADD COLUMN user_id VARCHAR(100)")
                    print("[EchoEats] Added missing user_id column to orders table.")
            except Exception as col_err:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note verifying orders columns: {col_err}")

            # 4. Create session_carts table
            try:
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
            except Exception as e:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note creating session_carts table: {e}")

            # 5. Synchronize PostgreSQL sequences to avoid duplicate key errors
            if is_postgres:
                for table_name, pk_name in [('users', 'user_id'), ('orders', 'id'), ('session_carts', 'id')]:
                    try:
                        cursor.execute(f"""
                            SELECT setval(
                                pg_get_serial_sequence('{table_name}', '{pk_name}'),
                                COALESCE((SELECT MAX({pk_name}) FROM "{table_name}"), 0) + 1,
                                false
                            )
                        """)
                    except Exception:
                        try:
                            cursor.execute(f"""
                                SELECT setval(
                                    pg_get_serial_sequence('{table_name}', '{pk_name}'),
                                    COALESCE((SELECT MAX({pk_name}) FROM {table_name}), 0) + 1,
                                    false
                                )
                            """)
                        except Exception as seq_err:
                            connection.rollback()
                            print(f"[EchoEats] Note syncing {table_name} sequence: {seq_err}")

            # 6. Seed all FoodItems (idempotent duplicate-safe insertion)
            try:
                added = seed_all_food_items(cursor, is_postgres)
                if added > 0:
                    print(f"[EchoEats] Seeded {added} new food items.")
            except Exception as seed_err:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note seeding food items: {seed_err}")

            # 7. Seed demo user if not exists with hashed password
            try:
                cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(email) = %s", ["alex@echoeats.com"])
                if cursor.fetchone()[0] == 0:
                    hashed_demo_pw = make_password("password123")
                    cursor.execute("""
                        INSERT INTO users (name, email, password, is_logged_in)
                        VALUES (%s, %s, %s, %s)
                    """, ["Alex Turner", "alex@echoeats.com", hashed_demo_pw, 0])
                    print("[EchoEats] Seeded demo user alex@echoeats.com")
            except Exception as u_seed_err:
                if is_postgres:
                    connection.rollback()
                print(f"[EchoEats] Note seeding demo user: {u_seed_err}")

        print(f"[EchoEats] Database ({vendor}) initialized successfully!")
    except Exception as e:
        print(f"[EchoEats] Database initialization error: {e}")

if __name__ == '__main__':
    initialize_database()
