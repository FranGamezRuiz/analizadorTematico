import time
import tweepy
from tweepy import Stream, AppAuthHandler
from tweepy.streaming import StreamListener
from herramienta.keys import consumer_key, consumer_secret, access_key, access_secret
from herramienta.models import Tweet
from herramienta.utilsTexto import analisisMeaning, analisisText, formateoFecha, coincidenciaTexto, deEmojify, palabrasClave
import json
import datetime
###########################
#   Variables gobales     #
###########################
tema_global = ''
temaPal_global = ''
categoria_global = ''
categoriaPal_global = ''
fechaFin_global = ''
def modificarGlobal(nombreTema, nombreCate, palClaveTema, palClaveCate, fechaFin):
    global tema_global
    tema_global = nombreTema
    global categoria_global
    categoria_global = nombreCate
    global temaPal_global
    temaPal_global = palClaveTema
    global categoriaPal_global
    categoriaPal_global = palClaveCate
    global fechaFin_global
    fechaFin_global = fechaFin


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

#############################
#     Procesar el tweet     #
#############################
def procesarTweet(data,maquina,busqueda, tema, categoria, palClaveCate, palClaveTema):
    if busqueda == 'actual':
        try:
            full_text = data['retweeted_status']['extended_tweet']['full_text']
            esRet = True
        except:  # No es un retweet
            if data['truncated'] == True:
                full_text = data['extended_tweet']['full_text']
                esRet = False
            else:
                full_text = data['text']
                esRet = False
    else:
        try:
            full_text = data['retweeted_status']['full_text']
            esRet = True
        except:  # No es un retweet
            full_text = data['full_text']
            esRet = False

    full_text = deEmojify(full_text)
    categoria, temaEncontrado = coincidenciaTexto(full_text, categoria, tema, palClaveCate, palClaveTema)
    tweetEncontrado = Tweet.objects.all()
    encontrado = tweetEncontrado.filter(id_twitter=data['id'], busqueda=busqueda, analisis=maquina).count()

    if temaEncontrado != 'no pertenece' and encontrado <= 0:
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
        idioma = str(data['lang'])
        tweet = Tweet(fecha_creado=fecha_creado, id_twitter=id_twitter,texto=texto,truncado=truncado,geo=geo,coordenadas=coordenadas,place=place,numero_ret=numero_ret,numero_fav=numero_fav,esFavorito=esFav,esRetweet=esRet,idioma=idioma,tema=tema,categoría=categoria,polaridad=polaridad,numero_Polaridad=polarity,busqueda=busqueda,analisis=maquina)
        tweet.save()
        print('Guardo el tweet porque pertenece a ', format(tema))
    else:
        print('No guardo el tweet porque no pertenece a ',format(tema),'o ya estaba en la base de datos')


#############################
#   Clase streamListener    #
#############################
class MyStreamListener(StreamListener):
    def on_data(self, raw_data):
        try:
            fechaHoy = datetime.date.today()
            fechaHoy = fechaHoy.strftime("%Y-%m-%d")
            print(format(fechaHoy), " hasta ", format(fechaFin_global))
            if fechaHoy >= fechaFin_global:
                return False

            data = json.loads(raw_data)
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
def stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, fechaFin):
    modificarGlobal(nombreTema, nombreCate, palabrasClaveT, palabrasClaveC, fechaFin)
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
    max_id = -1
    while contTweet < busqueda:
        busqueda = busqueda - contTweet
        print(busqueda)
        try:
            if max_id <= 0:
               tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, lang='es', tweet_mode='extended').items(busqueda)
            else:
                tweetemp = tweepy.Cursor(api.search, palabra, since=fechaInic, until=fechaFin, max_id=str(max_id - 1), lang='es', tweet_mode='extended').items(busqueda)

            if not tweetemp:
                print('No encontrado')
                break
            for tweet in tweetemp:
                contTweet += 1
                tweJason = tweet._json
                max_id = tweJason['id']
                print(maquina)
                procesarTweet(tweJason, str(maquina), 'historica', nombreTema, nombreCate, palabrasClaveC,palabrasClaveT)

        except tweepy.TweepError as e:
            time.sleep(60 * 15) #Para los limites de la API
            print(e.reason)
        except StopIteration:
            break
        print('bucle')
    print('Termina el bucle')
    print('Entre ',format(fechaInic),' y ',format(fechaFin),' se han encontrado ',format(contTweet),' de ',format(numTw))

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
    max_id = -1
    contTweets = 0
    while contTweets < numTw:
        try:
            if max_id <= 0:

                tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin,count=tweetsPorBusqueda,tweet_mode='extended')
            else:
                tweetemp = api.search(q=palabra, since=fechaInic, until=fechaFin,count=tweetsPorBusqueda, max_id=str(max_id - 1),tweet_mode='extended')

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
    print('Entre ', format(fechaInic), ' y ', format(fechaFin), ' se han encontrado ', format(contTweets), ' de ',
          format(numTw))