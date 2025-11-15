from decouple import config
from django.http import HttpResponse
from google import genai

import os
import json
from google.genai import types
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from random import randint, choice

SESSION_KEY_INPUT = 'ultima_input_usuario'
SESSION_KEY_LISTA = 'ultima_lista_palabras'
FLAG = 'usar_denuevo'
NUM_PAL = 'holis'
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
            return redirect('lobby') 
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
                return redirect('lobby') 
            else:
                
                pass
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("home")

def lobby(request):
    request.session.pop(SESSION_KEY_LISTA, None)
    request.session.pop('juego_indice',None)
    request.session.pop(FLAG, False)
    return render(request,'lobby.html')


def account(request):
    return render(request,'account.html')

def palabra_por_contexto(request):
    api_key_value = os.getenv('GEMINI_APY_KEY')
    if not api_key_value:
        
        return HttpResponse("Error grave: GEMINI_API_KEY NO SE ENCONTRÓ en las variables de entorno.")
    
    client = genai.Client(api_key=api_key_value)
    respuesta_api = ""
    prompt_completo = ""
    lista_de_listas = []
    input_usuario =''
    ultima_consulta = None
    flag = request.session.get(FLAG)
    print("se detecto-----------------------", flag)
    if flag == True:
        input_usu = request.session.get(SESSION_KEY_INPUT)
        NUM = request.session.get(NUM_PAL)
        texto_base = (
            "Genera exactamente "+str(NUM)+ "palabras según el contexto personal y/o solicitud a continuación. "
            "Tu respuesta DEBE ser un objeto JSON con la clave 'datos_palabras'. "
            "El valor de 'datos_palabras' debe ser una lista de listas, "
            "donde CADA lista interior tenga EXACTAMENTE 5 elementos en el siguiente orden: "
            "[palabra_generada, significado_de_palabra (si vas a mencionar la palabra que elegiste en s significado, reemplaza la letra equivocada que elegiste en los elementos de la lista de mas adelante por un '_', ej si llegaras a mencionar árbol en el significado de árbol, escribelo _rbol), UNA_regla_ortografica_aplicable_a_esta_palabra, letra_equivocada_comun_relacionada_a_esta_regla_ortografica_en_esta_palabra(ej: si árbol lleva tilde por ser grave, quiero que me des la letra á, la letra tiene que ser la de la regla ortografica), indice_de_esa_letra]. "
            "Contexto:"
            )
        prompt_completo = texto_base + input_usu

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents= prompt_completo,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            json_string= response.text
            try:
                datos_dict = json.loads(json_string)
              
                lista_de_listas = datos_dict.get('datos_palabras', []) 
                if SESSION_KEY_LISTA not in request.session:
                    request.session[SESSION_KEY_LISTA] = lista_de_listas
                palabras_usuario = request.session[SESSION_KEY_LISTA]
                respuesta_api = f"Datos estructurados recibidos (Formato Python):\n{lista_de_listas[1]}"
                request.session[FLAG] = False
                return redirect('juego')
            except json.JSONDecodeError:
                
                respuesta_api = f"Error: La API no devolvió un JSON válido. Respuesta cruda: {json_string}"
                lista_de_listas = [] 
        except Exception as e:
            respuesta_api = f"Ocurrió un error al conectar con la API de Gemini: {e}"
        
        
        return redirect('juego')
    if request.method == 'POST':
        
        input_usuario = request.POST.get('input_usuario', '')
        num_palabras = request.POST.get('num_palabras', '')
        
        request.session[SESSION_KEY_INPUT] = input_usuario #por si falla antes estaba lista_de_listas
        request.session[NUM_PAL]= num_palabras
        
        texto_base = (
            "Genera exactamente "+str(num_palabras)+ "palabras según el contexto personal y/o solicitud a continuación. "
            "Tu respuesta DEBE ser un objeto JSON con la clave 'datos_palabras'. "
            "El valor de 'datos_palabras' debe ser una lista de listas, "
            "donde CADA lista interior tenga EXACTAMENTE 5 elementos en el siguiente orden: "
            "[palabra_generada, significado_de_palabra (si vas a mencionar la palabra que elegiste en s significado, reemplaza la letra equivocada que elegiste en los elementos de la lista de mas adelante por un '_', ej si llegaras a mencionar árbol en el significado de árbol, escribelo _rbol), UNA_regla_ortografica_aplicable_a_esta_palabra, letra_equivocada_comun_relacionada_a_esta_regla_ortografica_en_esta_palabra(ej: si árbol lleva tilde por ser grave, quiero que me des la letra á, la letra tiene que ser la de la regla ortografica), indice_de_esa_letra]. "
            "Contexto:"
            )   
        prompt_completo = texto_base + input_usuario

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents= prompt_completo,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            json_string= response.text
            try:
                datos_dict = json.loads(json_string)
              
                lista_de_listas = datos_dict.get('datos_palabras', []) 
                if SESSION_KEY_LISTA not in request.session:
                    request.session[SESSION_KEY_LISTA] = lista_de_listas
                palabras_usuario = request.session[SESSION_KEY_LISTA]
                respuesta_api = f"Datos estructurados recibidos (Formato Python):\n{lista_de_listas[1]}"
                return redirect('juego')
            except json.JSONDecodeError:
                
                respuesta_api = f"Error: La API no devolvió un JSON válido. Respuesta cruda: {json_string}"
                lista_de_listas = [] 
        except Exception as e:
            respuesta_api = f"Ocurrió un error al conectar con la API de Gemini: {e}"
    
    return render(request, 'palabra_por_contexto.html', {
        'response': respuesta_api,
        'ultima_consulta': ultima_consulta, 

    })

def juego_final(request):
    #hay que poner la url jijijij
    lista_palabras = request.session.get(SESSION_KEY_LISTA, None)
    #[palabra_generada, significado_de_palabra, letra_equivocada_comun, 
    # indice_de_esa_letra, regla_ortografica_aplicable]. "
    if not lista_palabras:
        return redirect('palabra_por_contexto')
    
    cant_palabras = len(lista_palabras)
    palabras_acabadas = False
    generar = False
    result = None
    texto = ''
    i = request.session.get('juego_indice', 0)
    if  i>= cant_palabras :
        palabras_acabadas = True
        #request.session.pop(SESSION_KEY_LISTA, None) 
        #request.session.pop('juego_indice', None)
        #return render(request, 'registration/juego.html', {'pal_acabadas': palabras_acabadas})
    if not palabras_acabadas:
        palabra_c = lista_palabras[i][0]
        significado = lista_palabras[i][1]
        #letra_e = lista_palabras[i][2]
        ind = lista_palabras[i][4]
        letra_e = palabra_c[ind]
        regla = lista_palabras[i][2]
        palabra_s = list(palabra_c)
        palabra_s[ind]= "_"
        pal_temp = "".join(palabra_s)
        temp = pal_temp.split("_")
        parte1 = temp[0]
        parte2 = temp[1]
    else:
        palabra_c = significado = ind = letra_e = regla = palabra_s = pal_temp = temp = parte1 = parte2 = None
    

    #if i >= cant_palabras:
    #    request.session.pop(SESSION_KEY_LISTA, None) 
    #    request.session.pop('juego_indice', None)
    if request.method == 'POST':
        accion_solicitada = request.POST.get('accion')
        if accion_solicitada == 'saltar':
            
            i += 1
            request.session['juego_indice'] = i
            request.session['mensaje_resultado'] = '¡Palabra saltada! Cargando una nueva...'
            
            return redirect('juego')
        
        elif accion_solicitada == 'validar':
            texto = request.POST.get('texto', '')
            if letra_e and texto.lower() == letra_e.lower():
                request.session['mensaje_resultado'] = f"¡Correcto! La palabra era {palabra_c}."
                
            else:
                request.session['mensaje_resultado'] = f"Incorrecto ¡Inténtalo de nuevo!"
            mensaje = request.session.pop('mensaje_resultado', None)
            quepaso = None
            if mensaje:
                quepaso = {'mensaje': mensaje}
                texto = '' 
            result = {
                'mensaje': quepaso['mensaje'] if quepaso else '',
                'palabraBuena': palabra_c,
                'correccion': regla,
            }
        elif palabras_acabadas == True:
                
            if accion_solicitada == "continuar":
                request.session[FLAG] = True
                request.session.pop(SESSION_KEY_LISTA, None) 
                request.session.pop('juego_indice', None)
                print("hola")
                return redirect("palabra_por_contexto")
            elif accion_solicitada == "cambiar":
                request.session.pop(SESSION_KEY_LISTA, None) 
                request.session.pop('juego_indice', None)
                print("-----------------------------")
                return redirect("palabra_por_contexto")
            
    return render(request, 'registration/juego.html', {'result': result, 'texto': texto, "part1": parte1,"part2": parte2,'mi_palabra': pal_temp, 'significado': significado, "pal_acabadas": palabras_acabadas})

    return render(request, 'prueba.html', {
        'response': lista_palabras

    })

