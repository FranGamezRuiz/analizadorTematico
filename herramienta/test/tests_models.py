from django.test import TestCase

from herramienta.models import Tema, Categoria, Tweet

class herramienta_test_class(TestCase):

    @classmethod
    def setUpTestData(cls):
        categoria = Categoria.objects.create(nombre="Jazztel", palabras_clave="jazztel")
        categoria1 = Categoria.objects.create(nombre="Movistar", palabras_clave="movistar")
        Tema.objects.create(nombre="ADSL", palabras_clave="adsl", categorias=[categoria, categoria1])
        Tema.objects.create(nombre="Fibra", palabras_clave="Fibra optica", categorias=[categoria, categoria1])
        Tweet.objects.create(fecha_creado="2020-06-01", id_twitter="000000000001",texto="Prueba",truncado=False,geo=None,coordenadas=None,place=None,numero_ret=0,numero_fav=0,esFavorito=False,esRetweet=False,idioma="es",tema="ADSL",categoría="Jazztel",polaridad="Positivo",numero_Polaridad=1,busqueda="Actual",analisis="TextBlob")
        Tweet.objects.create(fecha_creado="2020-06-01", id_twitter="000000000002",texto="Prueba 2",truncado=False,geo=None,coordenadas=None,place=None,numero_ret=0,numero_fav=0,esFavorito=False,esRetweet=False,idioma="es",tema="ADSL",categoría="Jazztel",polaridad="Negativo",numero_Polaridad=-1,busqueda="Actual",analisis="TextBlob")

    def test_categoria_in_tema(self):
        nombre_categoria = Categoria.objects.get(pk=1).nombre
        categorias_tema = Tema.objects.get(pk=1).categorias
        categorias_nombre = []
        for categoria in categorias_tema:
            categorias_nombre += [categoria.nombre]
        self.assertTrue(nombre_categoria in categorias_nombre)


    def test_tweets_in_tema(self):
        nombre_tema = Tema.objects.get(pk=1).nombre
        tweets = Tweet.objects.filter(tema=nombre_tema)
        cont = tweets.count()
        self.assertEqual(cont, 2)

    def test_tweets_notin_tema(self):
        nombre_tema = Tema.objects.get(pk=2).nombre
        tweets = Tweet.objects.filter(tema=nombre_tema)
        cont = tweets.count()
        self.assertEqual(cont, 0)
