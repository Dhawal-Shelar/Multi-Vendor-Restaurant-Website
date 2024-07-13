from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('deals/', main, name='deals'),
    path('sign-in/', signIn),
    path('login/', login),
    path('add_cart/<int:item_id>/', add_to_cart, name='add_cart'),  # Updated this line
    path('cart/', view_cart),
      path('cart/', view_cart, name='view_cart'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('success/', success),
    path("logout/", logout),
    path('profile/', profile)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)