from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(UserModel)
admin.site.register(OrderItems)
admin.site.register(Cart)