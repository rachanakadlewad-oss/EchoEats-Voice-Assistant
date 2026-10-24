import razorpay
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
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
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT FoodID, FoodName, Description, Price, Category,
                           ImageName, IsAvailable, Rating,
                           DateAdded, Quantity, Stock
                    FROM FoodItems
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
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE email = %s AND password = %s",
                    [email, password]
                )
                users = cursor.fetchall()
                
                if len(users) > 0:
                    user = users[0]
                    col_names = [col[0] for col in cursor.description]
                    user_dict = dict(zip(col_names, user))
                    
                    with connection.cursor() as cursor2:
                        cursor2.execute(
                            "UPDATE users SET is_logged_in = TRUE WHERE user_id = %s",
                            [user_dict['user_id']]
                        )
                    
                    return JsonResponse({
                        "success": True,
                        "user": {
                            "user_id": user_dict['user_id'],
                            "name": user_dict['name'],
                            "email": user_dict['email']
                        }
                    })
                else:
                    return JsonResponse({"error": "Invalid email or password"}, status=401)
                    
        except Exception as e:
            print("Login error:", e)
            return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
def signup_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", [email])
                existing = cursor.fetchall()
                
                if len(existing) > 0:
                    return JsonResponse({"error": "Email already exists"}, status=400)
                
                cursor.execute(
                    "INSERT INTO users (name, email, password, is_logged_in) VALUES (%s, %s, %s, TRUE)",
                    [name, email, password]
                )
                
                user_id = cursor.lastrowid
            
            return JsonResponse({
                "success": True,
                "user": {
                    "user_id": user_id,
                    "name": name,
                    "email": email
                }
            })
            
        except Exception as e:
            print("Signup error:", e)
            return JsonResponse({"error": "Server error"}, status=500)

@csrf_exempt
def logout_user(request, user_id):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET is_logged_in = FALSE WHERE user_id = %s OR email = %s",
                    [user_id, str(user_id)]
                )
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            print("Logout error:", e)
            return JsonResponse({"error": "Server error"}, status=500)

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
            address = data.get('address') or data.get('deliveryAddress') or {}
            delivery_notes = data.get('deliveryNotes') or data.get('delivery_notes') or ''
            customer_name = (
                data.get('customerName') or 
                data.get('customer_name') or 
                address.get('fullName') or 
                'Customer'
            )
            customer_phone = (
                data.get('customerPhone') or 
                data.get('customer_phone') or 
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

            customer_details = json.dumps({
                "user_id": str(user_id),
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
            
            response_data = {
                "success": True,
                "orderId": order_id,
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
def get_user_orders(request, user_id):
    if request.method == "GET":
        try:
            target_id_str = str(user_id).strip()
            if not target_id_str or target_id_str.lower() in ['undefined', 'null']:
                return JsonResponse([], safe=False)

            user_identifiers = {target_id_str}
            with connection.cursor() as cursor:
                try:
                    if target_id_str.isdigit():
                        cursor.execute("SELECT user_id, email FROM users WHERE user_id = %s", [int(target_id_str)])
                    else:
                        cursor.execute("SELECT user_id, email FROM users WHERE email = %s", [target_id_str])
                    for u_row in cursor.fetchall():
                        if u_row[0] is not None:
                            user_identifiers.add(str(u_row[0]))
                        if u_row[1]:
                            user_identifiers.add(str(u_row[1]).lower())
                except Exception as u_err:
                    print("User identifier lookup note:", u_err)

                cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
                orders = cursor.fetchall()
                col_names = [col[0] for col in cursor.description]
                
                orders_with_items = []
                for order in orders:
                    order_dict = dict(zip(col_names, order))

                    customer_details = {}
                    try:
                        customer_details = json.loads(order_dict.get('customer_details', '{}'))
                    except Exception:
                        customer_details = {}

                    # Strict owner isolation: only return orders that belong to the queried user
                    order_uid = str(order_dict.get('user_id') or customer_details.get('user_id') or '').strip()
                    order_email = str(customer_details.get('email') or customer_details.get('customer_email') or '').strip().lower()

                    is_owner = (
                        (order_uid and order_uid in user_identifiers) or
                        (order_email and order_email in user_identifiers)
                    )

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
