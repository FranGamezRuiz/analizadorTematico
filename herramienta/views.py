from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from herramienta.forms import TemaForm, ConfiForm
from herramienta.models import Tema


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
def categoriaDetail_View(request, pk, nombre):

    variable = Tema.objects.all()   #Obtengo Todos los temas
    tema = variable.filter(pk=pk) #tengo el tema
    nombreTema = tema.first()
    categorias = tema.first().getCategorias() #tengo las categorias
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

@login_required
def confiBusqueda_View(request, pk, nombre, tipo):

    variable = Tema.objects.all()  # Obtengo Todos los temas
    tema = variable.filter(pk=pk)  # tengo el tema
    nombreTema = tema.first()
    categorias = tema.first().getCategorias()  # tengo las categorias
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
    tipo = int(tipo)
    if tipo == 1:
        tipoN = 'historico'
    else:
        tipoN = 'actual'

    if request.method == 'POST':
        formulario = ConfiForm(request.POST)
        if formulario.is_valid():
            numeroTweets = formulario.cleaned_data['numeroTweets']
            fechaFin = formulario.cleaned_data['fechaFin']
            maquinaAnalisis = formulario.cleaned_data['maquinaAnalisis']

            return redirect('save-busqueda-view', pk=pk, nombre=nombre, tipo=tipo, numTw=numeroTweets, fechaFin=fechaFin,maquina=maquinaAnalisis)

    else:
        formulario = ConfiForm()
    

    context = {
        'tema':nombreTema,
        'categoria':nombreCate,
        'tema.pk':pk,
        'tipo':tipoN,
        'formulario':formulario
    }

    return render(request, 'herramienta/confi_busqueda.html', context)

@login_required()
def saveBusqueda_View(request, pk, nombre, tipo, numTw, fechaFin, maquina):
    variable = Tema.objects.all()  # Obtengo Todos los temas
    tema = variable.filter(pk=pk)  # tengo el tema
    nombreTema = tema.first()
    palabrasClaveT = tema.first().palabras_clave
    categorias = tema.first().getCategorias()  # tengo las categorias
    for categoria in categorias:
        if categoria.nombre == nombre:
            nombreCate = categoria.nombre
            palabrasClaveC = categoria.palabras_clave
    tipo = int(tipo)
    if tipo == 1:
        tipoN = 'historico'
    else:
        tipoN = 'actual'


    context = {
        'tema': nombreTema,
        'palabrasClaveTema':palabrasClaveT,
        'categoria': nombreCate,
        'palabrasClaveCate':palabrasClaveC,
        'tipo': tipoN,
        'numTw':numTw,
        'fecha':fechaFin,
        'maquinaA':maquina

    }

    return render(request, 'herramienta/save_busqueda.html', context)


#########################
# CLASES para las vistas
#########################


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

