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
    print('Termina el proceso')

#########################
#   Uso de Streaming    #
#########################
@background(schedule=5)
def actual(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC , fechaFin):
    fechaHoy = datetime.date.today()
    fechaHoy = fechaHoy.strftime("%Y-%m-%d")
    vuelta = 1
    print('entro a buscar ',format(nombreTema))
    print('con la categoria ',format(nombreCate))
    print(vuelta)
    while fechaHoy <= fechaFin:
        stream(nombreTema, palabrasClaveT, nombreCate, palabrasClaveC)
        vuelta += 1
        print(vuelta)
        fechaHoy = datetime.date.today()
        fechaHoy = fechaHoy.strftime("%Y-%m-%d")
    print('Termina el proceso')


