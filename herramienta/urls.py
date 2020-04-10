from django.conf.urls import url

from herramienta.views import TemaListView, TemaDetailView, sobreMi_view, inicio_view, TemaUpdateView, TemaCreateView, categoriaDetail_View

urlpatterns = [

    url(r'^$', inicio_view, name='inicio-view'),
    url(r'^inicio/$', inicio_view, name='inicio-view'),
    url(r'^sobreMi/$', sobreMi_view, name='sobreMi-view'),

    url(r'^analizador/$', TemaListView.as_view(), name='tema-list-view'),

    url(r'^analizador/tema/(?P<pk>\d+)$', TemaDetailView.as_view(), name='tema-detalle-view'),
    url(r'^analizador/createTema/$', TemaCreateView.as_view(), name='tema-create-view'),
    url(r'^analizador/tema/edit/(?P<pk>\d+)$', TemaUpdateView.as_view(), name='tema-edit-view'),

    url(r'^analizador/tema/(?P<pk>\d+)/(?P<nombre>[a-zA-Z/ ]+)$', categoriaDetail_View, name='categoria-detalle-view'),


]