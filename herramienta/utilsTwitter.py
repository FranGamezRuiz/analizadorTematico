import time
import tweepy
from tweepy import Stream, AppAuthHandler
from tweepy.streaming import StreamListener
from herramienta.keys import consumer_key, consumer_secret, access_key, access_secret, license_key_MC
from herramienta.models import Tweet
from textblob import TextBlob
import meaningcloud
import json
import re
from unicodedata import normalize


###########################
#   Variables gobales     #
###########################
tema_global = ''
temaPal_global = ''
categoria_global = ''
categoriaPal_global = ''
def modificarGlobal(nombreTema, nombreCate, palClaveTema, palClaveCate):
    global tema_global
    tema_global = nombreTema
    global categoria_global
    categoria_global = nombreCate
    global temaPal_global
    temaPal_global = palClaveTema
    global categoriaPal_global
    categoriaPal_global = palClaveCate


###########################
#   Autenticación Twitter #
###########################
def get_auth(tipo):
    if tipo == 'stream':
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
    else:
        auth = AppAuthHandler(consumer_key, consumer_secret)
    return auth


##################################
#      Análisis con TextBlob     #
##################################
def analisisText(full_text):
    textoTextBlob = TextBlob(full_text)
    textoIngles = textoTextBlob.translate(to='en')
    print(textoIngles)
    polarity = textoIngles.sentiment.polarity
    if polarity < 0:
        polaridad = "Negativo"
    elif polarity == 0:
        polaridad = "Neutro"
    elif polarity > 0:
        polaridad = "Positivo"

    return (polaridad,polarity)

##################################
#     Análisis con MeaningCloud   #
##################################
def analisisMeaning(full_text):
    analisis = meaningcloud.SentimentResponse(
        meaningcloud.SentimentRequest(license_key_MC, lang='es', txt=full_text, txtf='plain').sendReq())

    if analisis.getGlobalScoreTag() == 'N+':
        polaridad = "Negativo"
        polarity = -1
    elif analisis.getGlobalScoreTag() == 'N':
        polaridad = "Negativo"
        polarity = -0.5
    elif analisis.getGlobalScoreTag() == 'P':
        polaridad = "Positivo"
        polarity = 0.5
    elif analisis.getGlobalScoreTag() == 'P+':
        polaridad = "Positivo"
        polarity = 1
    else:
        polaridad = "Neutro"
        polarity = 0

    return (polaridad,polarity)

#############################
#   Formatear la fecha tw   #
#############################
def formateoFecha(fecha):
    fecha = str(fecha)
    months = {'Jan':'01','Feb':'02', 'Mar':'03', 'Apr':'04','May':'05','June':'06','Jun':'06',
              'July':'07','Jul':'07','Aug':'08','Sept':'09','Oct':'10','Nov':'11', 'Dec':'12'}
    fecha = fecha.split()
    fechaFormat = "{}-{}-{}".format(fecha[5], months[fecha[1]], fecha[2])

    return fechaFormat

##################################
#     minuscula y sin tildes     #
##################################
def eliminarTildes(texto):
    texto = str(texto).lower()
    # -> NFD y eliminar diacríticos para las tildes
    texto = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", texto), 0, re.I
    )
    # -> NFC
    texto = normalize('NFC', texto)
    print("Sin tildes: ",format(texto))

    return texto

##############################################
#     Buscar coincidencias palabras clave    #
##############################################
def findPalClave(array,texto):
    palabraT = ''
    palabras = []
    posiciones = []
    repetidos = []
    for pa in array:
        if pa != ' ':
            palabraT += pa
        else:
            palabras.append(palabraT)
            palabraT = ''
    palabras.append(palabraT)
    print(palabras)
    for pal in palabras:
        posiciones.append(texto.find(pal))
    if -1 not in posiciones:
        return 0
    else:
        for pos in posiciones:
            if pos < 0:
                repetidos.append(pos)
        if len(posiciones) > len(repetidos):
            return 0
    return -1

################################
#     Buscar coincidencias     #
################################
def coincidenciaTexto(texto, categoria, tema, palClaveCate, palClaveTema):
    '''
    Como la búsqueda se realiza con un or en categoría y tema,
    si no aparece la categoria o el tema no pertenece a la dicha, con lo
    cual, se desecha el tweet.
    Cuando se haga una busqueda general del tema, la categoria
    se muestra con la palabra 'general' y no tiene porque aparecer
    en el tweet.
    :param texto: Texto del tweet
    :param categoria: Categoria a la que pertenece
    :return: categoria perteneciente
    '''
    texto = eliminarTildes(texto)
    categoriaT = eliminarTildes(categoria)
    temaT = eliminarTildes(tema)
    claveCat = eliminarTildes(palClaveCate)
    claveTem = eliminarTildes(palClaveTema)
    print(texto)
    print(categoriaT)
    print(temaT)
    if categoriaT != 'general':
        posicionC = texto.find(categoria)
        posicionCC = findPalClave(claveCat,texto) ##tengo que distinguir los espacios
        if posicionC < 0 and posicionCC < 0:
            categoria = 'general'
    posicionT = texto.find(temaT)
    posicionCT = findPalClave(claveTem,texto)
    if posicionT < 0 and posicionCT < 0:
        tema = 'no pertenece'


    print('Encontradas: ')
    print(categoria)
    print(tema)
    return (categoria,tema)

#############################
#     Procesar el tweet     #
#############################
def procesarTweet(data,maquina,busqueda, tema, categoria, palClaveCate, palClaveTema):
    if busqueda == 'actual':
        try:
            full_text = data['retweeted_status']['extended_tweet']['full_text']
        except:  # No es un retweet
            if data['truncated'] == True:
                full_text = data['extended_tweet']['full_text']
            else:
                full_text = data['text']
    else:
        try:
            full_text = data['retweeted_status']['full_text']
        except:  # No es un retweet
            full_text = data['full_text']

    categoria, temaEncontrado = coincidenciaTexto(full_text, categoria, tema, palClaveCate, palClaveTema)

    if temaEncontrado != 'no pertenece':

        if str(maquina) != 'TextBlob':
            polaridad,polarity = analisisMeaning(full_text)
        else:
            polaridad,polarity = analisisText(full_text)

        id_twitter = data['id']
        texto = full_text
        fecha_creado = formateoFecha(data['created_at'])
        truncado = bool(data['truncated'])
        try:
            geo = data['place']['bounding_box']['coordinates']
            coordenadas = data['place']['bounding_box']['coordinates']
            place = str(data['place']['full_name'])
        except:
            geo = data['geo']
            coordenadas = data['coordinates']
            place = data['place']
        numero_ret =int(data['retweet_count'])
        numero_fav = int(data['favorite_count'])
        esFav = bool(data['favorited'])
        esRet = bool(data['retweeted'])
        idioma = str(data['lang'])
        tweet = Tweet(fecha_creado=fecha_creado, id_twitter=id_twitter,texto=texto,truncado=truncado,geo=geo,coordenadas=coordenadas,place=place,numero_ret=numero_ret,numero_fav=numero_fav,esFavorito=esFav,esRetweet=esRet,idioma=idioma,tema=tema,categoría=categoria,polaridad=polaridad,numero_Polaridad=polarity,busqueda=busqueda,analisis=maquina)
        tweet.save()
        print('Guardo el tweet porque pertenece a ', format(tema))
    else:
        print('No guardo el tweet porque no pertenece a ',format(tema))


#############################
#   Clase streamListener    #
#############################
class MyStreamListener(StreamListener):
    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)
            print(data)
            print("Uno")
            procesarTweet(data,'TextBlob','actual',tema_global, categoria_global, categoriaPal_global, temaPal_global)
            return True
        except BaseException as e:
            print("Error en el dato: %s",format(str(e)))
        return True #True para que siga recolectando

    def on_error(self, status):
        if status == 420:
            return False #Parar por error de conexión
        elif status == 401:
            print('Error autenticación')
            return False
        elif status == 400:
            print('Solicitud incorrecta: Parámetros mal introducidos')
            return False
        elif status == 403:
            print('No hay productos Lab en la autenticación')
            return False
        else:
            print('Se para durante 15 min')
            time.sleep(60 * 15)  # Para los limites de la API
        print(status)
        return True

###############################
#   Función streamListener    #
###############################
def stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC):
    modificarGlobal(nombreTema, nombreCate, palabrasClaveT, palabrasClaveC)
    auth = get_auth('stream')
    twitter_stream = Stream(auth, MyStreamListener())
    palabra = []
    palabra.append(palabrasClave(nombreTema))
    palabra.append(palabrasClave(nombreCate))
    palabra.append(palabrasClave(palabrasClaveT))
    palabra.append(palabrasClave(palabrasClaveC))
    print('Busqueda con los parámetros: ',format(palabra))
    twitter_stream.filter(languages=['es'], track=palabra)

#############################
#     Función historica     #
#############################
def cursorHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina, fechaInic, fechaFin):
    '''
    Esta función permite la recolección de tweets a traves de la función cursor a traves de search, esta función
    tiene mayor restricción, con lo cual, se utiliza para cuando el número de recolección es inferior a 1000
    si en algún caso excede la velocidad de recolección, se para durante 15 minutos que es el tiempo para que
    vuelva a la velocidad normal de recolección de la API de twitter.
    :param nombreTema: nombre del tema para la búsqueda
    :param palabrasClaveT:  palabras clave sobre el tema
    :param nombreCate: nombre de la categoría
    :param palabrasClaveC: palabras clave para la categoría
    :param numTw: número de tweets a recolectar
    :param maquina: proceso para el análisis de sentimientos
    :param fechaInic: fecha de inicio para el análisis
    :param fechaFin: fecha de fin para el análisis
    :return:
    '''
    auth = get_auth('cursor')
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    palabra = []
    palabra.append(palabrasClave(nombreTema))
    palabra.append(palabrasClave(nombreCate))
    palabra.append(palabrasClave(palabrasClaveT))
    palabra.append(palabrasClave(palabrasClaveC))
    numTw = int(numTw)
    contTweet = 0
    busqueda = numTw
    sinceId = None
    max_id = -1
    while contTweet < numTw:
        busqueda = busqueda - contTweet
        try:
            if max_id <= 0:
                if not sinceId:
                    tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, lang='es', tweet_mode='extended').items(busqueda)
                else:
                    tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, since_id=sinceId, lang='es', tweet_mode='extended').items(busqueda)
            else:
                if not sinceId:
                    tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, max_id=str(max_id - 1), lang='es', tweet_mode='extended').items(busqueda)
                else:
                    tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, max_id=str(max_id - 1), since_id=sinceId, lang='es', tweet_mode='extended').items(busqueda)

            if not tweetemp:
                #No encontrado
                break
            for tweet in tweetemp:
                tweJason = tweet._json
                procesarTweet(tweJason, str(maquina), 'historica', nombreTema, nombreCate, palabrasClaveC,palabrasClaveT)

            contTweet += len(tweetemp)
            max_id = tweetemp[-1].id
        except tweepy.TweepError as e:
            time.sleep(60 * 15) #Para los limites de la API
            print(e.reason)
        except StopIteration:
            break

################################
#   Recolección con search     #
################################
def searchHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina, fechaInic, fechaFin):
    '''
    Esta función permite la recolección de tweets a traves de search, esta función recoge un máximo de tweet
    por búsqueda, cuando consigue esos tweets vuelve a realizar de nuevo la búsqueda y para ello, guarda el
    id del último tweet para que comience la búsqueda a través de ese tweet y así no repetir los tweets
    si en algún caso excede la velocidad de recolección, se para durante 15 minutos que es el tiempo para que
    vuelva a la velocidad normal de recolección de la API de twitter.
    :param nombreTema: nombre del tema para la búsqueda
    :param palabrasClaveT:  palabras clave sobre el tema
    :param nombreCate: nombre de la categoría
    :param palabrasClaveC: palabras clave para la categoría
    :param numTw: número de tweets a recolectar
    :param maquina: proceso para el análisis de sentimientos
    :param fechaInic: fecha de inicio para el análisis
    :param fechaFin: fecha de fin para el análisis
    :return:
    '''
    auth = get_auth('search')
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    palabra = []
    palabra.append(palabrasClave(nombreTema))
    palabra.append(palabrasClave(nombreCate))
    palabra.append(palabrasClave(palabrasClaveT))
    palabra.append(palabrasClave(palabrasClaveC))
    numTw = int(numTw)
    tweetsPorBusqueda = 100
    sinceId = None
    max_id = -1
    contTweets = 0
    while contTweets < numTw:
        try:
            if max_id <= 0:
                if not sinceId:
                    tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin,count=tweetsPorBusqueda,tweet_mode='extended')
                else:
                    tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin,since_id=sinceId,count=tweetsPorBusqueda,tweet_mode='extended')
            else:
                if not sinceId:
                    tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin,count=tweetsPorBusqueda, max_id=str(max_id - 1),tweet_mode='extended')
                else:
                    tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin, since_id=sinceId,count=tweetsPorBusqueda, max_id=str(max_id - 1),tweet_mode='extended')

            if not tweetemp:
                #No encontrado
                break
            for tweet in tweetemp:
                tweJason = tweet._json
                procesarTweet(tweJason, str(maquina),'historica',nombreTema, nombreCate, palabrasClaveC, palabrasClaveT)

            contTweets += len(tweetemp)
            max_id = tweetemp[-1].id

        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(60 * 15) #Para los limites de la API



################################
#   Función palabras clave     #
################################
def palabrasClave(array):
    '''
    Introduce la cadena de char que contiene las palabras clave
    y devuelve un string con las palabras clave y entre el espacio
    un OR para realizar correctamente la búsqueda. Si la palabra
    encontrada es general, es que la categoría es general y los
    tweets no tienen porque contener la palabra 'general' para
    mostrar una opinión general.
    :param array: Cadena que contiene las palabras clave
    :return: String de palabras clave
    '''
    palabraT = ''
    for pa in array:
        if pa != ' ':
            palabraT += pa
        else:
            palabraT += ' OR '
    if palabraT.lower() == 'general':
        palabraT = ''

    return palabraT