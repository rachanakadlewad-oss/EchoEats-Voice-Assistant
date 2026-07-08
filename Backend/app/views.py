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
import os

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@csrf_exempt
def get_food_items(request):
    if request.method == "GET":
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM FoodItems")
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                food_items = []
                for row in rows:
                    food_items.append(dict(zip(columns, row)))
            return JsonResponse(food_items, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def process_voice(request):
    if request.method == "POST":
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
            
            response = openai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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
                temperature=0.7,
                max_tokens=500
            )
            
            print("AI Response:", response.choices[0].message.content)
            
            try:
                command_data = json.loads(response.choices[0].message.content)
            except:
                command_data = {
                    "command": "UNKNOWN",
                    "response": response.choices[0].message.content
                }
            
            return JsonResponse({
                "status": "Received ✅",
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
                    "UPDATE users SET is_logged_in = FALSE WHERE user_id = %s",
                    [user_id]
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
            user_id = data.get('userId')
            amount = data.get('amount')
            items = data.get('items')
            payment_method = data.get('paymentMethod', 'COD')
            
            print("Creating order:", {"userId": user_id, "amount": amount, "items": items, "paymentMethod": payment_method})
            
            if not user_id or not amount or not items or not len(items):
                return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)
            
            order_id = 'ORD_' + str(int(datetime.now().timestamp())) + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            
            items_json = json.dumps([{
                "name": item.get('FoodName'),
                "food_id": item.get('FoodID'),
                "quantity": item.get('Quantity'),
                "price": item.get('Price')
            } for item in items])
            
            customer_details = json.dumps({"user_id": user_id})
            
            razorpay_order_id = None
            if payment_method == 'UPI':
                try:
                    razorpay_order = razorpay_client.order.create({
                        'amount': int(float(amount) * 100),
                        'currency': 'INR',
                        'payment_capture': 1,
                        'receipt': order_id,
                        'notes': {
                            'user_id': user_id,
                            'order_id': order_id
                        }
                    })
                    razorpay_order_id = razorpay_order['id']
                    print(f"Razorpay order created: {razorpay_order_id}")
                except Exception as e:
                    print(f"Razorpay order creation failed: {e}")
                    return JsonResponse({"success": False, "error": "Payment gateway error: " + str(e)}, status=500)
            
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO orders 
                       (order_id, amount, currency, payment_method, status, items, customer_details, razorpay_order_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    [order_id, amount, 'INR', payment_method, 'placed', items_json, customer_details, razorpay_order_id]
                )
            
            response_data = {
                "success": True,
                "orderId": order_id,
                "message": "Order created successfully"
            }
            
            if payment_method == 'UPI' and razorpay_order_id:
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
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            order_id = data.get('orderId')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                payment_verified = True
            except Exception as e:
                print(f"Signature verification failed: {e}")
                return JsonResponse({"success": False, "error": "Payment verification failed"}, status=400)
            
            if payment_verified:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE orders 
                           SET payment_id = %s, 
                               status = 'completed'
                           WHERE order_id = %s""",
                        [razorpay_payment_id, order_id]
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
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM orders WHERE customer_details LIKE %s ORDER BY created_at DESC",
                    [f'%{user_id}%']
                )
                orders = cursor.fetchall()
                
                col_names = [col[0] for col in cursor.description]
                
                orders_with_items = []
                for order in orders:
                    order_dict = dict(zip(col_names, order))
                    
                    items = []
                    try:
                        items = json.loads(order_dict.get('items', '[]'))
                    except:
                        items = []
                    
                    customer_details = {}
                    try:
                        customer_details = json.loads(order_dict.get('customer_details', '{}'))
                    except:
                        customer_details = {}
                    
                    orders_with_items.append({
                        "order_id": order_dict.get('id'),
                        "order_date": order_dict.get('created_at'),
                        "total_amount": order_dict.get('amount'),
                        "payment_method": order_dict.get('payment_method'),
                        "payment_id": order_dict.get('payment_id'),
                        "order_status": order_dict.get('status'),
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
                    "UPDATE orders SET status = %s WHERE order_id = %s",
                    [status, order_id]
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