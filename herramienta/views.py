from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from herramienta.forms import TemaForm, HistoricoForm, ActualForm
from herramienta.models import Tema, Tweet

#Para la vista tareas
from background_task.models import Task, CompletedTask
import datetime

from herramienta.tasks import hello


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
                numeroTweets = formulario.cleaned_data['numeroTweets']
                fechaFin = formulario.cleaned_data['fechaFin']
                maquinaAnalisis = formulario.cleaned_data['maquinaAnalisis']

                return redirect('save-busq-act-view', pk=pk, nombre=nombre, tipo=tipo, numTw=numeroTweets,
                                fechaFin=fechaFin, maquina=maquinaAnalisis)

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

    #hello(str(nombreTema), palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaFin,repeat_until=fechaFin)

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
def saveBusqAct_View(request, pk, nombre, tipo, numTw, fechaFin, maquina):
    tema, nombreTema, categorias = datos(pk)
    palabrasClaveT = nombreTema.palabras_clave
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
            palabrasClaveC = categoria.palabras_clave

    #hello(str(nombreTema), palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaFin,repeat_until=fechaFin)

    context = {
        'tema': nombreTema,
        'palabrasClaveTema': palabrasClaveT,
        'categoria': nombreCate,
        'palabrasClaveCate': palabrasClaveC,
        'numTw': numTw,
        'fechaFin': fechaFin,
        'maquinaA': maquina

    }

    return render(request, 'herramienta/save_busqueda_act.html', context)


########################
#   Dashboard
########################
@login_required()
def temaGraficas_View(request, pk, tipo, cate):

    tema, nombreTema, categorias = datos(pk)
    cate = str(cate)
    if cate != '1':
        #Pertenece a un tema
        for categoria in categorias:
            if categoria.nombre == cate:
                cate = categoria.nombre
    else:
        cate = 'General'


    nTipo = int(tipo)
    if nTipo == 1:
        tipo = 'Historico'
    elif nTipo == 2:
        tipo = 'Actual'
    else:
        tipo = 'Actual vs Historico'

    objTweet = Tweet.objects.all()
    tweetTema = objTweet.filter(tema=nombreTema, categoría=cate, busqueda=tipo)
    tweetPos = tweetTema.filter(polaridad='Positivo').count()
    tweetNeg = tweetTema.filter(polaridad='Negativo').count()
    tweetNeu = tweetTema.filter(polaridad='Neutro').count()

    context = {
        'tema':nombreTema,
        'categorias':categorias,
        'tipo':tipo,
        'nTipo':nTipo,

        #Grafica
        'titulo':cate,
        'labels': ['Negativo', 'Positivo', 'Neutro'],
        'data': [tweetPos, tweetNeg, tweetNeu],
        'colors': ["#FF4136", "#0074D9", "#A2EEC6"]
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

