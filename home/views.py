from django.shortcuts import render ,get_object_or_404 ,redirect
from .models import *
from datetime import datetime

# Create your views here.
def index(request):
    
    return render(request,"index.html")


def main(request):
    cat = Category.objects.all()  # Get all categories
    
    category = request.GET.get('category')
    counts = Menu.objects.count()
    data = Menu.objects.all()  # Default queryset if no category filter is applied
    
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
    
    
    
    user = UserModel.objects.get(username = username)
    
    if user :
        
        menu_item = get_object_or_404(Menu,pk = item_id)
        
        order_items  ,created = OrderItems.objects.get_or_create(user=user,items = menu_item , defaults =  { "quantity": 0})
    
        if not created :
            
            order_items.quantity +=1
            order_items.save()
            
            
        return redirect('/main')
        
        
     

def signIn(request):
    
    if request.method == "POST":
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password  = request.POST.get('passoword')
        created =  datetime.now()
        
        if UserModel.objects.filter(username= username).exists():
            context = {
                "message" : "User is already exist"
            }
            return  redirect('/login',context)
        
        else:
            user = UserModel(username = username,email=email,password=password,created_date =created)
            user.save()
            request.session[username] =  username
            return redirect('/deals')
    return render(request,"signup.html" )



def login(request):
    
    if request.method == "POST":
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = UserModel.objects.filter(user = username,password =password)
        
        if not user :
            context = {
                "message": "Something is invalid"
            }
            return render(request,"index.html" , context )
      
        
        
    
    return render(request,"login.html" )
