from background_task import background
from herramienta.utilsTwitter import stream, cursorHist, searchHist
import datetime
###############################################
#   Tareas que se realizan en segundo plano   #
###############################################



#########################
#     Uso de Cursor     #
#########################
@background(schedule=5)
def historico(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina , fechaInic, fechaFin):
    numTw = int(numTw)
    if numTw <= 1000:
        cursorHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaInic, fechaFin)
    else:
        searchHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaInic, fechaFin)

#########################
#   Uso de Streaming    #
#########################
#quitar maquina y numTw
@background(schedule=5)
def actual(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , numTw, maquina, fechaFin):
    fechaHoy = datetime.date.today()
    fechaHoy = fechaHoy.strftime("%Y-%m-%d")
    while fechaHoy <= fechaFin:
        stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC)
        fechaHoy = datetime.date.today()
        fechaHoy = fechaHoy.strftime("%Y-%m-%d")


