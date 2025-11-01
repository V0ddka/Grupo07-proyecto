
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from random import randint, choice

def sustituir_b_por_v(palabra_original: str, num_fijo:int) -> str:
    
    palabra = palabra_original.lower()
    nueva_palabra = list(palabra)
    
    tildes =("á","é","í","ó","ú")
    notilde = ("a","e","i","o","u")
    prefijos = ('bi', 'bis', 'biz', 'bus', 'bur',"eva", "eve", "evi", "evo","hia","hie","hue","hui","hum")
    
    posibles_correcciones = []
    
    for prefijo in prefijos:
        if palabra.startswith(prefijo) and len(palabra) > len(prefijo):
            
            if prefijo[0] == 'b':
                if nueva_palabra[0] == "b":
                    posibles_correcciones.append([0,"Los prefijo como bi, bis, biz, bus, bur siempre les corresponde una b, estos tienen un significado y por ello siempre se escriben así" ])
                    break
            elif prefijo[0] == 'h':
                if palabra[0]== "h":
                    posibles_correcciones.append([0,"Palabras que empiezan con ia, ie, ue, ui les corresponde una h al inicio, además de la mayoría de palabras que empiezan con hum" ])
                    break
            elif prefijo[1] == 'v': 
                if palabra[1] == 'v':
                    
                    posibles_correcciones.append((1,"Prefijos como eva, eve, evi, evo les corresponde la v y no la b"))
                    break
                
    num = num_fijo%2
    for i in range(len(palabra)):
        if palabra[i] == 'b':
            
            if i > 0 and palabra[i-1] == 'm':
                nueva_palabra[i] = 'v'
                posibles_correcciones.append([i,"Después de la letra m corresponde la letra b, otra regla es que la letra v va después de una n"])
            
            elif i < len(palabra) - 1 and palabra[i+1] in ('l', 'r'):
                 posibles_correcciones.append([i,"La b va antes de las consonantes l y r, no la v"])
            elif num == 1:
                posibles_correcciones.append([i,"Le correspondia una b por regla general"])
        elif palabra[i] == "v":
            if i > 0 and (palabra[i-1] == 'n' or palabra[i-1] == 'b' or palabra[i-1] == 'd'):
                 posibles_correcciones.append([i,"Después de la letra n corresponde la letra v, otra regla es que la letra b va después de una m"])
            elif i > 0 and palabra[i-1] in "aei" and i < len(palabra) - 1 and palabra[i+1] in ('a', 'o'):
                
                 posibles_correcciones.append([i,"Los adjetivos (Una palabra que describe o califica) que terminan en avo, ava, evo, eva, ivo e iva les coresponde la v, a excepcion de las formas del verbo haber y palabras como silaba, cabo, jarabe, etc"])
            elif i > 0 and palabra[i-1] in "ae" and i < len(palabra) - 1 and palabra[i+1] == "e":
                posibles_correcciones.append([i,"Los adjetivos (Una palabra que describe o califica) que terminan en avo, ava, evo, eva, ivo e iva les coresponde la v, a excepcion de las formas del verbo haber y palabras como silaba, cabo, jarabe, etc"])
            elif i > 1 and palabra[i-2]== "o" and palabra[i-1]=="l":
                posibles_correcciones.append([i,"palabra terminada por olvo, olva llevan v"])

                
            elif num == 1:
                posibles_correcciones.append([i,"Le correspondia una v por regla general"])
        elif palabra[i]== "c":
            
            if i < len(palabra) - 1 and palabra[i+1:len(palabra)] in ("ito","ita","illo","illa","ico","ica","ión"):
                posibles_correcciones.append([i, "En terminaciones con ito, ita, illo, illa, ico, ica, ión corresponde usar la letra c mientras la palabra original no provenga con la letra z ó s, ejemplo mesa -> mesita (no es con c), camión -> camioncito (es con c)"])
        elif palabra[i] in tildes:
            k = tildes.index(palabra[i])
            posibles_correcciones.append([i, f"La palabra llevaba tilde , recuerda pensar en la acentuación de la palabra"])
            
        elif palabra[i] == "z" and num == 1:
            posibles_correcciones.append([i, "Aquí correspondia una z, recuerda pensar en la pronunciación de la palabra, la z es un sonido distindo al de la s"])
            
    
    if not posibles_correcciones:
        return [palabra, ""]
    indice_mod, regla = choice(posibles_correcciones)
    nueva_palabra[indice_mod] = "_"
    mala_y_correccion =["".join(nueva_palabra), regla]

    return mala_y_correccion

@login_required
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
                    request.session["mala"] = mala
                    request.session["Correccion"] = Correccion
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
            palabra_a_mostrar = dicc_p_malas[num_ale][1].split("_")
            bbbb = list(dicc_p_malas[num_ale][1])
            xxxx = bbbb.index("_")
            part1 = palabra_a_mostrar[0]
            part2 = palabra_a_mostrar[1]
            palabraBuena = dicc_p_malas[num_ale][0]
            letracorrecta = palabraBuena[xxxx]
            significado = dicc_p_malas[num_ale][2]
            correct = dicc_p_malas[num_ale][3]
    except FileNotFoundError:
        palabra_a_mostrar = "El archivo no fue encontrado."  
        significado= "El archivo no fue encontrado."             
    result = None
    texto = ''
    
    if request.method == 'POST':
        accion_solicitada = request.POST.get('accion')
        if accion_solicitada == 'saltar':
            
            request.session['mensaje_resultado'] = '¡Palabra saltada! Cargando una nueva...'
            
            
            if 'num_regla' in request.session:
                del request.session['num_regla']
            if 'num_ale' in request.session:
                del request.session['num_ale']
            
            
            return redirect('juego')
        elif accion_solicitada == 'validar':
            texto = request.POST.get('texto', '')
            if letracorrecta and texto.lower() == letracorrecta.lower():
                request.session['mensaje_resultado'] = f"¡Correcto! La palabra era {palabraBuena}."
                if 'num_regla' in request.session:
                    del request.session['num_regla']
                if 'num_palabra' in request.session:
                    del request.session['num_palabra']
                
                
                
                
            else:
                request.session['mensaje_resultado'] = f"Incorrecto ¡Inténtalo de nuevo!"
            mensaje = request.session.pop('mensaje_resultado', None)
            quepaso = None
            if mensaje:
                quepaso = {'mensaje': mensaje}
                texto = '' 
            result = {
                'mensaje': quepaso['mensaje'] if quepaso else '',
                'palabraBuena': palabraBuena,
                'correccion': correct,
                
                
            }

    return render(request, 'registration/juego.html', {'result': result, 'texto': texto, "part1": part1,"part2": part2,'mi_palabra': palabra_a_mostrar, 'significado': significado})



def home (request):
    return render(request,'home.html')
def registro_usuario(request):
    
    if request.method == 'POST':
        
        form = UserCreationForm(request.POST) 
        
        
        if form.is_valid():
            
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada.")
            return redirect('home') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                
                pass
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("home")

# mi_proyecto/views.py

#from django.shortcuts import render
#from django.views.decorators.csrf import csrf_exempt
#from decouple import config
#import requests
#import json

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