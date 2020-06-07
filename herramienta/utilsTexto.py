from textblob import TextBlob
import meaningcloud
import re
from unicodedata import normalize
import unicodedata
from unidecode import unidecode
from herramienta.keys import license_key_MC

#######################
#      WORDCLOUD      #
#######################
def procesarTexto(text):
    texto = ''
    text = str(text).lower()
    palabraT = ''
    espacios = [' ','.',',','(',')','[',']','{','}',';',',',"!","¡","¿","?","'","\"","/",":","_"]
    preposiciones = ['a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'versus', 'durante']
    articulos = ['la','el','lo','los','las','un','una','unos','unas','aquel','aquella','aquellos','aquellas','eso','esa','esos','esas','del','de','que','cual','y']
    posesivos = ['mio','mi','tuyo','tu','suyo','su','mios','mis','tuyos','tus','suyos','sus',"https","http","www", "http:","https:"]
    for palabra in text:
        if palabra in espacios:
            if palabraT not in preposiciones and palabraT not in articulos and palabraT not in posesivos and len(palabraT) > 3:
                texto += palabraT+" "
            palabraT = ''
        else:
            palabraT += palabra

    return texto


##################################
#      Análisis con TextBlob     #
##################################
def analisisText(full_text):
    textoTextBlob = TextBlob(full_text)
    try:
        textoIngles = textoTextBlob.translate(to='en')
    except:
        textoIngles = textoTextBlob

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



##############################################
#   Quitar los emojis de los tweets          #
##############################################
def deEmojify(inputString):
    returnString = ""
    for character in inputString:
        try:
            character.encode("ascii")
            returnString += character
        except UnicodeEncodeError:
            replaced = unidecode(str(character))
            if replaced != '':
                returnString += replaced
            else:
                try:
                     returnString += "[" + unicodedata.name(character) + "]"
                except ValueError:
                     returnString += "[x]"

    return returnString


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
