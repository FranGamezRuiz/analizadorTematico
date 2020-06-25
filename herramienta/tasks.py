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
        print('Tarea cursor')
        cursorHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaInic, fechaFin)
    else:
        print('Tarea search')
        searchHist(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, numTw, maquina, fechaInic, fechaFin)
    print('Termina el proceso')

#########################
#   Uso de Streaming    #
#########################
@background(schedule=5)
def actual(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , fechaFin):
    print('Entro a buscar ',format(nombreTema))
    print('Con la categoria ',format(nombreCate))
    print('Fecha Fin ',format(fechaFin))
    stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC, fechaFin)
    print('Termina el proceso')


