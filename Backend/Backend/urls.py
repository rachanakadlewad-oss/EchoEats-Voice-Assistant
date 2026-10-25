"""
URL configuration for Backend project.
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_food_items),
    path('voice/', views.process_voice),
    path('voice', views.process_voice),
    path('update-quantity/<int:id>/', views.update_quantity),
    path('update-quantity/<int:id>', views.update_quantity),
    path('login/', views.login_user),
    path('login', views.login_user),
    path('signup/', views.signup_user),
    path('signup', views.signup_user),
    path('logout/', views.logout_user),
    path('logout', views.logout_user),
    path('logout/<str:user_id>/', views.logout_user),
    path('logout/<str:user_id>', views.logout_user),
    path('create-order/', views.create_order),
    path('create-order', views.create_order),
    path('verify-payment/', views.verify_payment),
    path('verify-payment', views.verify_payment),
    path('orders/', views.get_user_orders),
    path('orders', views.get_user_orders),
    path('orders/<str:user_id>/', views.get_user_orders),
    path('orders/<str:user_id>', views.get_user_orders),
    path('api/orders/', views.get_user_orders),
    path('api/orders', views.get_user_orders),
    path('api/orders/<str:user_id>/', views.get_user_orders),
    path('api/orders/<str:user_id>', views.get_user_orders),
    path('update-order-status/<str:order_id>/', views.update_order_status),
    path('update-order-status/<str:order_id>', views.update_order_status),
    path('session-cart/', views.session_cart_operations),
    path('session-cart', views.session_cart_operations),
    path('session-cart/<str:session_id>/', views.get_session_cart),
    path('session-cart/<str:session_id>', views.get_session_cart),
    path('session-cart/clear/<str:session_id>/', views.clear_session_cart),
    path('session-cart/clear/<str:session_id>', views.clear_session_cart),
]