from django.shortcuts import render
import os
ruta_base_texto = os.path.dirname(__file__)
carpeta_datos = "data"
nombre_archivo = "mi_palabra.txt"

ruta_absoluta_archivo = os.path.join(ruta_base_texto, carpeta_datos, nombre_archivo)
def home (request):
    return render(request,'home.html')
