from decimal import Decimal

from bson import Decimal128
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
import csv
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from herramienta.forms import TemaForm, HistoricoForm, ActualForm, TemaUpdateForm
from herramienta.models import Tema, Tweet
#Para wordcloud
from herramienta.utilsTexto import procesarTexto
from django.shortcuts import render
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import urllib, base64
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
ps = PorterStemmer()
wnl = WordNetLemmatizer()

#Para la vista tareas
from background_task.models import Task, CompletedTask
import datetime

from herramienta.tasks import historico, actual


# FUNCIONES para las vistas
@login_required
def inicio_view(request):

    context = {

    }

    return render(request, 'herramienta/herramienta.html', context)

@login_required
def sobreMi_view(request):

    context = {

    }

    return render(request, 'herramienta/herramienta_about_me.html', context)

@login_required
def tareas_view(request):

    tareas = Task.objects.all()
    tareasCompletas = CompletedTask.objects.all()
    fechaHoy = datetime.date.today()

    context = {
        'tareas':tareas,
        'completas':tareasCompletas,
        'fechaHoy':fechaHoy
    }

    return render(request, 'herramienta/tareas.html', context)

################################################
# Función para recoger el tema y categoria
################################################
def datos(pk):
    variable = Tema.objects.all()  # Obtengo Todos los temas
    tema = variable.filter(pk=pk)  # tengo el tema
    nombreTema = tema.first()
    categorias = tema.first().getCategorias()  # tengo las categorias
    return (tema,nombreTema,categorias)

#################
#   Categorias
#################
@login_required
def categoriaDetail_View(request, pk, nombre):

    tema, nombreTema, categorias = datos(pk)
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre


    context = {
        'tema':nombreTema,
        'categoriaN':nombreCate,
        'tema.pk':pk,
        'categorias':categorias
    }

    return render(request, 'herramienta/categoria_detail.html', context)

##############################
#   Configuración de Busquedas
##############################
@login_required
def confiBusqueda_View(request, pk, nombre, tipo):

    tema, nombreTema, categorias = datos(pk)
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
    tipo = int(tipo)
    if tipo == 1:
        tipoN = 'historico'
    else:
        tipoN = 'actual'

    if request.method == 'POST':
        if tipoN == 'historico':
            formulario = HistoricoForm(request.POST)
            if formulario.is_valid():
                numeroTweets = formulario.cleaned_data['numeroTweets']
                fechaInic = formulario.cleaned_data['fechaInicio']
                fechaFin = formulario.cleaned_data['fechaFin']
                maquinaAnalisis = formulario.cleaned_data['maquinaAnalisis']

                return redirect('save-busq-hist-view', pk=pk, nombre=nombre, tipo=tipo, numTw=numeroTweets, fechaInic=fechaInic,
                                fechaFin=fechaFin, maquina=maquinaAnalisis)
        else:
            formulario = ActualForm(request.POST)
            if formulario.is_valid():
                fechaFin = formulario.cleaned_data['fechaFin']

                return redirect('save-busq-act-view', pk=pk, nombre=nombre, tipo=tipo, fechaFin=fechaFin)


    else:
        if tipoN == 'historico':
            formulario = HistoricoForm()
        else:
            formulario = ActualForm()



    context = {
        'tema':nombreTema,
        'categoria':nombreCate,
        'tema.pk':pk,
        'tipo':tipoN,
        'formulario':formulario
    }

    return render(request, 'herramienta/confi_busqueda.html', context)

###########################
#   Guardar Busq Historico
###########################

@login_required()
def saveBusqHist_View(request, pk, nombre, tipo, numTw, fechaInic, fechaFin, maquina):
    tema, nombreTema, categorias = datos(pk)
    palabrasClaveT = nombreTema.palabras_clave
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
            palabrasClaveC = categoria.palabras_clave


    historico(str(nombreTema), palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaInic, fechaFin)
    context = {
        'tema': nombreTema,
        'palabrasClaveTema': palabrasClaveT,
        'categoria': nombreCate,
        'palabrasClaveCate': palabrasClaveC,
        'numTw': numTw,
        'fechaInic':fechaInic,
        'fechaFin': fechaFin,
        'maquinaA': maquina

    }

    return render(request, 'herramienta/save_busqueda_hist.html', context)


###########################
#   Guardar Busq Actual
###########################


@login_required()
def saveBusqAct_View(request, pk, nombre, tipo,  fechaFin):
    tema, nombreTema, categorias = datos(pk)
    palabrasClaveT = nombreTema.palabras_clave
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
            palabrasClaveC = categoria.palabras_clave

    actual(str(nombreTema), palabrasClaveT, nombreCate, palabrasClaveC, fechaFin)

    context = {
        'tema': nombreTema,
        'palabrasClaveTema': palabrasClaveT,
        'categoria': nombreCate,
        'palabrasClaveCate': palabrasClaveC,
        'fechaFin': fechaFin,

    }

    return render(request, 'herramienta/save_busqueda_act.html', context)


#################
#   Dashboard   #
#################

#####################
#   Evolución/dia   #
#####################
def evolucionDia(tweets):
    '''
    Función para la creación de la grafica para observar la evolución
    de las opiniones por días, para calcular el número se realiza una
    media aritmetica con los valores obtenidos del análisis de
    sentimientos
    :param tweets: Objeto tweets filtrado
    :return:
    '''
    tweet = tweets.first()
    fecha1 = tweet.fecha_creado
    fechas = {fecha1: 1}
    for tweet in tweets:
        if tweet.fecha_creado not in fechas:
            fechas[tweet.fecha_creado] = tweet.numero_Polaridad
        else:
            numero = float(fechas.get(tweet.fecha_creado))
            numero += float(tweet.numero_Polaridad)
            del fechas[tweet.fecha_creado]
            numero = round(numero, 5)
            fechas[tweet.fecha_creado] = numero
    fechasSort = sorted(fechas)
    fechasTemp = {}
    for fecha in fechasSort:
        fechasTemp[fecha]=fechas.get(fecha)
    fechas = fechasTemp
    listaFecha = []
    listaValor = []
    for fecha, valor in fechas.items():
        listaFecha.append(fecha)
        tweetemp = tweets.filter(fecha_creado=fecha)
        cantidad = tweetemp.count()
        valor = round(float(valor)/float(cantidad),5)
        fechas[fecha] = valor
        listaValor.append(str(valor))

    return (listaFecha, listaValor, fechas)

##################
#   PIE Grafica  #
##################
def pieGrafica(tweets):
    tweetPos = tweets.filter(polaridad='Positivo').count()
    tweetNeg = tweets.filter(polaridad='Negativo').count()
    tweetNeu = tweets.filter(polaridad='Neutro').count()
    tweetPos = round(float((tweetPos / tweets.count()) * 100), 2)
    tweetNeg = round(float((tweetNeg / tweets.count()) * 100), 2)
    tweetNeu = round(float((tweetNeu / tweets.count()) * 100), 2)
    return (tweetPos,tweetNeg,tweetNeu)


def valorOrdenFecha(listaFecha, fechasTH, fechasT):
    array1=[]
    for fecha in listaFecha:
        if fecha in fechasTH.keys():
            array1.append(fechasTH.get(fecha))
        else:
            array1.append(0.0)
    array2 = []
    for fecha in listaFecha:
        if fecha in fechasT.keys():
            array2.append(fechasT.get(fecha))
        else:
            array2.append(0.0)
    return (array1,array2)

#########################
#   imagen wordcloud    #
#########################
def imagenPalabras(tweets):
    text = ''
    for tweet in tweets:
        text += tweet.texto
    text = procesarTexto(text)
    wc = WordCloud(scale=10, max_words=100, background_color="white").generate(text)
    plt.figure(figsize=(32, 18))
    plt.imshow(wc, interpolation="bilinear", aspect='auto')
    plt.axis("off")
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    return uri

@login_required()
def temaGraficas_View(request, pk, tipo, cate):

    tema, nombreTema, categorias = datos(pk)
    allTweets = Tweet.objects.all()  # Obtengo Todos los tweets

    cate = str(cate)
    if cate != '1':
        #Buscar la categoría
        for categoria in categorias:
            if categoria.nombre == cate:
                cate = categoria.nombre
    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'historica'
        tipoH = 'Histórico'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema, busqueda=tipo)
    elif nTipo == 2:
        tipo = 'actual'
        tipoH = 'Actual'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema, busqueda=tipo)
    else:
        tipoH = 'Actual vs Histórico'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema)
        tweetsH = allTweets.filter(categoría=cate, tema=nombreTema,busqueda='historica')
        tweetsA = allTweets.filter(categoría=cate, tema=nombreTema,busqueda='actual')

    #########

    try:
        uri = imagenPalabras(tweets)
    except:
        uri = ''

    #########
    recolectados = tweets.count()
    tweetPos = 0
    tweetNeg = 0
    tweetNeu = 0
    tweetPosMean = 0
    tweetNegMean = 0
    tweetNeuMean = 0
    contTextBlob = 0
    contMeaning = 0
    listaFecha = []
    listaValor = []
    listaFechaMean = []
    listaValorMean = []
    colores = ["#FF4136", "#0074D9", "#A2EEC6"]
    labels = ['Negativo', 'Positivo', 'Neutro']
    tweetNegH = 0
    tweetPosH = 0
    tweetNeuH = 0
    tweetNegA = 0
    tweetPosA = 0
    tweetNeuA = 0
    listaValorH = []
    fechasT = {}
    fechasTH = {}
    if recolectados != 0:
        if tipoH == 'Actual vs Histórico':
            #Historicos
            if tweetsH.count() > 0:
                # Evolución de la opinión por días
                listaFechaH, listaValorH, fechasTH = evolucionDia(tweetsH)
                # Pie grafica
                tweetPosH, tweetNegH, tweetNeuH = pieGrafica(tweetsH)

            #Actual
            if tweetsA.count() > 0:
                # Evolución de la opinión por días
                listaFecha, listaValor, fechasT = evolucionDia(tweetsA)
                # Pie grafica
                tweetPosA, tweetNegA, tweetNeuA = pieGrafica(tweetsA)
            try:
                listaFecha += ponerFechas(listaFechaH,listaFecha)
                listaFecha = sorted(listaFecha)
                listaValorH, listaValor = valorOrdenFecha(listaFecha,fechasTH,fechasT)
            except:
                listaFecha = []
                listaValorH = []
                listaValor = []


        else:

            tweetsTextBlob = tweets.filter(analisis='TextBlob')
            tweetsMean = tweets.filter(analisis='MeaningCloud')
            contTextBlob = tweetsTextBlob.count()
            contMeaning = tweetsMean.count()
            if contTextBlob > 0:
                # Evolución de la opinión por días
                listaFecha, listaValor, fechasT = evolucionDia(tweetsTextBlob)
                # Pie grafica
                tweetPos, tweetNeg, tweetNeu = pieGrafica(tweetsTextBlob)

            if contMeaning > 0:
                # Evolución de la opinión por días
                listaFechaMean, listaValorMean, fechasT = evolucionDia(tweetsMean)
                # Pie grafica
                tweetPosMean, tweetNegMean, tweetNeuMean = pieGrafica(tweetsMean)

    context = {
        'tema':nombreTema,
        'categorias':categorias,
        'tipo':tipoH,
        'nTipo':nTipo,
        'nTweets': recolectados,
        'tweetsTextBlob':contTextBlob,
        'tweetsMeaning':contMeaning,
        #Grafica pie TextBlob
        'titulo':cate,
        'labels': labels,
        'data': [tweetNeg, tweetPos, tweetNeu],
        'colors': colores,
        #Grafica evolución TextBlob
        'fechas':listaFecha,
        'valores':listaValor,
        # Grafica pie MeaningCloud
        'labels2': labels,
        'data2': [tweetNegMean, tweetPosMean, tweetNeuMean],
        'colors2': colores,
        # Grafica evolución MeaningCloud
        'fechas2': listaFechaMean,
        'valores2': listaValorMean,
        #ActualVSHistorico
        # Grafica pie Hist
        'dataHist': [tweetNegH, tweetPosH, tweetNeuH],
        # Grafica pie Act
        'dataAct': [tweetNegA, tweetPosA, tweetNeuA],
        # Grafica evolución Hist
        'valoresHist': listaValorH,
        # Grafica evolución Act
        'fechasAct': listaFecha,
        'valoresAct': listaValor,
        #######
        'image': uri

    }
    return render(request, "herramienta/tema_graficas.html", context)


def ponerFechas(listaFecha, fechasG):
    fechas = []
    for fecha in listaFecha:
        if fecha not in fechasG:
            fechas.append(fecha)

    return fechas

@login_required()
def temaGrGeneral_View(request, pk, tipo):

    tema, nombreTema, categorias = datos(pk)
    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'historica'
        tipoH = 'Histórico'
    elif nTipo == 2:
        tipo = 'actual'
        tipoH = 'Actual'
    else:
        tipo = 'Actual vs Historico'
        tipoH = 'Actual vs Histórico'
        allTweets = Tweet.objects.all()
        tweetsH = allTweets.filter(tema=nombreTema, busqueda='historica')
        tweetsA = allTweets.filter(tema=nombreTema, busqueda='actual')

    nombreCategorias = []
    labelsPos = []
    labelsNeg = []
    labelsNeu = []
    temaGeneralCount = 0
    temaGeneralCountH = 0
    listaValorH = []
    listaValorA = []
    data = []
    dataH = []
    fechas = []
    labels = {}
    dictNombreValor = []
    if tipo == 'Actual vs Historico':
        try:
            tweetPosH, tweetNegH, tweetNeuH = pieGrafica(tweetsH)
            tweetPos, tweetNeg, tweetNeu = pieGrafica(tweetsA)
            listaFechaH, listaValorH, fechasTH = evolucionDia(tweetsH)
            listaFechaA, listaValorA, fechasTA = evolucionDia(tweetsA)
            data = [tweetNeg, tweetPos, tweetNeu]
            temaGeneralCount = tweetsA.count()
            dataH = [tweetNegH, tweetPosH, tweetNeuH]
            temaGeneralCountH = tweetsH.count()
            fechas += ponerFechas(listaFechaH,fechas)
            fechas += ponerFechas(listaFechaA,fechas)
            fechas = sorted(fechas)
            listaValorH, listaValorA = valorOrdenFecha(fechas, fechasTH, fechasTA)

        except:
            temaGeneralCount = 0
            temaGeneralCountH = 0
            listaValorH = []
            listaValorA = []
            data = []
            dataH = []
            fechas = []
    else:
        for categoria in categorias:
            nombreCategorias.append(categoria.nombre)
            objTweet = Tweet.objects.all()
            tweetTema = objTweet.filter(tema=nombreTema, busqueda=tipo, categoría=categoria)
            numeroTotal = tweetTema.count()
            tweetPos = tweetTema.filter(polaridad='Positivo').count()
            tweetNeg = tweetTema.filter(polaridad='Negativo').count()
            tweetNeu = tweetTema.filter(polaridad='Neutro').count()
            try:
                listaFecha, listaValor, fechasT = evolucionDia(tweetTema)
                fechas += ponerFechas(listaFecha, fechas)
                labels[str(categoria.nombre)] = fechasT
                labelsPos.append(round(float((tweetPos / numeroTotal) * 100), 2))
                labelsNeg.append(round(float((tweetNeg / numeroTotal) * 100), 2))
                labelsNeu.append(round(float((tweetNeu / numeroTotal) * 100), 2))
            except:
                labelsPos.append(0)
                labelsNeg.append(0)
                labelsNeu.append(0)
        fechas = sorted(fechas)

        dictNombreValor = {}
        for nombreCat in labels:
            arrayT = []
            dictValor = labels.get(nombreCat)
            for fecha in fechas:
                valor = dictValor.get(fecha)
                if valor == None:
                    arrayT.append(0.0)
                else:
                    arrayT.append(dictValor.get(fecha))
            dictNombreValor[nombreCat] = arrayT

        try:
            temaGeneral = objTweet.filter(tema=nombreTema, busqueda=tipo)
            temaGeneralCount = temaGeneral.count()
            positivo, negativo, neutro = pieGrafica(temaGeneral)
            data = [positivo, negativo,neutro]
        except:
            temaGeneral = objTweet.filter(tema=nombreTema, busqueda=tipo)
            temaGeneralCount = temaGeneral.count()
            data = [0, 0, 0]

    context = {
        'tema':nombreTema,
        'categorias':categorias,
        'tipo':tipoH,
        'nTipo':nTipo,
        #Pie grafica
        'cantidadTotal':temaGeneralCount,
        'data':data,
        #Polaridad por categoria
        'titulo':'General',
        'labelsCat':nombreCategorias,
        'labelsPos':labelsPos,
        'labelsNeg':labelsNeg,
        'labelsNeu':labelsNeu,
        #Evolucion por dias
        'fechas':fechas,
        'labels':dictNombreValor,
        'valoresAct':listaValorA,
        'valoresHist':listaValorH,
        #Pie grafica Historica
        # Pie grafica
        'cantidadTotalH': temaGeneralCountH,
        'dataHist': dataH,
    }
    return render(request, "herramienta/tema_grGeneral.html", context)

#############################
#   Vista para los tweets   #
#############################
@login_required()
def tweetCate_View(request, pk,  tipo, cate):
    tema, nombreTema, categorias = datos(pk)

    tweets = Tweet.objects.all()

    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'historica'
        tipoH = 'Histórico'
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema, busqueda=tipo)
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate, busqueda=tipo)
    elif nTipo == 2:
        tipo = 'actual'
        tipoH = 'Actual'
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema, busqueda=tipo)
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate, busqueda=tipo)
    else:
        tipoH = 'Actual vs Histórico'
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema)
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate)

    paginator = Paginator(tweets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'tema':nombreTema,
        'categorias':categorias,
        'tipo':tipoH,
        'nTipo':nTipo,
        'titulo':cate,
        'tweets':tweets,
        'page_obj': page_obj
    }
    return render(request, "herramienta/tweets_view.html", context)

#######################
#    Descarga CSV     #
#######################
@login_required()
def csvdownload_View(request, pk, tipo, cate):
    tema, nombreTema, categorias = datos(pk)

    tweets = Tweet.objects.all()
    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'historica'
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema, busqueda=tipo)
            nombrefichero = 'tweets_' + str(nombreTema) + '_' + tipo
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate, busqueda=tipo)
            nombrefichero = 'tweets_' + str(nombreTema) + '_' + cate + '_' + tipo
    elif nTipo == 2:
        tipo = 'actual'
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema, busqueda=tipo)
            nombrefichero = 'tweets_' + str(nombreTema) + '_' + tipo
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate, busqueda=tipo)
            nombrefichero = 'tweets_' + str(nombreTema) + '_' + cate + '_' + tipo
    else:
        if cate == 'General':
            tweets = tweets.filter(tema=nombreTema)
            nombrefichero = 'tweets_' + str(nombreTema)
        else:
            tweets = tweets.filter(tema=nombreTema, categoría=cate)
            nombrefichero = 'tweets_' + str(nombreTema) + '_' + cate

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+nombrefichero+'.csv"'

    writer = csv.writer(response)
    writer.writerow(['fecha_creado','id_twitter','texto','truncado','geo','coordenadas','place','numero_ret','numero_fav','esFavorito','esRetweet','idioma','tema','categoría','polaridad','numero_Polaridad','busqueda','analisis'])

    for tweet in tweets:
        writer.writerow([tweet.fecha_creado, tweet.id_twitter, tweet.texto,tweet.truncado,tweet.geo,tweet.coordenadas,tweet.place,tweet.numero_ret,tweet.numero_fav,tweet.esFavorito,tweet.esRetweet,tweet.idioma,tweet.tema,tweet.categoría,tweet.polaridad,tweet.numero_Polaridad,tweet.busqueda,tweet.analisis])

    return response

@login_required()
def csvdownall_View(request):

    tweets = Tweet.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tweets.csv"'

    writer = csv.writer(response)
    writer.writerow(['fecha_creado','id_twitter','texto','truncado','geo','coordenadas','place','numero_ret','numero_fav','esFavorito','esRetweet','idioma','tema','categoría','polaridad','numero_Polaridad','busqueda','analisis'])

    for tweet in tweets:
        writer.writerow([tweet.fecha_creado, tweet.id_twitter, tweet.texto,tweet.truncado,tweet.geo,tweet.coordenadas,tweet.place,tweet.numero_ret,tweet.numero_fav,tweet.esFavorito,tweet.esRetweet,tweet.idioma,tweet.tema,tweet.categoría,tweet.polaridad,tweet.numero_Polaridad,tweet.busqueda,tweet.analisis])

    return response

######################################
# CLASES para las vistas sobre temas #
######################################


#Ver lista de Temas
class TemaListView(LoginRequiredMixin,ListView):
    model = Tema

#Ver un Tema
class TemaDetailView(LoginRequiredMixin,DetailView):
    model = Tema

#CU de TEMA
class TemaCreateView(LoginRequiredMixin, CreateView):
    model = Tema
    form_class = TemaForm
    #Hay que editar el success_url para obtener la clave del objeto
    success_url =  reverse_lazy('tema-list-view')

class TemaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tema
    form_class = TemaUpdateForm
    template_name_suffix = '_update_form'
    #Hay que editar el success_url para obtener la clave del objeto
    def get_success_url(self):
        return reverse_lazy('tema-detalle-view', kwargs={'pk':self.object.id})

