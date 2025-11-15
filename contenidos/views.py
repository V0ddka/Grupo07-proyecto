from django.shortcuts import render
from .models import contenidos
from django.http import HttpResponse
# Create your views here.


def apuntes(request):
    apuntes = contenidos.objects.all()
    return render(request, 'apuntes/apuntes.html', {'apuntes': apuntes})

def apuntes_bov(request,slug):
    apunte = contenidos.objects.get(slug=slug)
    return render(request, 'apuntes/apuntes.html', {'apunt': apunte})