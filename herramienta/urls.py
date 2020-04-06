from django.conf.urls import url

from herramienta.views import first_view

urlpatterns = [
    url(r'^$', first_view, name='first_view'),

]