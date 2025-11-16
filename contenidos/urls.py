from django.urls import path
from . import views
app_name='contenidos'

urlpatterns = [
    path('', views.apuntes, name='apuntes-base'),
    path('<slug:slug>', views.apuntes_detalle, name='detalle-base'),
]