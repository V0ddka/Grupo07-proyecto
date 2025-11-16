from django.shortcuts import render
from .models import contenidos
from django.http import HttpResponse
# Create your views here.


def apuntes(request):
    apuntes = contenidos.objects.all()
    return render(request, 'apuntes/apuntes-base.html', {'apuntes': apuntes})

def apuntes_detalle(request,slug):
    apunte = contenidos.objects.get(slug=slug)
    apuntes = contenidos.objects.all()
    return render(request, 'apuntes/apuntes-detalle-base.html', {'apunt': apunte, 'apuntes': apuntes})