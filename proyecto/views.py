
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from random import randint, choice

def sustituir_b_por_v(palabra_original: str, num_fijo:int) -> str:
    
    palabra = palabra_original.lower()
    nueva_palabra = list(palabra)
    
    # 1. Regla de Prefijo (solo se aplica si la palabra comienza con el prefijo)
    tildes =("á","é","í","ó","ú")
    notilde = ("a","e","i","o","u")
    prefijos = ('bi', 'bis', 'biz', 'bus', 'bur',"eva", "eve", "evi", "evo","hia","hie","hue","hui","hum")
    prefijo_encontrado = False
    result_correccion = []
    for prefijo in prefijos:
        if prefijo in palabra[:3] and prefijo[-1]in palabra[1:3] and prefijo[0]==palabra[0] and len(palabra) > len(prefijo):
            
            if prefijo[0] == 'b':
                nueva_palabra[0] = 'v'
                prefijo_encontrado = True
                result_correccion.append("Prefijo como bi, bis, biz, bus, bur cambiado de b a v")
                break
            if prefijo[0] == 'h':
                nueva_palabra[0] = ''
                prefijo_encontrado = True
                result_correccion.append("Prefijo como hia, hie, hue, hui, hum se le quito la h")
                break
            elif prefijo[1] == 'v':
                nueva_palabra[1] = 'b'
                nueva_palabra[0] = "e"
                prefijo_encontrado = True
                result_correccion.append("Prefijo como eva, eve, evi, evo cambiado de v a b")
                break 
    inicio_busqueda = 1 if prefijo_encontrado else 0
    if inicio_busqueda == 1 and palabra[1]== "v":
        inicio_busqueda +=2
    num = num_fijo%2
    for i in range(inicio_busqueda, len(palabra)):
        if palabra[i] == 'b':
            # a) Antecedida por 'm' (mB -> mV)
            if i > 0 and palabra[i-1] == 'm':
                nueva_palabra[i] = 'v'
                result_correccion.append("b antecedida por m cambiada a v")
            
            #Seguida por 'l' o 'r' (Bl -> Vl, Br -> Vr)
            elif i < len(palabra) - 1 and palabra[i+1] in ('l', 'r'):
                 nueva_palabra[i] = 'v'
                 result_correccion.append("b seguida por l o r cambiada a v")
            elif num == 1:
                 nueva_palabra[i]= "v"
                 result_correccion.append("cambiamos la b a v por regla general")
        elif palabra[i] == "v":
            if i > 0 and (palabra[i-1] == 'n' or palabra[i-1] == 'b' or palabra[i-1] == 'd'):
                 nueva_palabra[i]= "b"
                 result_correccion.append("v antecedida por n, b o d cambiada a b")
            elif i > 0 and palabra[i-1] in "aei" and i < len(palabra) - 1 and palabra[i+1] in ('a', 'o'):
                
                 nueva_palabra[i]= "b"
                 result_correccion.append("palabra terminada por avo, ava, evo, eva, ivo e iva cambiando la v a b")
            elif i > 0 and palabra[i-1] in "ae" and i < len(palabra) - 1 and palabra[i+1] == "e":
                nueva_palabra[i]= "b"
            elif i > 1 and palabra[i-2]== "o" and palabra[i-1]=="l":
                nueva_palabra[i]= "b"
                
            elif num == 1:
                nueva_palabra[i]= "b"
                result_correccion.append("cambiamos la v a b por regla general")
        elif palabra[i]== "c":
            
            if i < len(palabra) - 1 and palabra[i+1:len(palabra)] in ("ito","ita","illo","illa","ico","ica","ión"):
                nueva_palabra[i]= "s"
                result_correccion.append("c cambiada a s por terminación ito, ita, illo, illa, ico, ica, ión")
        elif palabra[i] in tildes:
            k = 0
            for tilde in tildes:
                if tilde == palabra[i]:
                    nueva_palabra[i] =notilde[k]
                    result_correccion.append(f"Letra {notilde[k]} llevaba tilde y se la quitamos")
                    break
                k +=1
        elif palabra[i] == "z" and num == 1:

            nueva_palabra[i]= "s"
            result_correccion.append("z cambiada a s, para la proxima fijate en el sonido al pronunciarla")
     
    # Unir la lista de caracteres para formar la nueva palabra y mantener la mayúscula inicial
    resultado = "".join(nueva_palabra)
    
    if palabra_original[0].isupper():
        mala_y_correccion = [resultado, result_correccion]
        return resultado.capitalize()
    mala_y_correccion = [resultado, result_correccion]

    return mala_y_correccion



def juego_ortografia(request):
    ruta_base_texto = os.path.dirname(__file__)
    carpeta_datos = "data"
    nombre_archivo = "palabras_proyecto_ortografia.txt"
    ruta_absoluta_archivo = os.path.join(ruta_base_texto, carpeta_datos, nombre_archivo)
    palabra_a_mostrar = "No se encontró archivo"
    significado= "No se encontró archivo"
    if 'num_regla' not in request.session:
        request.session['num_regla'] = randint(1, 2)
    num_regla = request.session['num_regla']

    try:
        with open(ruta_absoluta_archivo, 'r', encoding='UTF-8') as archivo:
            dicc_todas_pal ={}
            dicc_p_malas ={}
            l = 0
            o = 1
            for linea in archivo:
                if l<5001:
                    l +=1
                    
                    datos_p = linea.strip().split("-")
                    if len(datos_p) < 3:
                        print(f"Advertencia: Saltando línea mal formateada: {linea.strip()}")
        
                        
                    
                        continue
                    numero = datos_p[0]
                    pal = datos_p[1]
                    
                    sig = datos_p[2]
                    mala = sustituir_b_por_v(pal,num_regla)[0]
                    Correccion = sustituir_b_por_v(pal,num_regla)[1]
                    dicc_todas_pal[numero] = [pal,mala,sig,Correccion]
                    
                    if mala != pal:
                        dicc_p_malas[o] =[pal,mala,sig,Correccion]
                        
                        o+= 1
            palabra_a_mostrar = dicc_p_malas
            if 'num_ale' not in request.session:
                request.session['num_ale'] = randint(1,len(dicc_p_malas)) 
            num_ale = request.session['num_ale']
            if num_ale not in dicc_p_malas:
                num_ale = randint(1, len(dicc_p_malas))
                while num_ale not in dicc_p_malas:  # sigue intentando hasta encontrar una clave válida
                    num_ale = randint(1, len(dicc_p_malas))    
            palabra_a_mostrar = dicc_p_malas[num_ale][1]
            palabraBuena = dicc_p_malas[num_ale][0]
            significado = dicc_p_malas[num_ale][2]
            correct = dicc_p_malas[num_ale][3]
    except FileNotFoundError:
        palabra_a_mostrar = "El archivo no fue encontrado."  
        significado= "El archivo no fue encontrado."             
    result = None
    texto = ''
    

    valor_de_python = "Hola desde Python"

    if request.method == 'POST':
        accion_solicitada = request.POST.get('accion')
        if accion_solicitada == 'saltar':
            
            request.session['mensaje_resultado'] = '¡Palabra saltada! Cargando una nueva...'
            
            # Borrar las claves de sesión para forzar nueva palabra y regla
            if 'num_regla' in request.session:
                del request.session['num_regla']
            if 'num_ale' in request.session:
                del request.session['num_ale']
            
            # Redirigir inmediatamente (POST-Redirect-GET)
            return redirect('juego')
        elif accion_solicitada == 'validar':
            texto = request.POST.get('texto', '')
            if palabraBuena and texto.lower() == palabraBuena.lower():
                request.session['mensaje_resultado'] = f"¡Correcto! La palabra era {palabraBuena}."
                if 'num_regla' in request.session:
                    del request.session['num_regla']
                if 'num_palabra' in request.session:
                    del request.session['num_palabra']
                
                # C) REDIRECCIÓN: Esto evita el reenvío del formulario
                
                
            else:
                request.session['mensaje_resultado'] = f"Incorrecto. La palabra correcta es: {palabraBuena}. ¡Inténtalo de nuevo!"
            mensaje = request.session.pop('mensaje_resultado', None)
            quepaso = None
            if mensaje:
                quepaso = {'mensaje': mensaje}
                texto = '' 
            result = {
                'mensaje': quepaso['mensaje'] if quepaso else '',
                'palabraBuena': palabraBuena,
                'correccion': "; ".join(correct),
                
                
            }

    return render(request, 'registration/juego.html', {'result': result, 'texto': texto, 'valor_de_python': valor_de_python,'mi_palabra': palabra_a_mostrar, 'significado': significado})



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
            return redirect('home') # Asegúrate de tener una URL con este nombre
            
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