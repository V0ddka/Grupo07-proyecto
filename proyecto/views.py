from django.shortcuts import render
import os
ruta_base_texto = os.path.dirname(__file__)
carpeta_datos = "data"
nombre_archivo = "mi_palabra.txt"

ruta_absoluta_archivo = os.path.join(ruta_base_texto, carpeta_datos, nombre_archivo)
def home (request):
    try:
        with open(ruta_absoluta_archivo, 'r', encoding='utf-8') as archivo:
            palabrax = []
            for linea in archivo:
                linea_final = linea.strip().split()
                l = linea_final[0]

                palabrax.append(l)
    except FileNotFoundError:
        palabrax = []

    return render(request,'home.html', {'palabra': palabrax})

def login_view(request):
    return render(request, 'registration/login.html')