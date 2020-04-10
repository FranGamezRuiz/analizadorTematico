# CLASE PARA LOS FORMULARIOS
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from herramienta.models import Tema, Categoria


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
