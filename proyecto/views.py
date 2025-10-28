from django.shortcuts import render
import os
ruta_base_texto = os.path.dirname(__file__)
carpeta_datos = "data"
nombre_archivo = "mi_palabra.txt"

ruta_absoluta_archivo = os.path.join(ruta_base_texto, carpeta_datos, nombre_archivo)
def home (request):
    return render(request,'home.html')
# mi_proyecto/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import requests
import json

# URL del modelo de lenguaje en Hugging Face
API_URL = "https://router.huggingface.co/hf-inference/"
headers = {"Authorization": f"Bearer {config('HF_API_KEY')}"}

def query_huggingface(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "max_new_tokens": 100,
                "temperature": 0.7,
                "return_full_text": False
            }
        )
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

@csrf_exempt
def inicio(request):
    if request.method == 'POST':
        palabra_usuario = request.POST.get('palabra', '').strip()
        palabra_correcta = "canción"
        
        # Prompt para el modelo
        prompt = f"""
        Analiza el error ortográfico en la palabra "{palabra_usuario}" que debería ser "{palabra_correcta}".
        Devuelve solo un JSON con:
        {{
            "variable1": "parte inicial correcta",
            "variable2": "error o tilde faltante",
            "variable3": "parte final",
            "regla": "explicación de la regla ortográfica"
        en la regla trata de escribir de forma clara y concisa la regla ortográfica aplicable
        }}
        Ejemplo: {{"variable1": "canci", "variable2": "ó", "variable3": "n", "regla": "Palabras agudas terminadas en n, s o vocal llevan tilde"}}
        """
        
        try:
            # Llamar a Hugging Face
            respuesta_texto = query_huggingface(prompt)
            
            # Intentar convertir a JSON
            resultado = json.loads(respuesta_texto)
            
        except:
            # Si falla el JSON, usar respuestas predefinidas
            resultado = usar_respuestas_predefinidas(palabra_usuario)
        
        return render(request, 'resultado.html', {
            'resultado': resultado,
            'palabra_usuario': palabra_usuario
        })
    
    return render(request, 'formulario.html')

def usar_respuestas_predefinidas(palabra):
    """Respuestas de respaldo si Hugging Face falla"""
    errores = {
        'cancion': {
            'variable1': 'canci',
            'variable2': 'ó',
            'variable3': 'n',
            'regla': 'Las palabras agudas terminadas en n, s o vocal llevan tilde'
        },
        'cansión': {
            'variable1': 'can',
            'variable2': 's',
            'variable3': 'ión',
            'regla': 'Después de vocal se usa "c" en "ción", no "s"'
        },
        'cancíon': {
            'variable1': 'can',
            'variable2': 'cí',
            'variable3': 'on',
            'regla': 'La tilde va en la "o", no en la "i"'
        },
        'canción': {
            'variable1': '¡Correcto!',
            'variable2': '',
            'variable3': '',
            'regla': 'Has escrito perfectamente la palabra'
        }
    }
    
    return errores.get(palabra.lower(), {
        'variable1': palabra,
        'variable2': '?',
        'variable3': '',
        'regla': 'Prueba con: cancion, cansión, canción'
    })