from django.shortcuts import render ,get_object_or_404 ,redirect
from .models import *
import logging
from datetime import datetime
import stripe
from django.http import JsonResponse
stripe.api_key = 'sk_test_51PZ88Z2K7YRi0VwqX3mTC5Gkgbfg55MIBCB8IBriLUQYLTbcVWBU3a2iTZYH7gtOsZ9evL7xwOzXjFCWOeO3HGAN0065iqIu6i'  # This should be set in settings.py, not here
STRIPE_PUBLISHABLE_KEY = "pk_test_51PZ88Z2K7YRi0VwqiuyAgrjU8rAd0XusB69D4VRCv9TjCDFfbZLdeEjgmRG2vVXWwn8eq9eowMX24lAlFZufzSZo00MLgsQaIv"
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
        
        
   
def view_cart(request):
    user = request.session.get('username')
    order_items = []
    total_sum = 0

    if user:
        user_obj = UserModel.objects.get(username=user)
        order_items = OrderItems.objects.filter(user=user_obj)

        for item in order_items:
            total_sum += item.items.item_price * item.quantity

    context = {
        'order_items': order_items,
        'total_sum': total_sum,
        'STRIPE_PUBLISHABLE_KEY': STRIPE_PUBLISHABLE_KEY,
    }
    print("what is happing")
    return render(request, 'cart.html', context)
   
   
   


def create_checkout_session(request):
    user = request.session.get('username')
    if not user:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    
    try:
        user_obj = UserModel.objects.get(username=user)
        order_items = OrderItems.objects.filter(user=user_obj)
        
        line_items = []
        for item in order_items:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.items.item_name,
                    },
                    'unit_amount': int(item.items.item_price * 100),  # Stripe requires integer amount in cents
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        
        cart = Cart.objects.create(order_items=order_items, is_confirm=True, date_confirm=datetime.now())
        cart.save()

        logging.info(f"Checkout session created: {session.id}")
        return JsonResponse({'sessionId': session.id})
    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        return JsonResponse({'error': str(e)}, status=500)
   
   
   
   
   
def logout(request):
    
    request.session["username"] = None
    
    return redirect("/login/")
   
   
def success(request):
    
    return render(request,"success.html")
   
   
from django.shortcuts import render
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
