from typing import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from core.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from core.forms import *
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_SECRET))

# Create your views here.
def index(request):
    products = product.objects.all()
    return render(request,'core/index.html',{'product':products})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            print('True')
            form.save()
            print("Data saved successfully")
            messages.info(request,"Product added successfully.")
            return redirect('addproduct')
        else:
            print("not working")
            messages.info(request,'Product is not added.Try Again')
    else:
        form = ProductForm()
    return render(request,'core/add_product.html',{'form':form})


def product_desc(request,pk):
    products = product.objects.get(pk=pk)
    return render(request,'core/product_desc.html',{'product':products})

def add_to_cart(request,pk):
    Product = product.objects.get(pk=pk)
    #create order item
    order_item,created = orderitem.objects.get_or_create(
        product = Product,
        user = request.user,
        ordered = False,
    )
    #get qusery set of order object
    order_qs = order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        orders = order_qs[0]
        if orders.items.filter(product__pk = pk).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"Added Quantity Item")
            return redirect("productdesc",pk=pk)
        else:
            orders.items.add(order_item)
            messages.info(request,"Item added to Cart ")
            return redirect("productdesc",pk=pk)
    else:
        ordered_date = timezone.now()
        orders = order.objects.create(user=request.user,ordered_date= ordered_date)
        orders.items.add(order_item)
        messages.info(request,"Item added to cart")
        return redirect ("productdesc",pk=pk)
            

def orderlist(request):
    if order.objects.filter(user=request.user,ordered=False).exists():
        Order = order.objects.get(user=request.user,ordered=False)
        return render(request,'core/orderlist.html',{'order':Order})
    return render(request,'core/orderlist.html',{'message':'Your Cart is Empty'})
    

def additem(request,pk):
    Product = product.objects.get(pk=pk)
    #create order item
    order_item,created = orderitem.objects.get_or_create(
        product = Product,
        user = request.user,
        ordered = False,
    )
    #get qusery set of order object
    order_qs = order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        orders = order_qs[0]
        if orders.items.filter(product__pk = pk).exists():
            if order_item.quantity < Product.count:
                order_item.quantity += 1
                order_item.save()
                messages.info(request,"Added Quantity Item")
                return redirect("orderlist")
            else:
                messages.info(request,"Sorry! Product is out of stock")
                return redirect("orderlist")
        else:
            orders.items.add(order_item)
            messages.info(request,"Item added to Cart ")
            return redirect("productdesc",pk=pk)
    else:
        ordered_date = timezone.now()
        orders = order.objects.create(user=request.user,ordered_date= ordered_date)
        orders.items.add(order_item)
        messages.info(request,"Item added to cart")
        return redirect ("productdesc",pk=pk)


def removeitem(request,pk):
    item = get_object_or_404(product,pk=pk)
    order_qs = order.objects.filter(
        user = request.user,
        ordered = False,
    )
    if order_qs.exists():
        Order = order_qs[0]
        if Order.items.filter(product__pk=pk).exists():
            order_item = orderitem.objects.filter(
                product = item,
                user = request.user,
                ordered = False,
            )[0]
            if order_item.quantity >1:
                order_item.quantity -=1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request,'Item quantity was updated')
            return redirect('orderlist')
        else:
            messages.info(request,'This item is not in your cart')
            return redirect('orderlist')
    else:
        messages.info(request,"You Do not have any order")



def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render (request,'core/checkout.html',{'payment_allow':'allow'})
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        try:
            if form.is_valid():
                streetaddress =  form.cleaned_data.get('streetaddress')
                apartmentaddress = form.cleaned_data.get('apartmentaddress')
                country = form.cleaned_data.get('country')
                zipcode = form.cleaned_data.get('zipcode')

                checkout_address = CheckoutAddress(
                    user = request.user,
                    streetaddress = streetaddress,
                    apartmentaddress = apartmentaddress,
                    country = country,
                    zipcode=zipcode,
                )
                checkout_address.save()
                print("It should render the summary page")
                return render(request,'core/checkout.html',{'payment_allow':'allow'})
        except Exception as e:
            messages.warning(request,'Failed Checkout')
            return redirect ('checkoutpage')
    else:
        form = CheckoutForm()
        return render(request,'core/checkout.html',{'form':form})


def payment(request):
    try:
        Order = order.objects.get(user=request.user,ordered = False)
        address = CheckoutAddress.objects.get(user = request.user)
        order_amount = Order.get_total_price()
        order_currency = 'INR'
        order_receipt = Order.order_id
        notes = {
            'streetaddress' : address.streetaddress,
            'apartmentaddress' : address.apartmentaddress,
            'country' : address.country.name,
            'zipcode' : address.zipcode,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount = order_amount*100,
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture='0',
            )
        )
        print(razorpay_order['id'])
        Order.razorpay_order_id = razorpay_order['id']
        Order.save()
        print('It should render the summary page')
        return render(
            request,
            'core/paymentsummaryrazorpay.html',
            {
                'order' : Order,
                'order_id' : razorpay_order['id'],
                'orderId' : Order.order_id,
                'final_price' : order_amount,
                'razorpay_merchant_id' : settings.RAZORPAY_ID,
            }
        )
    
    except order.DoesNotExist:
        print('Order not found')
        return HttpResponse('404 Error')

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id','')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')
            print(payment_id,order_id,signature)
            params_dict ={
                'razorpay_order_id' : order_id,
                'razorpay_payment_id' : payment_id,
                'razorpay_signature' : signature,
            }
            try:
                order_db = order.objects.get(razorpay_order_id = order_id)
                print('Order Found')
            except:
                print("Order Not found")
                return HttpResponse('505 not found')
            order_db.razorpay_payment_id = payment_id 
            order_db.razorpay_signature = signature
            order_db.save()
            print('Working..........')
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result == None:
                print('Working Final Fine.....')
                amount = order_db.get_total_price()
                amount = amount * 100
                payment_status = razorpay_client.payment.capture(payment_id,amount)
                if payment_status is not None:
                    print('payment_status')
                    order_db.ordered = True
                    order_db.save()
                    print('Payment success')
                    checkout_address = CheckoutAddress.objects.get(user= request.user)
                    request.session[
                        'order_complete'
                    ] = 'Your order is successfully placed,You will receive your order within a week'
                    return render(request,'core/invoice.html',{'order':order_db,'payment_status':payment_status})
                else:
                    print('Payment failed')
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        'order_failed'
                    ] = 'unfortunately your order could not be placed,try again!'
                    return redirect('/')
            else:
                order_db.ordered = False
                order_db.save()
                return render (request,'core/paymentfailed.html')
        except:
            return HttpResponse('Error Occured')





def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        messages.info(request,"Login Failed.Please Try Again")
    return render(request,'core/login.html')






def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email =  request.POST.get('email')
        password = request.POST.get('password')
        confirm_password =  request.POST.get('confirm_password')
        phone =  request.POST.get('phone')
        #to check print(username,email)
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username already exists")
                return redirect('register')
            else:
                if User.objects.filter(email = email).exists():
                    messages.info(request,"Email already exists")
                    return redirect('register')
                else:
                    user = User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    data = customer(user=user,phone = phone)
                    data.save()
                    #login 
                    our_user = authenticate(username = username,password = password)
                    if our_user is not None:
                        login(request,user)
                        return redirect('index') 
        else:
            messages.info(request,"Password and Confirm Password mismatch")
            return redirect('register')  
    return render(request,'core/register.html')





def user_logout(request):
    logout(request)
    return redirect('/')


def invoice(request):
    return render(request,'core/invoice.html')