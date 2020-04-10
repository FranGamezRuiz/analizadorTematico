from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from herramienta.forms import TemaForm
from herramienta.models import Tema, Categoria


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
            palabrasCate = categoria.palabras_clave


    context = {
        'tema':nombreTema,
        'categoria':nombre,
        'palabras':palabrasCate
    }

    return render(request, 'herramienta/categoria_detail.html', context)


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

