from django.db import models
from django.conf import settings

# Create your models here.
class contenidos(models.Model):
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
