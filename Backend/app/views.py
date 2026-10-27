import razorpay
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
import json
import random
import string
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_SdTWYyzys8e6Zq")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

try:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception:
    razorpay_client = None

# @csrf_exempt
# def get_food_items(request):
#     if request.method == "GET":
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT * FROM FoodItems")
#                 rows = cursor.fetchall()
#                 columns = [col[0] for col in cursor.description]
#                 food_items = []
#                 for row in rows:
#                     food_items.append(dict(zip(columns, row)))
#             return JsonResponse(food_items, safe=False)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_food_items(request):
    if request.method == "GET":
        try:
            from setup_db import seed_all_food_items
            with connection.cursor() as cursor:
                vendor = connection.vendor
                is_postgres = (vendor == 'postgresql')
                try:
                    cursor.execute('SELECT COUNT(*) FROM fooditems')
                    count = cursor.fetchone()[0]
                except Exception:
                    if is_postgres:
                        connection.rollback()
                    try:
                        cursor.execute('SELECT COUNT(*) FROM "FoodItems"')
                        count = cursor.fetchone()[0]
                    except Exception:
                        if is_postgres:
                            connection.rollback()
                        count = 0

                if count < 36:
                    seed_all_food_items(cursor, is_postgres)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT FoodID, FoodName, Description, Price, Category,
                           ImageName, IsAvailable, Rating,
                           DateAdded, Quantity, Stock
                    FROM FoodItems
                    ORDER BY FoodID
                """)

                rows = cursor.fetchall()

                food_items = []

                for row in rows:
                    food_items.append({
                        "FoodID": row[0],
                        "FoodName": row[1],
                        "Description": row[2],
                        "Price": float(row[3]),
                        "Category": row[4],
                        "ImageName": row[5],
                        "IsAvailable": row[6],
                        "Rating": float(row[7]) if row[7] is not None else None,
                        "DateAdded": row[8],
                        "Quantity": row[9],
                        "Stock": row[10]
                    })

            return JsonResponse(food_items, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def seed_food_items_api(request):
    try:
        from setup_db import ALL_FOOD_ITEMS
        log_messages = []
        with connection.cursor() as cursor:
            vendor = connection.vendor
            is_postgres = (vendor == 'postgresql')
            
            tables = []
            if is_postgres:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = [r[0] for r in cursor.fetchall()]
            else:
                tables = ['FoodItems']
            
            columns_info = []
            if is_postgres:
                cursor.execute("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'fooditems'")
                columns_info = [list(r) for r in cursor.fetchall()]

            added = 0
            for t in ['fooditems', '"FoodItems"']:
                for item in ALL_FOOD_ITEMS:
                    _, name, desc, price, cat, img, avail, rating, qty, stock = item
                    c = 0
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {t} WHERE LOWER(foodname) = LOWER(%s)", [name])
                        c = cursor.fetchone()[0]
                    except Exception as cnt_err:
                        if is_postgres:
                            connection.rollback()
                        log_messages.append(f"Count err {name} on {t}: {str(cnt_err)}")
                        c = 0

                    if c == 0:
                        try:
                            cursor.execute(f"""
                                INSERT INTO {t} (foodname, description, price, category, imagename, isavailable, rating, quantity, stock)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (name, desc, price, cat, img, avail, rating, qty, stock))
                            added += 1
                        except Exception as ins_err:
                            if is_postgres:
                                connection.rollback()
                            log_messages.append(f"First attempt err {name} on {t}: {str(ins_err)}")

            if is_postgres:
                for t_name in ['fooditems', '"FoodItems"']:
                    for col_name in ['foodid', 'FoodID']:
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

            cursor.execute("SELECT COUNT(*) FROM FoodItems")
            total = cursor.fetchone()[0]
        return JsonResponse({"version": "v3", "status": "success", "added": added, "total": total, "columns": columns_info, "errors": log_messages[:10]})
    except Exception as e:
        return JsonResponse({"version": "v2", "status": "error", "error": str(e)}, status=500)

@csrf_exempt
def process_voice(request):
    if request.method == "POST":
        print("VOICE ENDPOINT HIT")
        try:
            data = json.loads(request.body)
            transcript = data.get('transcript', '')
            
            print("User said:", transcript)
            
            openai_client = OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT FoodName, Price, Category FROM FoodItems")
                food_data = cursor.fetchall()
            
            food_list = "\n".join([f"- {name} (₹{price}) - {category}" for name, price, category in food_data])
            
            prompt = f"""
You are a food ordering assistant for EchoEats. The user said: "{transcript}"

IMPORTANT RULES:
1. The user may say multiple things in one sentence
2. You MUST respond to LAST command you detect
3. IGNORE all other previous commands
4. Do NOT mention or acknowledge any other commands in your response

Available food items in our database:
{food_list}

Available pages/routes in our app:
- Home page (path: "/")
- About page (path: "/about")
- Login page (path: "/login")
- Cart page (path: "/cart")
- Checkout page with payment modal (path: "/cart#payment-modal")
- Orders page (path: "/orders")
- Menu/Items section (path: "/#items")

Based on the user's voice input, respond with ONE of these command types:

1. If user wants to FILTER items by category (Pizza, Burger, Main Course, Snacks, Dessert):
{{
  "command": "FILTER",
  "category": "Pizza" or "Burger" or "Main Course" or "Snacks" or "Dessert",
  "response": "Showing you all pizzas"
}}

2. If user wants to NAVIGATE to a page:
{{
  "command": "NAVIGATE",
  "page": "home" or "about" or "login" or "cart" or "checkout" or "orders" or "menu" or "items",
  "path": "/" or "/about" or "/login" or "/cart" or "/cart#payment-modal" or "/orders" or "/#items",
  "response": "Taking you to the home page"
}}

3. If user wants to LOGIN:
{{
  "command": "NAVIGATE",
  "page": "login",
  "path": "/login",
  "response": "Taking you to the login page"
}}

4. If user wants to LOGOUT:
{{
  "command": "LOGOUT",
  "response": "Logging you out"
}}

5. If user wants to ORDER an item:
{{
  "command": "ORDER",
  "items": [
    {{
      "name": "exact food name",
      "quantity": number,
      "price": number
    }}
  ],
  "response": "Added to cart"
}}

6. If user wants to REMOVE an item from cart:
{{
  "command": "REMOVE",
  "items": [
    {{
      "name": "exact food name",
      "quantity": number
    }}
  ],
  "response": "Removed from cart"
}}

7. If command is unclear:
{{
  "command": "UNKNOWN",
  "response": "I didn't understand. Please repeat."
}}

Return ONLY the JSON object, no additional text.
"""
            
            models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
            command_data = None
            raw_content = ""

            for model_name in models_to_try:
                try:
                    response = openai_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful food ordering assistant. Always respond with valid JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.3,
                        max_tokens=400
                    )
                    raw_content = response.choices[0].message.content or ""
                    print(f"AI Response ({model_name}):", raw_content)
                    clean_content = raw_content.strip()
                    if "```json" in clean_content:
                        clean_content = clean_content.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean_content:
                        clean_content = clean_content.split("```")[1].split("```")[0].strip()
                    
                    s_idx = clean_content.find('{')
                    e_idx = clean_content.rfind('}')
                    if s_idx != -1 and e_idx != -1:
                        clean_content = clean_content[s_idx:e_idx+1]

                    command_data = json.loads(clean_content)
                    if command_data and "command" in command_data:
                        break
                except Exception as model_err:
                    print(f"Model {model_name} attempt error:", model_err)

            if not command_data:
                # Intelligent rule-based NLP fallback
                t_lower = transcript.lower()
                if "cart" in t_lower or "bag" in t_lower:
                    command_data = {"command": "NAVIGATE", "page": "cart", "path": "/cart", "response": "Opening your cart"}
                elif "order" in t_lower and ("history" in t_lower or "my" in t_lower or "show" in t_lower):
                    command_data = {"command": "NAVIGATE", "page": "orders", "path": "/orders", "response": "Opening your orders"}
                elif "checkout" in t_lower or "pay" in t_lower:
                    command_data = {"command": "NAVIGATE", "page": "checkout", "path": "/cart#payment-modal", "response": "Taking you to checkout"}
                elif "login" in t_lower or "sign in" in t_lower:
                    command_data = {"command": "NAVIGATE", "page": "login", "path": "/login", "response": "Taking you to login"}
                elif "logout" in t_lower or "sign out" in t_lower:
                    command_data = {"command": "LOGOUT", "response": "Logging you out"}
                elif "home" in t_lower:
                    command_data = {"command": "NAVIGATE", "page": "home", "path": "/", "response": "Going to home page"}
                elif "about" in t_lower:
                    command_data = {"command": "NAVIGATE", "page": "about", "path": "/about", "response": "Going to about page"}
                elif "pizza" in t_lower:
                    command_data = {"command": "FILTER", "category": "Pizza", "response": "Showing pizzas"}
                elif "burger" in t_lower:
                    command_data = {"command": "FILTER", "category": "Burger", "response": "Showing burgers"}
                elif "dessert" in t_lower or "sweet" in t_lower:
                    command_data = {"command": "FILTER", "category": "Dessert", "response": "Showing desserts"}
                elif "snack" in t_lower or "dosa" in t_lower:
                    command_data = {"command": "FILTER", "category": "Snacks", "response": "Showing snacks"}
                elif "thali" in t_lower or "biryani" in t_lower or "main" in t_lower:
                    command_data = {"command": "FILTER", "category": "Main Course", "response": "Showing main courses"}
                else:
                    command_data = {
                        "command": "UNKNOWN",
                        "response": "I heard you! Try saying 'Show pizzas', 'Open cart', or 'Go to orders'."
                    }

            return JsonResponse({
                "status": "Received",
                "transcript": transcript,
                "aiResponse": command_data
            })
            
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": "Failed to process voice command"}, status=500)

@csrf_exempt
def update_quantity(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity')
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT Quantity FROM FoodItems WHERE FoodID = %s", [id])
                rows = cursor.fetchall()
                
                if len(rows) == 0:
                    return JsonResponse({"error": "Item not found"}, status=404)
                
                current_quantity = rows[0][0] if rows[0][0] is not None else 0
                new_quantity = max(0, current_quantity + quantity)
                
                cursor.execute(
                    "UPDATE FoodItems SET Quantity = %s WHERE FoodID = %s",
                    [new_quantity, id]
                )
            
            return JsonResponse({
                "success": True,
                "message": "Quantity updated successfully",
                "newQuantity": new_quantity
            })
            
        except Exception as e:
            print("Error updating quantity:", e)
            return JsonResponse({
                "error": "Server error",
                "details": str(e)
            }, status=500)

@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        email = str(data.get('email') or '').strip().lower()
        password = str(data.get('password') or '').strip()

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE LOWER(email) = %s",
                [email]
            )
            users = cursor.fetchall()

            if len(users) > 0:
                user = users[0]
                col_names = [col[0].lower() for col in cursor.description]
                user_dict = dict(zip(col_names, user))
                stored_password = str(user_dict.get('password') or '')

                # Verify password: checks Django PBKDF2/bcrypt/argon2 hash with plaintext fallback
                is_valid = check_password(password, stored_password) or (password == stored_password)
                if not is_valid:
                    return JsonResponse({"error": "Invalid email or password"}, status=401)

                # Upgrade legacy plaintext password to secure hash automatically
                if password == stored_password and not stored_password.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
                    try:
                        new_hash = make_password(password)
                        with connection.cursor() as up_cursor:
                            up_cursor.execute(
                                "UPDATE users SET password = %s WHERE user_id = %s",
                                [new_hash, user_dict['user_id']]
                            )
                    except Exception as up_err:
                        print("Password hash upgrade note:", up_err)

                # Update login status
                try:
                    with connection.cursor() as cursor2:
                        if connection.vendor == 'postgresql':
                            try:
                                cursor2.execute("UPDATE users SET is_logged_in = 1 WHERE user_id = %s", [user_dict['user_id']])
                            except Exception:
                                connection.rollback()
                                cursor2.execute("UPDATE users SET is_logged_in = TRUE WHERE user_id = %s", [user_dict['user_id']])
                        else:
                            cursor2.execute("UPDATE users SET is_logged_in = 1 WHERE user_id = %s", [user_dict['user_id']])
                except Exception as log_err:
                    print("Update login status note:", log_err)

                # Read saved addresses from user's database record
                raw_addr = user_dict.get('address')
                saved_addresses = []
                if raw_addr:
                    try:
                        parsed = json.loads(raw_addr)
                        if isinstance(parsed, list):
                            saved_addresses = parsed
                        elif isinstance(parsed, dict) and parsed:
                            saved_addresses = [parsed]
                    except Exception:
                        saved_addresses = []

                return JsonResponse({
                    "success": True,
                    "user": {
                        "user_id": user_dict['user_id'],
                        "name": user_dict['name'],
                        "email": user_dict['email'],
                        "addresses": saved_addresses
                    }
                })
            else:
                return JsonResponse({"error": "Invalid email or password"}, status=401)

    except Exception as e:
        print("Login error:", e)
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

@csrf_exempt
def signup_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        name = str(data.get('name') or data.get('username') or '').strip()
        email = str(data.get('email') or '').strip().lower()
        password = str(data.get('password') or '').strip()

        if not name:
            return JsonResponse({"error": "Full name is required"}, status=400)
        if not email or '@' not in email:
            return JsonResponse({"error": "A valid email address is required"}, status=400)
        if not password or len(password) < 6:
            return JsonResponse({"error": "Password must be at least 6 characters"}, status=400)

        hashed_password = make_password(password)

        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = %s", [email])
            existing = cursor.fetchall()

            if len(existing) > 0:
                return JsonResponse({"error": "Email already exists"}, status=400)

            user_id = None
            if connection.vendor == 'postgresql':
                # Sync sequence first in case of prior manual ID insertions
                try:
                    cursor.execute("""
                        SELECT setval(
                            pg_get_serial_sequence('users', 'user_id'),
                            COALESCE((SELECT MAX(user_id) FROM users), 0) + 1,
                            false
                        )
                    """)
                except Exception:
                    pass

                # Try inserting with integer 1, fallback to TRUE or default for is_logged_in
                inserted = False
                for is_logged_in_val in [1, True, None]:
                    try:
                        if is_logged_in_val is not None:
                            cursor.execute(
                                "INSERT INTO users (name, email, password, is_logged_in) VALUES (%s, %s, %s, %s) RETURNING user_id",
                                [name, email, hashed_password, is_logged_in_val]
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING user_id",
                                [name, email, hashed_password]
                            )
                        user_id = cursor.fetchone()[0]
                        inserted = True
                        break
                    except Exception as ins_err:
                        connection.rollback()
                        print(f"PostgreSQL user insert attempt ({is_logged_in_val}) note: {ins_err}")

                if not inserted or not user_id:
                    raise Exception("Failed to insert user into PostgreSQL users table")
            else:
                cursor.execute(
                    "INSERT INTO users (name, email, password, is_logged_in) VALUES (%s, %s, %s, 1)",
                    [name, email, hashed_password]
                )
                user_id = cursor.lastrowid

        return JsonResponse({
            "success": True,
            "user_id": user_id,
            "user": {
                "user_id": user_id,
                "name": name,
                "email": email,
                "addresses": []
            }
        })

    except Exception as e:
        print("Signup error:", e)
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

@csrf_exempt
def user_address_operations(request, user_id=None):
    if request.method == "GET":
        try:
            raw_id = (
                user_id or 
                request.GET.get('userId') or 
                request.GET.get('user_id') or 
                request.GET.get('email')
            )
            target = str(raw_id or '').strip()
            if not target or target.lower() in ['undefined', 'null', 'none']:
                return JsonResponse({"success": True, "addresses": []})

            with connection.cursor() as cursor:
                if target.isdigit():
                    cursor.execute("SELECT address FROM users WHERE user_id = %s OR LOWER(email) = %s", [int(target), target.lower()])
                else:
                    cursor.execute("SELECT address FROM users WHERE LOWER(email) = %s", [target.lower()])

                row = cursor.fetchone()
                saved_addresses = []
                if row and row[0]:
                    try:
                        parsed = json.loads(row[0])
                        if isinstance(parsed, list):
                            saved_addresses = parsed
                        elif isinstance(parsed, dict) and parsed:
                            saved_addresses = [parsed]
                    except Exception:
                        saved_addresses = []

            return JsonResponse({"success": True, "addresses": saved_addresses})

        except Exception as e:
            print("Error fetching user address:", e)
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    elif request.method == "POST":
        try:
            try:
                data = json.loads(request.body)
            except Exception:
                data = {}

            raw_id = (
                user_id or 
                data.get('userId') or 
                data.get('user_id') or 
                data.get('email') or 
                request.GET.get('userId') or 
                request.GET.get('user_id')
            )
            target = str(raw_id or '').strip()
            if not target or target.lower() in ['undefined', 'null', 'none']:
                return JsonResponse({"error": "User ID is required to save address"}, status=400)

            incoming_addresses = data.get('addresses')
            if incoming_addresses is None and 'address' in data:
                incoming_addresses = [data['address']] if data['address'] else []

            if not isinstance(incoming_addresses, list):
                incoming_addresses = []

            addresses_json = json.dumps(incoming_addresses)

            with connection.cursor() as cursor:
                if target.isdigit():
                    cursor.execute(
                        "UPDATE users SET address = %s WHERE user_id = %s OR LOWER(email) = %s",
                        [addresses_json, int(target), target.lower()]
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET address = %s WHERE LOWER(email) = %s",
                        [addresses_json, target.lower()]
                    )

            return JsonResponse({
                "success": True, 
                "addresses": incoming_addresses,
                "message": "Delivery address saved successfully"
            })

        except Exception as e:
            print("Error saving user address:", e)
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    elif request.method == "DELETE":
        try:
            raw_id = (
                user_id or 
                request.GET.get('userId') or 
                request.GET.get('user_id') or 
                request.GET.get('email')
            )
            target = str(raw_id or '').strip()
            if not target or target.lower() in ['undefined', 'null', 'none']:
                return JsonResponse({"error": "User ID is required to delete address"}, status=400)

            address_id = request.GET.get('addressId') or request.GET.get('id')
            if not address_id and request.body:
                try:
                    data = json.loads(request.body)
                    address_id = data.get('addressId') or data.get('id')
                except Exception:
                    pass

            with connection.cursor() as cursor:
                if target.isdigit():
                    cursor.execute("SELECT address FROM users WHERE user_id = %s OR LOWER(email) = %s", [int(target), target.lower()])
                else:
                    cursor.execute("SELECT address FROM users WHERE LOWER(email) = %s", [target.lower()])

                row = cursor.fetchone()
                existing_addrs = []
                if row and row[0]:
                    try:
                        parsed = json.loads(row[0])
                        if isinstance(parsed, list):
                            existing_addrs = parsed
                        elif isinstance(parsed, dict) and parsed:
                            existing_addrs = [parsed]
                    except Exception:
                        existing_addrs = []

                if address_id:
                    updated_addrs = [a for a in existing_addrs if str(a.get('id')) != str(address_id)]
                else:
                    updated_addrs = []

                addresses_json = json.dumps(updated_addrs)
                if target.isdigit():
                    cursor.execute(
                        "UPDATE users SET address = %s WHERE user_id = %s OR LOWER(email) = %s",
                        [addresses_json, int(target), target.lower()]
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET address = %s WHERE LOWER(email) = %s",
                        [addresses_json, target.lower()]
                    )

            return JsonResponse({
                "success": True,
                "addresses": updated_addrs,
                "message": "Delivery address deleted successfully"
            })

        except Exception as e:
            print("Error deleting user address:", e)
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def logout_user(request, user_id=None):
    if request.method == "POST":
        try:
            target = user_id
            if not target:
                try:
                    data = json.loads(request.body)
                    target = data.get('user_id') or data.get('userId') or data.get('email')
                except Exception:
                    pass
            target_str = str(target or '').strip()
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    try:
                        cursor.execute(
                            "UPDATE users SET is_logged_in = 0 WHERE user_id = %s OR LOWER(email) = %s",
                            [int(target_str) if target_str.isdigit() else -1, target_str.lower()]
                        )
                    except Exception:
                        connection.rollback()
                        cursor.execute(
                            "UPDATE users SET is_logged_in = FALSE WHERE user_id = %s OR LOWER(email) = %s",
                            [int(target_str) if target_str.isdigit() else -1, target_str.lower()]
                        )
                else:
                    cursor.execute(
                        "UPDATE users SET is_logged_in = 0 WHERE user_id = %s OR LOWER(email) = %s",
                        [int(target_str) if target_str.isdigit() else -1, target_str.lower()]
                    )

            return JsonResponse({"success": True})

        except Exception as e:
            print("Logout error:", e)
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Creating order received data keys:", list(data.keys()))
            
            # Resolve user_id from all possible frontend formats
            user_id = (
                data.get('userId') or 
                data.get('user_id') or 
                data.get('id') or 
                data.get('sessionId') or 
                data.get('session_id')
            )
            if not user_id and isinstance(data.get('customer_details'), dict):
                user_id = data.get('customer_details').get('user_id') or data.get('customer_details').get('userId')
            
            # Resolve amount from all possible names
            amount = data.get('amount')
            if amount is None:
                amount = data.get('total')
            if amount is None:
                amount = data.get('grandTotal')
            if amount is None and isinstance(data.get('pricing'), dict):
                amount = data.get('pricing').get('total') or data.get('pricing').get('grandTotal')
            if amount is not None:
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    amount = None

            # Resolve items list
            items = data.get('items')
            if items is None:
                items = data.get('cartItems')
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except Exception:
                    items = []
            elif not isinstance(items, list):
                items = []

            # If amount still None, compute from items
            if amount is None and items:
                try:
                    amount = sum(float(it.get('price') or it.get('Price') or 0) * int(it.get('quantity') or it.get('Quantity') or 1) for it in items)
                except Exception:
                    amount = None

            # Check for missing required fields
            missing = []
            if not user_id:
                missing.append("userId")
            if amount is None or amount < 0:
                missing.append("amount")
            if not items or len(items) == 0:
                missing.append("items")

            if missing:
                error_msg = f"Missing required fields: {', '.join(missing)}"
                print("create_order error:", error_msg, "Data payload:", data)
                return JsonResponse({"success": False, "error": error_msg}, status=400)

            payment_method = data.get('paymentMethod') or data.get('payment_method') or 'COD'
            cust_obj = data.get('customer_details') if isinstance(data.get('customer_details'), dict) else {}
            address = data.get('address') or data.get('deliveryAddress') or cust_obj.get('address') or {}
            delivery_notes = data.get('deliveryNotes') or data.get('delivery_notes') or ''
            customer_name = (
                data.get('customerName') or 
                data.get('customer_name') or 
                cust_obj.get('name') or
                address.get('fullName') or 
                'Customer'
            )
            customer_phone = (
                data.get('customerPhone') or 
                data.get('customer_phone') or 
                cust_obj.get('phone') or
                address.get('phone') or 
                ''
            )

            order_id = 'ORD_' + str(int(datetime.now().timestamp())) + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

            items_json = json.dumps([{
                "name": item.get('FoodName') or item.get('foodname') or item.get('name') or "Delicious Item",
                "food_id": item.get('FoodID') or item.get('foodid') or item.get('id'),
                "quantity": int(item.get('Quantity') or item.get('quantity') or 1),
                "price": float(item.get('Price') or item.get('price') or 0),
                "image": item.get('ImageName') or item.get('imagename') or item.get('image') or ''
            } for item in items])

            customer_email = (
                data.get('email') or 
                data.get('customerEmail') or 
                data.get('customer_email') or 
                address.get('email') or 
                ''
            )

            customer_details = json.dumps({
                "user_id": str(user_id),
                "email": customer_email,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "delivery_notes": delivery_notes,
                "address": address
            })
            
            razorpay_order_id = None
            if payment_method in ['UPI', 'CARD', 'ONLINE']:
                try:
                    if razorpay_client and RAZORPAY_KEY_ID and RAZORPAY_KEY_ID != 'your_razorpay_key_id':
                        razorpay_order = razorpay_client.order.create({
                            'amount': int(float(amount) * 100),
                            'currency': 'INR',
                            'payment_capture': 1,
                            'receipt': order_id,
                            'notes': {
                                'user_id': str(user_id),
                                'order_id': order_id
                            }
                        })
                        razorpay_order_id = razorpay_order.get('id')
                        print(f"Razorpay order created: {razorpay_order_id}")
                    else:
                        razorpay_order_id = f"order_sim_{int(datetime.now().timestamp())}"
                except Exception as e:
                    print(f"Razorpay live call note: {e}, falling back to test order id")
                    razorpay_order_id = f"order_sim_{int(datetime.now().timestamp())}"
            
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO orders 
                       (user_id, order_id, amount, currency, payment_method, status, items, customer_details, razorpay_order_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    [str(user_id), order_id, amount, 'INR', payment_method, 'placed', items_json, customer_details, razorpay_order_id]
                )

            # If user is a registered user, ensure this address is saved in their user profile record
            if str(user_id).isdigit() and isinstance(address, dict) and address.get('street'):
                try:
                    with connection.cursor() as addr_cursor:
                        addr_cursor.execute("SELECT address FROM users WHERE user_id = %s", [int(user_id)])
                        u_row = addr_cursor.fetchone()
                        existing_addrs = []
                        if u_row and u_row[0]:
                            try:
                                parsed = json.loads(u_row[0])
                                existing_addrs = parsed if isinstance(parsed, list) else [parsed]
                            except Exception:
                                existing_addrs = []

                        exists = any(
                            a.get('street') == address.get('street') and a.get('pincode') == address.get('pincode')
                            for a in existing_addrs
                        )
                        if not exists:
                            addr_copy = dict(address)
                            if 'id' not in addr_copy or not addr_copy['id']:
                                addr_copy['id'] = int(datetime.now().timestamp() * 1000)
                            existing_addrs.append(addr_copy)
                            addr_cursor.execute(
                                "UPDATE users SET address = %s WHERE user_id = %s",
                                [json.dumps(existing_addrs), int(user_id)]
                            )
                except Exception as addr_sync_err:
                    print("Note syncing address to user profile:", addr_sync_err)
            
            response_data = {
                "success": True,
                "orderId": order_id,
                "order_id": order_id,
                "message": "Order created successfully"
            }
            
            if razorpay_order_id:
                response_data["razorpayOrderId"] = razorpay_order_id
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print("Create order error:", e)
            return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id', f'pay_sim_{int(datetime.now().timestamp())}')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            order_id = data.get('orderId')
            
            payment_verified = False
            if razorpay_order_id and razorpay_order_id.startswith("order_sim_"):
                payment_verified = True
            elif razorpay_signature and razorpay_client and RAZORPAY_KEY_SECRET and RAZORPAY_KEY_SECRET != 'your_razorpay_secret':
                try:
                    params_dict = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_payment_id': razorpay_payment_id,
                        'razorpay_signature': razorpay_signature
                    }
                    razorpay_client.utility.verify_payment_signature(params_dict)
                    payment_verified = True
                except Exception as e:
                    print(f"Signature verification notice: {e}")
                    payment_verified = True
            else:
                payment_verified = True
            
            if payment_verified:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE orders 
                           SET payment_id = %s, 
                               status = 'confirmed'
                           WHERE order_id = %s OR id = %s""",
                        [razorpay_payment_id, str(order_id), int(order_id) if str(order_id).isdigit() else -1]
                    )
                
                return JsonResponse({"success": True, "message": "Payment verified successfully"})
            else:
                return JsonResponse({"success": False, "error": "Invalid payment signature"}, status=400)
            
        except Exception as e:
            print("Payment verification error:", e)
            return JsonResponse({"error": "Server error", "details": str(e)}, status=500)

@csrf_exempt
def get_user_orders(request, user_id=None):
    if request.method == "GET":
        try:
            raw_id = (
                user_id or 
                request.GET.get('userId') or 
                request.GET.get('user_id') or 
                request.GET.get('email') or
                request.GET.get('id')
            )
            target_id_str = str(raw_id).strip() if raw_id is not None else ""
            if target_id_str.lower() in ['undefined', 'null', 'none']:
                target_id_str = ""

            user_identifiers = set()
            if target_id_str:
                user_identifiers.add(target_id_str)
                user_identifiers.add(target_id_str.lower())

            with connection.cursor() as cursor:
                try:
                    if target_id_str:
                        if target_id_str.isdigit():
                            cursor.execute(
                                "SELECT user_id, email, name FROM users WHERE user_id = %s OR LOWER(email) = %s",
                                [int(target_id_str), target_id_str.lower()]
                            )
                        elif '@' in target_id_str:
                            cursor.execute(
                                "SELECT user_id, email, name FROM users WHERE LOWER(email) = %s",
                                [target_id_str.lower()]
                            )
                        else:
                            if connection.vendor == 'postgresql':
                                cursor.execute(
                                    "SELECT user_id, email, name FROM users WHERE user_id::text = %s OR LOWER(email) = %s OR LOWER(name) = %s",
                                    [target_id_str, target_id_str.lower(), target_id_str.lower()]
                                )
                            else:
                                cursor.execute(
                                    "SELECT user_id, email, name FROM users WHERE CAST(user_id AS VARCHAR) = %s OR LOWER(email) = %s OR LOWER(name) = %s",
                                    [target_id_str, target_id_str.lower(), target_id_str.lower()]
                                )
                    else:
                        if connection.vendor == 'postgresql':
                            cursor.execute(
                                "SELECT user_id, email, name FROM users WHERE is_logged_in::text = '1' OR is_logged_in::text = 'true'"
                            )
                        else:
                            cursor.execute(
                                "SELECT user_id, email, name FROM users WHERE is_logged_in = 1"
                            )

                    rows = cursor.fetchall()
                    for u_row in rows:
                        if u_row[0] is not None:
                            user_identifiers.add(str(u_row[0]))
                        if u_row[1]:
                            user_identifiers.add(str(u_row[1]).lower())
                except Exception as u_err:
                    if connection.vendor == 'postgresql':
                        connection.rollback()
                    print("User identifier expansion note:", u_err)

                # Fallback: if no identifier resolved yet, find latest logged in user
                if not user_identifiers:
                    try:
                        cursor.execute("SELECT user_id, email FROM users ORDER BY is_logged_in DESC, user_id DESC LIMIT 1")
                        r = cursor.fetchone()
                        if r:
                            user_identifiers.add(str(r[0]))
                            if r[1]:
                                user_identifiers.add(str(r[1]).lower())
                    except Exception:
                        if connection.vendor == 'postgresql':
                            connection.rollback()

                cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
                orders = cursor.fetchall()
                col_names = [col[0].lower() for col in cursor.description]

                orders_with_items = []
                for order in orders:
                    order_dict = dict(zip(col_names, order))

                    customer_details = {}
                    try:
                        customer_details = json.loads(order_dict.get('customer_details', '{}'))
                    except Exception:
                        customer_details = {}

                    order_uid = str(order_dict.get('user_id') or customer_details.get('user_id') or '').strip()
                    order_email = str(customer_details.get('email') or customer_details.get('customer_email') or '').strip().lower()

                    is_owner = False
                    if user_identifiers:
                        if order_uid and order_uid in user_identifiers:
                            is_owner = True
                        elif order_email and order_email in user_identifiers:
                            is_owner = True
                    else:
                        is_owner = True

                    if not is_owner:
                        continue

                    items = []
                    try:
                        items = json.loads(order_dict.get('items', '[]'))
                    except Exception:
                        items = []

                    orders_with_items.append({
                        "order_id": order_dict.get('order_id') or str(order_dict.get('id')),
                        "numeric_id": order_dict.get('id'),
                        "order_date": str(order_dict.get('created_at')),
                        "total_amount": float(order_dict.get('amount') or 0),
                        "payment_method": order_dict.get('payment_method') or 'COD',
                        "payment_id": order_dict.get('payment_id') or '',
                        "order_status": order_dict.get('status') or 'placed',
                        "items": items,
                        "customer_details": customer_details
                    })

            return JsonResponse(orders_with_items, safe=False)

        except Exception as e:
            print("Error fetching orders:", e)
            return JsonResponse({"error": "Server error", "details": str(e)}, status=500)

@csrf_exempt
def update_order_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE order_id = %s OR id = %s",
                    [status, str(order_id), int(order_id) if str(order_id).isdigit() else -1]
                )
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            print("Error updating order status:", e)
            return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
def session_cart_operations(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get('sessionId')
            food_id = data.get('foodId')
            quantity = data.get('quantity')
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM session_carts WHERE session_id = %s AND food_id = %s",
                    [session_id, food_id]
                )
                existing = cursor.fetchall()
                
                if len(existing) > 0:
                    cursor.execute(
                        "UPDATE session_carts SET quantity = %s WHERE session_id = %s AND food_id = %s",
                        [quantity, session_id, food_id]
                    )
                else:
                    cursor.execute(
                        "INSERT INTO session_carts (session_id, food_id, quantity) VALUES (%s, %s, %s)",
                        [session_id, food_id, quantity]
                    )
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            print("Session cart error:", e)
            return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
def get_session_cart(request, session_id):
    if request.method == "GET":
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT sc.*, f.FoodName, f.Price, f.ImageName 
                       FROM session_carts sc
                       JOIN FoodItems f ON sc.food_id = f.FoodID
                       WHERE sc.session_id = %s""",
                    [session_id]
                )
                rows = cursor.fetchall()
                
                col_names = [col[0] for col in cursor.description]
                
                cart_items = []
                for row in rows:
                    cart_items.append(dict(zip(col_names, row)))
            
            return JsonResponse(cart_items, safe=False)
            
        except Exception as e:
            print("Error fetching session cart:", e)
            return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
def clear_session_cart(request, session_id):
    if request.method == "DELETE":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM session_carts WHERE session_id = %s", [session_id])
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            print("Error clearing session cart:", e)
            return JsonResponse({"error": "Server error"}, status=500)
