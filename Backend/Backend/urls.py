"""
URL configuration for Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('update-quantity/<int:id>/', views.update_quantity),  # Make sure this has trailing slash
    path('login/', views.login_user),
    path('signup/', views.signup_user),
    path('logout/<int:user_id>/', views.logout_user),
    path('create-order/', views.create_order),
    path('verify-payment/', views.verify_payment),
    path('orders/<int:user_id>/', views.get_user_orders),
    path('update-order-status/<str:order_id>/', views.update_order_status),
    path('session-cart/', views.session_cart_operations),
    path('session-cart/<str:session_id>/', views.get_session_cart),
    path('session-cart/clear/<str:session_id>/', views.clear_session_cart),
]