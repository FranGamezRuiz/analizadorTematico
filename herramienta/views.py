from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect


from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from herramienta.forms import TemaForm, HistoricoForm, ActualForm
from herramienta.models import Tema, Tweet

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
    fechas = {tweet.fecha_creado: 1}
    for tweet in tweets:
        if tweet.fecha_creado not in fechas:
            fechas[tweet.fecha_creado] = tweet.numero_Polaridad
        else:
            numero = float(fechas.get(tweet.fecha_creado))
            numero += float(tweet.numero_Polaridad)
            del fechas[tweet.fecha_creado]
            numero = round(numero, 5)
            fechas[tweet.fecha_creado] = numero
    listaFecha = []
    listaValor = []
    for fecha, valor in fechas.items():
        listaFecha.append(fecha)
        tweetemp = tweets.filter(fecha_creado=fecha)
        cantidad = tweetemp.count()
        valor = round(float(valor)/float(cantidad),5)
        listaValor.append(str(valor))
    listaValor = list(reversed(listaValor))
    listaFecha = list(reversed(listaFecha))
    return (listaFecha, listaValor)

##################
#   PIE Grafica  #
##################
def pieGrafica(tweets):
    tweetPos = tweets.filter(polaridad='Positivo').count()
    tweetNeg = tweets.filter(polaridad='Negativo').count()
    tweetNeu = tweets.filter(polaridad='Neutro').count()
    return (tweetPos,tweetNeg,tweetNeu)

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
        tipoH = 'Historico'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema, busqueda=tipo)
    elif nTipo == 2:
        tipo = 'actual'
        tipoH = 'Actual'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema, busqueda=tipo)
    else:
        tipoH = 'Actual vs Historico'
        tweets = allTweets.filter(categoría=cate, tema=nombreTema)
        tweetsH = allTweets.filter(categoría=cate, tema=nombreTema,busqueda='historica')
        tweetsA = allTweets.filter(categoría=cate, tema=nombreTema,busqueda='actual')

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
    colores = []
    labels = []
    coloresMean = []
    labelsMean = []
    if recolectados != 0:
        tweetsTextBlob = tweets.filter(analisis='TextBlob')
        tweetsMean = tweets.filter(analisis='MeaningCloud')
        contTextBlob = tweetsTextBlob.count()
        contMeaning = tweetsMean.count()
        if contTextBlob > 0:
            # Evolución de la opinión por días
            listaFecha, listaValor = evolucionDia(tweetsTextBlob)
            # Pie grafica
            tweetPos, tweetNeg, tweetNeu = pieGrafica(tweetsTextBlob)
            labels = ['Negativo', 'Positivo', 'Neutro']
            colores = ["#FF4136", "#0074D9", "#A2EEC6"]
        if contMeaning > 0:
            # Evolución de la opinión por días
            listaFechaMean, listaValorMean = evolucionDia(tweetsMean)
            # Pie grafica
            tweetPosMean, tweetNegMean, tweetNeuMean = pieGrafica(tweetsMean)
            labelsMean = ['Negativo', 'Positivo', 'Neutro']
            coloresMean = ["#FF4136", "#0074D9", "#A2EEC6"]




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
        'labels2': labelsMean,
        'data2': [tweetNegMean, tweetPosMean, tweetNeuMean],
        'colors2': coloresMean,
        # Grafica evolución MeaningCloud
        'fechas2': listaFechaMean,
        'valores2': listaValorMean

    }
    return render(request, "herramienta/tema_graficas.html", context)


@login_required()
def temaGrGeneral_View(request, pk, tipo):

    tema, nombreTema, categorias = datos(pk)


    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'Historico'
    elif nTipo == 2:
        tipo = 'Actual'
    else:
        tipo = 'Actual vs Historico'
    labels = []
    data = []
    colors = []
    for categoria in categorias:
        labels.append(categoria.nombre+' positivo')
        labels.append(categoria.nombre+' negativo')
        labels.append(categoria.nombre+' neutro')
        objTweet = Tweet.objects.all()
        tweetTema = objTweet.filter(tema=nombreTema, busqueda=tipo, categoría=categoria)
        tweetPos = tweetTema.filter(polaridad='Positivo').count()
        tweetNeg = tweetTema.filter(polaridad='Negativo').count()
        tweetNeu = tweetTema.filter(polaridad='Neutro').count()
        data.append(tweetPos)
        data.append(tweetNeg)
        data.append(tweetNeu)
        colors.append("#FF4136")
        colors.append("#0074D9")
        colors.append("#A2EEC6")


    context = {
        'tema':nombreTema,
        'categorias':categorias,
        'tipo':tipo,
        'nTipo':nTipo,

        #Grafica
        'titulo':'General',
        'labels': labels,
        'data': data,
        'colors': colors
    }
    return render(request, "herramienta/tema_grGeneral.html", context)



#####################################
# CLASES para las vistas sobre temas
#####################################


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
    form_class = TemaForm
    #Hay que editar el success_url para obtener la clave del objeto
    def get_success_url(self):
        return reverse_lazy('tema-detalle-view', kwargs={'pk':self.object.id})

