# CLASE PARA LOS FORMULARIOS
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from herramienta.models import Tema, Categoria

#####################
#   Formulario Temas
#####################
class TemaForm(forms.ModelForm):
    class Meta:
        model=Tema
        fields = ['nombre', 'palabras_clave', 'categorias']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.helper = FormHelper() #Lo que lleva el formulario
        self.helper.form_id = "tema-form" #el id
        self.helper.form_class = "blue" #clase para el css
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit-name','Enviar'))

##########################
#   Formulario Historico
##########################

class HistoricoForm(forms.Form):
    numeroTweets = forms.IntegerField(label="Número de tweets a recolectar",widget=forms.TextInput( attrs= {
                    'placeholder':"Numero de tweets: 1, 2, 3 ...",
                }))
    fechaInicio = forms.DateField(label="Introduzca la fecha de inicio",initial=datetime.date.today)
    fechaFin = forms.DateField(label="Introduzca la fecha de fin",initial=datetime.date.today)
    CHOICES = (('TextBlob', 'TextBlob'),
               ('MeaningCloud', 'MeaningCloud'),)
    maquinaAnalisis = forms.ChoiceField(label="¿Qué máquina de análisis usar?",choices=CHOICES, help_text="Utilice MeaningCloud solo para una recolección de tweets inferior a 10.000 debido a la restricción de la API")


########################
#   Formulario Actual
########################
class ActualForm(forms.Form):
    numeroTweets = forms.IntegerField(label="Número de tweets a recolectar",widget=forms.TextInput( attrs= {
                    'placeholder':"Numero de tweets: 1, 2, 3 ...",
                }))
    fechaFin = forms.DateField(label="Introduzca la fecha",initial=datetime.date.today)
    CHOICES = (('TextBlob', 'TextBlob'),)
    maquinaAnalisis = forms.ChoiceField(label="La máquina de análisis disponible",choices=CHOICES)
