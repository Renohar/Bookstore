from collections import namedtuple
from django.urls import path
from core import views

urlpatterns = [
    path('',views.index,name ='index'),
    path('login/',views.user_login,name='login'),
    path('addtocart/<pk>',views.add_to_cart,name="addtocart"),
    path('register/',views.user_register,name='register'),
    path('logout/',views.user_logout,name='logout'),
    path('addproduct/',views.add_product,name="addproduct"),
    path('productdescription/<int:pk>',views.product_desc,name="productdesc"),
    path('orderlist/',views.orderlist,name="orderlist"),
    path('additem/<int:pk>',views.additem,name='additem'),
    path('removeitem/<int:pk>',views.removeitem,name='removeitem'),
    path('checkout_page',views.checkout_page,name="checkoutpage"),
    path('payment',views.payment,name='payment'),
    path('handlerequest',views.handlerequest,name='handlerequest'),
    path('invoice',views.invoice,name='invoice')
]
