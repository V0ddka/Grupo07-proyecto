
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
ruta_base_texto = os.path.dirname(__file__)
carpeta_datos = "data"
nombre_archivo = "mi_palabra.txt"

ruta_absoluta_archivo = os.path.join(ruta_base_texto, carpeta_datos, nombre_archivo)
def home (request):
    return render(request,'home.html')
def registro_usuario(request):
    # 1. Si la solicitud es POST, el usuario está enviando datos
    if request.method == 'POST':
        # Instanciar el formulario con los datos POST
        form = UserCreationForm(request.POST) 
        
        # 2. Validar el formulario
        if form.is_valid():
            # 3. Guardar el nuevo usuario en la base de datos
            user = form.save()
            
            # Opcional: Loguear al usuario inmediatamente después del registro
            login(request, user)
            
            # Opcional: Agregar un mensaje de éxito
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada.")
            
            # 4. Redirigir a una página de éxito (ej. el inicio)
            return redirect('inicio') # Asegúrate de tener una URL con este nombre
            
    # 5. Si la solicitud es GET o el formulario es inválido,
    #    instanciar un formulario vacío o con errores para mostrar
    else:
        form = UserCreationForm()
        
    # 6. Renderizar la plantilla, pasando el formulario
    return render(request, 'registration/registro.html', {'form': form})
def login_view(request):
    # Si la solicitud es un POST, se envían los datos del formulario
    if request.method == 'POST':
        # Instanciamos el formulario de autenticación con los datos del POST
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # Los datos son válidos, intentamos autenticar
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autenticamos al usuario
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Si el usuario existe y las credenciales son correctas, lo logueamos
                login(request, user)
                # Redirigimos a la página de inicio (o la que tú definas)
                return redirect('home')  # Asegúrate de definir esta URL en 'urls.py'
            else:
                # Esto es manejado generalmente por form.is_valid() si usas AuthenticationForm
                # Si quieres un mensaje más específico, podrías agregarlo aquí.
                pass
        
        # Si el formulario no es válido (credenciales incorrectas),
        # el template mostrará form.errors (tu mensaje de alerta)
        # y renderizará el formulario de nuevo.

    # Si la solicitud es GET o el POST falla, mostramos el formulario
    else:
        form = AuthenticationForm()

    # Renderizamos la plantilla, pasando el formulario
    return render(request, 'registration/login.html', {'form': form})
# mi_proyecto/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import requests
import json

# URL del modelo de lenguaje en Hugging Face
'''API_URL = "https://router.huggingface.co/hf-inference/"
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
    })'''