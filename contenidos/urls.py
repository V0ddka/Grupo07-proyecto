from django.urls import path
from . import views
app_name='contenidos'

urlpatterns = [
    path('', views.apuntes, name='apuntes'),
    path('<slug:slug>', views.apuntes_bov, name='b-o-v'),
]