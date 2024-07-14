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
    cat = Category.objects.all() 
    
    category = request.GET.get('category')
    counts = Menu.objects.count()
    data = Menu.objects.all()  # Default queryset if no category filter is applied
    
    print("this is username" , request.session.get('username'))
    
    if category:
        data = Menu.objects.filter(cat_name__category_name=str(category))
        counts = Menu.objects.filter(cat_name__category_name=str(category)).count()

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
        
        
        order_item = get_object_or_404(OrderItems, user=user, items=menu_item)

        if order_item.quantity > 0:
            order_item.quantity -= 1
            if order_item.quantity == 0:
                order_item.delete()
            else:
                order_item.save()
    
    return redirect('view_cart')  


        
   
def view_cart(request):
    user = request.session.get('username')
    order_items = []
    total_amount = 0

    if user:
        try:
            user_obj = UserModel.objects.get(username=user)
            order_items = OrderItems.objects.filter(user=user_obj)

     
            total_amount = sum(item.items.item_price * item.quantity for item in order_items)
            print(total_amount,'----------')

        except UserModel.DoesNotExist:
    
            pass
    
    context = {
        'order_items': order_items,
        'total_amount': total_amount,
        'RAZORPAY_KEY_ID': RAZORPAY_KEY_ID, 
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
            user = request.session.get('username')
            if not user:
                return JsonResponse({'error': 'User not authenticated'}, status=400)
            
            # Assuming UserModel is the model representing your user
            user_instance = UserModel.objects.get(username=user)
            
            order_items = OrderItems.objects.filter(user=user_instance)
            print(order_items, "this my order items")
            
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            
            data = json.loads(request.body)
            data['amount'] = int(data['amount']) * 100
    
            razorpay_order = client.order.create(data=data)
            
            if razorpay_order['status'] == 'created':
                # Create a Cart instance
                cart = Cart.objects.create(user=user_instance, cart_items=order_items.first(), is_confirm=True, date_confirm=datetime.now())
         
                cart.save()
          
                order_items.delete()
            
            response_data = {
                'orderId': razorpay_order['id'],
                'amount': int(data['amount']),
                'currency': data['currency'],
                'status': razorpay_order['status'] 
            }
            
            return JsonResponse(response_data)

        except razorpay.errors.BadRequestError as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST request required'}, status=405)

   
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
