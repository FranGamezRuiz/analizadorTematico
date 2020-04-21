from background_task import background
###############################################
#   Tareas que se realizan en segundo plano
###############################################


###############
# Prueba back
###############
from background_task.models import Task

@background(schedule=5)
def hello(nombreTema, palabrasClaveT, nombreCate,palabrasClaveC,tipoN, numTw, maquina,fechaFin):

    object = Task.objects.all().count()
    print(object)
    print(nombreTema)
    print(palabrasClaveT)
    print(nombreCate)
    print(palabrasClaveC)
    print(tipoN)
    print(numTw)
    print(fechaFin)
    print(maquina)

@background(schedule=5)
def historico(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina , fechaInic, fechaFin):
    pass

@background(schedule=5)
def actual(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina, fechaFin):
    pass
