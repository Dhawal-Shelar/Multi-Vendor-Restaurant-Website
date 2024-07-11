from django.db import models

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    
    
    def __str__(self) -> str:
        return self.category_name
    



class Menu(models.Model):
    
    cat_name = models.ForeignKey(Category,on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    item_price = models.IntegerField()
    discount_price = models.IntegerField()
    description = models.TextField()
    item_img  =models.ImageField(upload_to='media/')
    
    
    def __str__(self) -> str:
        return self.item_name
    
    

class UserModel(models.Model):
    
    username = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
    
    
    
class  OrderItems(models.Model):
    
    user = models.ForeignKey(UserModel,on_delete = models.CASCADE)
    items = models.ForeignKey(Menu,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_date = models.DateField(auto_created=True)
    
    
    def __str__(self):
        return self.user.username
    
