# Herramienta para el análisis temático en Twitter.



Esta es una herramienta desarrollada en el Trabajo de Fin de Grado del alumno Francisco Jesús Gámez Ruiz perteneciente al Grado Ingeniería Informática de especialidad de Sistemas de la Información de la Universidad de Málaga.
Esta herramienta permite la recopilación de tuits basados en temáticas. El usuario puede crear una temática y seleccionar una categoría dentro de ella y la aplicación recopilar los tuits referentes a ellos en base a lo que el usuario le pide. Una vez hecho esto, los tuits serán analizados y caracterizados por su polaridad para, así, informar al usuario la opinión general que se tiene en el mundo.
## Instalación

Windows 10: Requiere de instalación previa de Python.

1. Instale MongoDB

```sh
https://www.mongodb.com/download-center/community
```

2. Cree la base de datos

```sh
Nombre de la base de datos analizadorTematicoDB
```

3. Descargue el proyecto

```sh
git clone https://github.com/FranGamezRuiz/analizadorTematico
```
4. Instale las dependencias

```sh
pip install -r requirements.txt --user
```

## Para ejecutarlo

1. Abra el terminal y ejecute

```sh
mongod
```

2. Ejecute en un terminal desde la dirección del proyecto.

```sh
python manage.py runserver
```

3. Ejecute en un terminal desde la dirección del proyecto para las tareas en segundo plano.

```sh
python manage.py process_tasks
```


