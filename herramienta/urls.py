from django.conf.urls import url

from herramienta.views import TemaListView, TemaDetailView, sobreMi_view, inicio_view, TemaUpdateView, TemaCreateView, \
    categoriaDetail_View, temaGrGeneral_View, temaGraficas_View, saveBusqHist_View, saveBusqAct_View, \
    confiBusqueda_View, tareas_view, tweetCate_View, csvdownload_View, csvdownall_View

urlpatterns = [

    url(r'^$', inicio_view, name='inicio-view'),
    url(r'^inicio/$', inicio_view, name='inicio-view'),
    url(r'^sobreMi/$', sobreMi_view, name='sobreMi-view'),

    url(r'^tareas/$', tareas_view, name='tareas-view'),


    url(r'^analizador/$', TemaListView.as_view(), name='tema-list-view'),

    url(r'^analizador/tema/(?P<pk>\d+)$', TemaDetailView.as_view(), name='tema-detalle-view'),
    url(r'^analizador/createTema/$', TemaCreateView.as_view(), name='tema-create-view'),
    url(r'^analizador/tema/edit/(?P<pk>\d+)$', TemaUpdateView.as_view(), name='tema-edit-view'),
    url(r'^analizador/tema/(?P<pk>\d+)/estadistica/(?P<tipo>\d+)/General$', temaGrGeneral_View, name='tema-grGeneral-view'),

    url(r'^analizador/tema/(?P<pk>\d+)/estadistica/(?P<tipo>\d+)/(?P<cate>[a-zA-Z\ ]+)$', temaGraficas_View,name='tema-graficas-view'),

    url(r'^analizador/tema/tweets/descarga$', csvdownall_View ,name='csv-all-view'),
    url(r'^analizador/tema/(?P<pk>\d+)/tweets/(?P<tipo>\d+)/(?P<cate>[a-zA-Z\ ]+)/descarga$', csvdownload_View ,name='csv-view'),
    url(r'^analizador/tema/(?P<pk>\d+)/tweets/(?P<tipo>\d+)/(?P<cate>[a-zA-Z\ ]+)$', tweetCate_View ,name='tweets-view'),



    url(r'^analizador/tema/(?P<pk>\d+)/(?P<nombre>[a-zA-Z/ ]+)$', categoriaDetail_View, name='categoria-detalle-view'),

    #Guardar Busqueda
    url(r'^analizador/tema/(?P<pk>\d+)/(?P<nombre>[a-zA-Z/ ]+)/(?P<tipo>[0-9]+)/(?P<numTw>[0-9]+)/(?P<fechaInic>[0-9\-\ \:]+)/(?P<fechaFin>[0-9\-\ \:]+)/(?P<maquina>[a-zA-Z]+)$', saveBusqHist_View, name='save-busq-hist-view'),
    #Configuración actual
    url(r'^analizador/tema/(?P<pk>\d+)/(?P<nombre>[a-zA-Z/ ]+)/(?P<tipo>[0-9]+)/(?P<fechaFin>[0-9\-\ \:]+)$', saveBusqAct_View, name='save-busq-act-view'),

    url(r'^analizador/tema/(?P<pk>\d+)/(?P<nombre>[a-zA-Z/ ]+)/(?P<tipo>[0-9]+)$', confiBusqueda_View, name='confi-busqueda-view'),



]