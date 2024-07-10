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