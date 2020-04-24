from django.db import models

from djongo import models #importo los modelos de django

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    palabras_clave = models.CharField('Palabras clave', max_length=100)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Tema(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    palabras_clave = models.CharField('Palabras clave', max_length=100)
    categorias = models.ArrayField(model_container=Categoria,)

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['nombre']

    def getCategorias(self):
        return self.categorias

    def __str__(self):
        return self.nombre

class Tweet(models.Model):
    fecha_creado = models.CharField('Fecha creado', max_length=100)
    id_twitter = models.CharField('id en twitter', max_length=100)
    texto = models.CharField('Texto del tweet', max_length=300)
    truncado = models.BooleanField('¿ es truncado ?', default=False)
    geo = models.CharField('Geolocalización',blank=True, null=True, max_length=300)
    coordenadas = models.CharField('Coordenadas',blank=True, null=True, max_length=300)
    place = models.CharField('Lugar',blank=True, null=True,max_length=300)
    numero_ret = models.IntegerField('Número de retweet', default=0)
    numero_fav = models.IntegerField('Número de favoritos', default=0)
    esFavorito = models.BooleanField('¿ es favorito?', default=False)
    esRetweet = models.BooleanField('¿ es favorito?', default=False)
    idioma = models.CharField('Idioma', max_length=3)
    tema = models.CharField('Tema', max_length=50)
    categoría = models.CharField('Categoria', max_length=50)
    polaridad = models.CharField('Polaridad', max_length=50)
    numero_Polaridad = models.DecimalField('Número de polaridad',max_digits=10, decimal_places=5)
    busqueda = models.CharField('Búsqueda utilizada', max_length=50)
    analisis = models.CharField('Análisis utilizado', max_length=50)

    class Meta:
        verbose_name = "Tweet"
        verbose_name_plural = "Tweets"

    def __str__(self):
        return self.texto