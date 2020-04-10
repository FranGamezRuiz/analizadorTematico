from django.conf.urls import url

from herramienta.views import tema_list_view, tema_detalle_view, sobreMi_view, inicio_view

urlpatterns = [

    url(r'^$', inicio_view, name='inicio-view'),
    url(r'^inicio/$', inicio_view, name='inicio-view'),
    url(r'^sobreMi/$', sobreMi_view, name='sobreMi-view'),
    url(r'^analizador/$', tema_list_view, name='tema-list-view'),
    #url(r'^detalles/(?P<pk>\d+)$', tema_detalle_view, name='tema-detalle-view'),
    url(r'^detalles/(?P<pk>[a-zA-Z/ ]+)$', tema_detalle_view, name='tema-detalle-view'),


]