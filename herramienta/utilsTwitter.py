import time
import tweepy
from tweepy import Stream, AppAuthHandler
from tweepy.streaming import StreamListener
from herramienta.keys import consumer_key, consumer_secret, license_key_MC
from herramienta.models import Tweet
from textblob import TextBlob
import meaningcloud
import json

###########################
#   Variables gobales     #
###########################
tema_global = ''
categoria_global = ''
def modificarGlobal(nombreTema, nombreCate):
    global tema_global
    tema_global = nombreTema
    global categoria_global
    categoria_global = nombreCate


###########################
#   Autenticación Twitter #
###########################
def get_auth():
    auth = AppAuthHandler(consumer_key, consumer_secret)
    return auth


##################################
#      Análisis con TextBlob     #
##################################
def analisisText(full_text):
    textoTextBlob = TextBlob(full_text)
    textoIngles = textoTextBlob.translate(to='en')
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

#############################
#     Procesar el tweet     #
#############################
def procesarTweet(data,maquina,busqueda, tema, categoria):
    try:
        full_text = data['retweeted_status']['full_text']
    except:  # No es un retweet
        full_text = data['full_text']
    if str(maquina) != 'TextBlob':
        polaridad,polarity = analisisMeaning(full_text)
    else:
        polaridad,polarity = analisisText(full_text)

    id_twitter = data['id']
    texto = full_text
    fecha_creado = formateoFecha(data['created_at'])
    truncado = bool(data['truncated'])
    try:
        geo = data['geo']['coordinates']
        coordenadas = data['coordinates']['coordinates']
        place = str(data['place']['country']) + ' ' + str(data['place']['full_name'])
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



#############################
#   Clase streamListener    #
#############################
class MyStreamListener(StreamListener):
    def on_data(self, raw_data):
        try:
            self.filter['track']
            data = json.loads(raw_data)
            procesarTweet(data,'TextBlob','actual',tema_global, categoria_global)
            return True
        except BaseException as e:
            print("Error en el dato: %s" &str(e))
        return True #True para que siga recolectando

    def on_error(self, status):
        if status == 420:
            return False #Parar por error de conexión
        else:
            time.sleep(60 * 15)  # Para los limites de la API
        print(status)
        return True

###############################
#   Función streamListener    #
###############################
def stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC):
    modificarGlobal(nombreTema, nombreCate)
    auth = get_auth()
    twitter_stream = Stream(auth, MyStreamListener())
    palabra = []
    palabra.append(palabrasClave(nombreTema))
    palabra.append(palabrasClave(nombreCate))
    palabra.append(palabrasClave(palabrasClaveT))
    palabra.append(palabrasClave(palabrasClaveC))
    twitter_stream.filter(languages=['es'], track=palabra,tweet_mode='extended')

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
    auth = get_auth()
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    palabra = []
    palabra.append(palabrasClave(nombreTema))
    palabra.append(palabrasClave(nombreCate))
    palabra.append(palabrasClave(palabrasClaveT))
    palabra.append(palabrasClave(palabrasClaveC))
    numTw = int(numTw)
    for tweetemp in tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, lang='es', tweet_mode='extended').items(numTw):
        try:
            tweJason = tweetemp._json
            procesarTweet(tweJason, str(maquina),'historica', nombreTema, nombreCate)
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
    auth = get_auth()
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
                procesarTweet(tweJason, str(maquina),'historica',nombreTema, nombreCate)

            contTweets += len(tweetemp)
            max_id = tweetemp[-1].id

        except tweepy.TweepError as e:
            time.sleep(60 * 15) #Para los limites de la API
            print(e.reason)


################################
#   Función palabras clave     #
################################
def palabrasClave(array):
    '''
    Introduce la cadena de char que contiene las palabras clave
    y devuelve un string con las palabras clave y entre el espacio
    un OR para realizar correctamente la búsqueda
    :param array: Cadena que contiene las palabras clave
    :return: String de palabras clave
    '''
    palabraT = ''
    for pa in array:
        if pa != ' ':
            palabraT += pa
        else:
            palabraT += ' OR '

    return palabraT