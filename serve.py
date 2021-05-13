from flask import Flask, jsonify, request, render_template
import json
import pyttsx3 #para poder hablar (en principio no se va a usar )
import webbrowser #libreria para abrir o buscar paginas 
from datetime import date, timedelta, datetime #mide el tiempo
import pyowm  # tiempo por localidad 
import operator  # matematicas
import random  #oeprador aleatorio
import os  #Interactuar con el directorio del pc 
from re import split #dividir arrays
import wikipedia # libreria para conectar con wikipedia
import requests #libreria que se usa para el traductor 
#alarma
from time import localtime
from pygame import mixer
#librerias parteBio
from pypdb import *

app = Flask(__name__)


@app.route('/')
def Alexis():
    return render_template('Alexis.html') 

@app.route('/ComoSeUsa')
def ComoSeUsa():
    return render_template('ComoSeUsa.html') 

@app.route('/BioAlexis')
def BioAlexis():
    return render_template('BioAlexis.html') 

@app.route('/BioComoSeUsa')
def BioComoSeUsa():
    return render_template('BioComoSeUsa.html')

@app.route('/getdataBio/<Bioindex_no>', methods=['GET','POST'])
def data_getBio(Bioindex_no):
    if request.method == 'GET':
        print("Comando enviado por metodo GET ") 
        comandoBio = str(Bioindex_no)
        return parteBio(comandoBio)
    else:
        print("Comando enviado por metodo POST ")
        comandoBio = str(Bioindex_no)
        return parteBio(comandoBio)

def parteBio(comandoBio):
    if "buscar proteínas por ID" in comandoBio:
        IDs = comandoBio[24::]
        Ids_sin_espacio = IDs.replace(" ", "")
        busqueda = Query(Ids_sin_espacio, "PubmedIdQuery").search()
        return busqueda
    elif "busca artículos sobre" in comandoBio:
        articulo = comandoBio[22::]
        articulo_traducido = Traductor('es', 'en', articulo)
        buscar_articulos = find_papers(articulo_traducido, max_results=10)
        return "Esto es lo que he encontrado sobre " + articulo + ": " + str(buscar_articulos)
    elif "busca información sobre" in comandoBio:
        IDs = comandoBio[23::]
        IDs_sinEspacio = IDs.replace(" ", "")
        IDs_final = IDs_sinEspacio.upper()
        webbrowser.open("https://www.rcsb.org/structure/"+ format(IDs_final))
        info = get_info(IDs_final)
        return str(info.keys())
    else: 
        return "Aún no estoy programado para hacer esto..."


@app.route('/getdata/<index_no>', methods=['GET','POST'])
def data_get(index_no):

    if request.method == 'GET':
        print("Comando enviado por metodo GET ")        
        comando = str(index_no)
        return menuComandos(comando, f)
    else:
        print("Comando enviado por metodo POST ")
        comando = str(index_no)
        return menuComandos(comando)

def Traductor(source, target, comando):
    parametros = {'sl': source, 'tl': target, 'q': comando}
    cabeceras = {"Charset":"UTF-8","User-Agent":"AndroidTranslate/5.3.0.RC02.130475354-53000263 5.1 phone TRANSLATE_OPM5_TEST_1"}
    url = "https://translate.google.com/translate_a/single?client=at&dt=t&dt=ld&dt=qca&dt=rm&dt=bd&dj=1&hl=es-ES&ie=UTF-8&oe=UTF-8&inputm=2&otf=2&iid=1dd3b944-fa62-4b55-b330-74909a99969e"
    response = requests.post(url, data=parametros, headers=cabeceras)
    if response.status_code == 200:
        for x in response.json()['sentences']:
            return x['trans']
    else:
        return "Ocurrió un error"

def alarma(hora, minut):
    while True:
        if localtime().tm_hour == int(hora) and localtime().tm_min == int(minut):
            mixer.init()
            mixer.music.load("alarm-clock.mp3")
            mixer.music.play()
            break
    return "ALARMAAA!!"

def tiempo(comando):
    owm = pyowm.OWM("012391b16eee62f600c190ed3ac9bf09")
    casa = "Barcelona, Montcada i Reixach"
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(casa)
    w = observation.weather
    temp = w.temperature('celsius')
    status = w.detailed_status
    respuesta_traducida = Traductor("en", "es", status)
   
    if "ahora" in comando or "hoy" in comando:
        return ("Ahora hace " + str(int(temp['temp'])) + " grados y " + respuesta_traducida.lower())

    else:	
        return "No se reconoce comando de tiempo"

def abrirPaginas(comando):
    try:
        if comando == "abre YouTube" or comando == "abrir Youtube" or comando == " abre YouTube" or comando == " abrir Youtube":
            webbrowser.open_new_tab("https://www.youtube.com")
            return "Abriendo Youtube..."
        elif comando == "abre Google" or comando == "abrir Google" or comando == " abre Google" or comando == " abrir Google" :
            webbrowser.open_new_tab("https://www.google.com")
            return "Abriendo Google..."
        elif comando == "abre WhatsApp" or comando == "abrir WhatsApp" or comando == " abre WhatsApp" or comando == " abrir WhatsApp":
            webbrowser.open_new_tab("https://web.whatsapp.com/")
            return "Abriendo WhatsApp..."
        elif "abre explorador de archivos" in comando or "abrir explorador de archivos" in comando :
            os.startfile("C:/Users/Aleix")
            return "Abriendo explorador de archivos"
        else: 
            return "No estoy programado para hacer esto aún..."
    except TypeError:
        return ("Tienes un error tipografico, cuidado")
        pass
    
def wikipediaBuscar(comando):
    try:
        if "buscar en Wikipedia" in comando or "busca en Wikipedia" in comando:
            comando_busqueda = str(comando[19::])
            wikipedia_resultado = wikipedia.summary(comando_busqueda) 
            respuesta_traducida = Traductor("en", "es", wikipedia_resultado)
            return respuesta_traducida
        else:
            return "No estoy programado para hacer esto aún..."
    except wikipedia.exceptions.PageError:
        return "¡ERROR! El comando introducido no encuentra nada en la Wikipedia"
        
    except wikipedia.exceptions.DisambiguationError:
        return "¡ERROR! Especifica a que te refieres..."

def buscarComando(comando):
    if "buscar en Google" in comando:
        comando_busqueda = str(comando[17::])
        webbrowser.open("https://www.google.com/search?q={}".format(comando_busqueda))
        return "Buscando '" + comando_busqueda + "' en Google"
    elif "busca en Google" in comando:
        comando_busqueda = str(comando[16::])
        webbrowser.open("https://www.google.com/search?q={}".format(comando_busqueda))
        return "Buscando '" + comando_busqueda + "' en Google"
    elif "pon la canción" in comando:
        comando_busqueda = str(comando[14::])
        webbrowser.open("https://www.youtube.com/search?q={}".format(comando_busqueda))
        return "Buscando '" + comando_busqueda + "' en Youtube "
    else:
        return "No estoy programado para hacer esto aún..."

def calculadora(comando):
    if "cuál es la" in comando or "Cuanto es" in comando:
        return "'Cuál es la...' o 'Cuanto es' no se reconoce como comando de una calculadora"
    elif "suma" in comando:
        nums = split("\D+", comando)
        resultado = int(nums[1]) + int(nums[2])
        return comando[5::] +" = "+str(resultado)
    elif " + " in comando:
        nums = split("\D+", comando)
        resultado = int(nums[0]) + int(nums[1])
        return comando+" = "+str(resultado)
    elif "menos" in comando:
        if "resta" in comando:
            nums = split("\D+", comando)
            resultado = int(nums[1]) - int(nums[2])
            resultado_replace = str(comando[5::]).replace("menos", "-")
            return resultado_replace +" = "+str(resultado)
        nums = split("\D+", comando)
        resultado = int(nums[0]) - int(nums[1])
        replace_comando = comando.replace("menos", "-")
        return replace_comando+" = "+str(resultado)
    elif "entre" in comando:
        if "divide" in comando:
            nums = split("\D+", comando)
            resultado = int(nums[1]) / int(nums[2])
            resultado_replace = str(comando[6::]).replace("entre", "/")
            return resultado_replace +" = "+str(resultado)
        nums = split("\D+", comando)
        resultado = int(nums[0]) / int(nums[1])
        replace_comando = comando.replace("entre", "/")
        return replace_comando+" = "+str(resultado)
    elif "por" in comando:
        if "multiplica" in comando:
            nums = split("\D+", comando)
            resultado = (float(nums[1]) * float(nums[2]))
            resultado_replace = str(comando[11::]).replace("por", "x")
            return resultado_replace +" = "+str(resultado)
        nums = split("\D+", comando)
        resultado = int(nums[0]) * int(nums[1])
        replace_comando = comando.replace("por", "x")
        return replace_comando+" = "+str(resultado)
    else: 
        return "No estoy programado para hacer esto aún..."

def Historial(comando):
    f = open("historial.txt", "a")
    f.write(comando +", ")
    f.close()

def leerArchivo():
    p = open("historial.txt", 'r')
    mensaje = p.read()
    return "Comandos usados: " + mensaje
    
def menuComandos(comando):
    if comando == "hola" or comando ==  " hola":
        saludos = ["Hola!", "Saludos!", "Buenas...", "Hola, me alegra oirte"]
        random_saludos = random.choice(saludos)
        Historial(comando)
        return random_saludos
    elif comando == " cómo estás" or comando == "cómo estás" or comando =="qué tal" or comando == " qué tal":
        estado = ["Estoy bien, gracias", "Podria estar mejor...", "Un poco cansado de tantas preguntas", "Muy bien!", "Listo para que me preguntes cualquier cosa"]
        random_estado = random.choice(estado)
        Historial(comando)
        return random_estado
    elif "quién eres" in comando:
        Historial(comando)
        return "Soy Alexis, un proyecto de DAW"
    elif "chiste" in comando:
        chistes = ["¿Cómo se llama el campeón de buceo japonés? \n Tokofondo. \n ¿Y el subcampeón? \n Kasitoko.", "- ¡Soldado López! \n ¡Sí, mi capitán! \n No lo vi ayer en la prueba de camuflaje \n ¡Gracias, mi capitán!",
        "Cariño, creo que estás obsesionado con el fútbol y me haces falta. \n ¡¿Qué falta?! ¡¿Qué falta?! ¡¡Si no te he tocado!!", "Van dos cieguitos por la calle pasando calor y dicen: \n Ojalá lloviera! \n ¡Ojalá yo también",
        "Si car es carro y men es hombre entonces Carmen es un transformer...", "Soy un tipo saludable \n Ah. ¿Comes sano y todo eso? \n No, la gente me saluda...", "¿Cómo se despiden los químicos? \n Ácido un placer...",
        "¿Cómo se dice escoba voladora en japonés? \n Simekaigo Memato.", "Como maldice un pollito a otro pollito? \n ¡Caldito seas!", " Mamá, mamá, el abuelo se cayó \n ¿Lo ayudaste hijo? \n No, se cayó solo."]
        random_chistes = random.choice(chistes)
        Historial(comando)
        return random_chistes
    elif "malo" in comando:
        return "Perdón, no soy tan bueno como tú.."
    elif "menú" in comando or "qué sabes hacer" in comando or "qué haces" in comando:
        Historial(comando)
        return "Esto es lo que puedo hacer: Me puedes preguntar por el tiempo de hoy, o tambien hacer calculos matematicos, buscar en Google o wikipedia entre otras cosas"
    elif "abre" in comando or "abrir" in comando:
        Historial(comando)
        return abrirPaginas(comando)
    elif "busca en Wikipedia" in comando or "buscar en Wikipedia" in comando:
        Historial(comando)
        return wikipediaBuscar(comando)
    elif "busca en Google" in comando or "buscar en Google" in comando or "pon la canción" in comando: 
        Historial(comando)
        return buscarComando(comando)
    elif "suma" in comando or " + " in comando or "menos" in comando or "resta" in comando or "divide" in comando or "entre" in comando or "multiplica" in comando or "por" in comando:
        Historial(comando)
        return calculadora(comando) 
    elif "tiempo" in comando:
        Historial(comando)
        return tiempo(comando)
    elif "traduce del español" in comando:   
        try:
            Historial(comando)
            comando_cc = str(comando[20::])
            respuesta_traducida = Traductor("es", "en", comando_cc)
            return respuesta_traducida
        except KeyError as e:
            return "Que quiere que traduzca?"
    elif "traduce del inglés" in comando:
        try:
            Historial(comando)
            comando_cc = str(comando[19::])
            respuesta_traducida = Traductor("en", "es", comando_cc)
            return respuesta_traducida
        except KeyError as e:
            return "Que quieres que traduzca?"
    elif "alarma" in comando:
        Historial(comando)
        nums = split("\D+", comando)
        hora = nums[1]
        minut = nums[2]
        return alarma(hora, minut)
    elif "historial" in comando:
        return leerArchivo()
    else:
        return "No estoy programado para hacer esto aún..."


if __name__ == "__main__":
    app.run(port=8080, debug=True)