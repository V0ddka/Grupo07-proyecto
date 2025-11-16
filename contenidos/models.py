from django.db import models
from django.conf import settings

# Create your models here.
class contenidos(models.Model):
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
    slug = models.SlugField()
    iframe = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo