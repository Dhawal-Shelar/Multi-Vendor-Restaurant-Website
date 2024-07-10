from django.shortcuts import render
from .models import *

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



def signIn(request):
    
    return render(request,"signup.html" )

def login(request):
    
    return render(request,"login.html" )