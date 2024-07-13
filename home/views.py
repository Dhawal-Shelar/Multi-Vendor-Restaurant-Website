from django.shortcuts import render ,get_object_or_404 ,redirect
from .models import *
import logging
from datetime import datetime
import stripe
from django.http import JsonResponse
import razorpay

RAZORPAY_KEY_ID = 'rzp_test_mvrpQw6DMA9i6b'
RAZORPAY_KEY_SECRET = '2eHOP95bcTioYHVuKbeO1RL7'
# Create your views here.
def index(request):
    print(request.session.get("username"),'ddddddddd')
    
    menu = Menu.objects.all()
    print(menu)
    
    return render(request,"index.html" ,{'data': menu})


def main(request):
    cat = Category.objects.all()  # Get all categories
    
    category = request.GET.get('category')
    counts = Menu.objects.count()
    data = Menu.objects.all()  # Default queryset if no category filter is applied
    
    print("this is username" , request.session.get('username'))
    
    if category:
        data = Menu.objects.filter(cat_name__category_name=str(category))
        counts = Menu.objects.filter(cat_name__category_name=str(category)).count()
    
    # Pass all context data in a single dictionary to render
    context = {
        'cat': cat,
        'data': data,
        'counts':counts
    }
    
    return render(request, 'main.html', context)



def add_to_cart(request ,item_id):
    
    username =  request.session.get('username') 
    
    print(item_id ,'dddddddddddddddddddddddddddddddddddd')
    
    
    user = UserModel.objects.get(username = username)
    
    if user :
        
        menu_item = get_object_or_404(Menu,pk = item_id)
        
        order_items  ,created = OrderItems.objects.get_or_create(user=user,items = menu_item , defaults =  { "quantity": 1})
    
        if not created :
            
            order_items.quantity +=1
            order_items.save()
            
     
        return redirect('/deals')
        


def remove_cart(request, item_id):
    username = request.session.get('username')
    
    if username:
        user = get_object_or_404(UserModel, username=username)
        menu_item = get_object_or_404(Menu, pk=item_id)
        
        # Retrieve the order item for this user and menu item
        order_item = get_object_or_404(OrderItems, user=user, items=menu_item)
        
        # If the order item exists, adjust quantity or delete if quantity <= 0
        if order_item.quantity > 0:
            order_item.quantity -= 1
            if order_item.quantity == 0:
                order_item.delete()
            else:
                order_item.save()
    
    return redirect('view_cart')  # Redirect to the cart page after removal


        
   
def view_cart(request):
    user = request.session.get('username')
    order_items = []
    total_amount = 0

    if user:
        try:
            user_obj = UserModel.objects.get(username=user)
            order_items = OrderItems.objects.filter(user=user_obj)

            # Calculate total amount
            total_amount = sum(item.items.item_price * item.quantity for item in order_items)
            print(total_amount,'----------')

        except UserModel.DoesNotExist:
            # Handle user not found error as per your application logic
            pass
    
    context = {
        'order_items': order_items,
        'total_amount': total_amount,
        'RAZORPAY_KEY_ID': RAZORPAY_KEY_ID,  # Assuming you have RAZORPAY_KEY_ID in your settings
    }

    return render(request, 'cart.html', context)
   
   

def checkout(request):
    # Dummy data for demonstration (replace with your actual logic)
    user = request.session.get('username')
    user_obj = UserModel.objects.get(username=user)
    order_items = OrderItems.objects.filter(user=user_obj)

   
    total_amount = sum(item['price'] * item['quantity'] for item in order_items)
    print('dsddddd',total_amount)
    
    context = {
        'order_items': order_items,
        'total_amount': total_amount,
        'RAZORPAY_KEY_ID': RAZORPAY_KEY_ID,
    }
    return render(request, 'checkout.html', context)

import json
def create_checkout_session(request):
    if request.method == 'POST':
        try:
         
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))
            
           
            data = json.loads(request.body)

            print(data,'ppppppppp')
            data['amount'] = int(data['amount']) * 100
            
    
            razorpay_order = client.order.create(data=data)


            response_data = {
                'orderId': razorpay_order['id'],
                'amount':  int(data['amount']) * 100,
                'currency': data['currency'],
            
            }
            print(response_data,'my response ')
            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'POST request required'})

   
def logout(request):
    
    request.session["username"] = None
    
    return redirect("/login/")
   
   
def success(request):
    
    return render(request,"success.html")
   
   

from .models import Cart, UserModel

def profile(request):
    username = request.session.get('username')  # Retrieve username from session

    # Assuming 'username' is a field in your User model or related to your Cart model
    user = UserModel.objects.get(username=username)  # Retrieve User object using username

    # Filter Cart items for the logged-in user that are confirmed
    cart_items = Cart.objects.filter(user=user, is_confirm=True)

    context = {
        'cart_items': cart_items
    }

    return render(request, 'mycarts.html', context)

   
   
   
   
     

def signIn(request):
    
    if request.method == "POST":
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password  = request.POST.get('password')
        created =  datetime.now()
        
        if UserModel.objects.filter(username= username).exists():
            context = {
                "message" : "User is already exist"
            }
            return  redirect('/login/',context)
        
        else:
            user = UserModel(username = username,email=email,password=password,created_date =created)
            user.save()
            request.session[username] =  username
            print('----------------')
            return redirect('/deals/')
    return render(request,"signup.html" )



def login(request):
    
    if request.method == "POST":
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = UserModel.objects.filter(username = username,password =password)
        
        if not user :
            context = {
                "message": "Something is invalid"
            }
            return render(request,"login.html" , context )
      
        
        else:
            request.session["username"] = username
            return redirect('/')
    
    return render(request,"login.html" )
