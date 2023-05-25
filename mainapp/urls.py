from django.urls import path
from .views import home, test

urlpatterns = [
    path('', home, name='home'),
    path('test/', test, name='home')
]