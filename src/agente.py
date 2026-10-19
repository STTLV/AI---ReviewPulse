"""Orquestación auditable: percepción -> decisión -> acción y memoria."""
from pathlib import Path
import sqlite3
from src.percepcion import validar_resena,EntradaInvalida
from src.memoria import Memoria
from src.modelo import clasificar
from src.decision import Configuracion,evaluar_alerta
from src.registro import registrar, instante_utc
from src.tiempos import fin_de_semana_iso_utc, evaluar_plazo

class AgenteReviewPulse:
    def __init__(self, carpeta_salida='salida_local', clasificador=None, config=None):
        self.carpeta=Path(carpeta_salida)
        self.memoria=Memoria(self.carpeta/'memoria.sqlite3')
        self.log=self.carpeta/'ejecuciones.jsonl'
        self.clasificador=clasificador or clasificar
        self.config=config or Configuracion()

    def procesar(self, entrada):
        try:
            percepcion=validar_resena(entrada)
        except EntradaInvalida as e:
            resultado={'estado':'rechazada','error':str(e)}
            registrar(self.log,entrada if isinstance(entrada,dict) else {'entrada':str(entrada)},
                     {'estado':'validacion_invalida','motivo':str(e)},{'tipo':'abstenerse','resultado':'solicitar_correccion'})
            return resultado
        if self.memoria.obtener_reporte(percepcion['semana']) is not None:
            registrar(self.log,percepcion,{'estado':'semana_cerrada'}, {'tipo':'no_modificar_historial_cerrado'})
            return {'estado':'semana_cerrada','semana':percepcion['semana']}
        if self.memoria.existe(percepcion['id']):
            registrar(self.log,percepcion,{'estado':'duplicado'}, {'tipo':'no_reprocesar'})
            return {'estado':'duplicada','id':percepcion['id']}
        pred=self.clasificador(percepcion['texto'])
        try:
            self.memoria.guardar_resena(percepcion,pred)
        except sqlite3.IntegrityError:
            return {'estado':'duplicada','id':percepcion['id']}
        accion={'tipo':'guardar_clasificacion','id':percepcion['id'],'semana':percepcion['semana']}
        registrar(self.log,percepcion,pred,accion)
        return {'estado':'aceptada','id':percepcion['id'],'semana':percepcion['semana'], 'clasificacion':pred,'accion':accion}

    def cerrar_semana(self,semana):
        import re
        from datetime import date
        if not isinstance(semana,str) or not re.fullmatch(r'\d{4}-W\d{2}',semana):
            return {'estado':'semana_invalida','error':'Utilice AAAA-W##'}
        try:
            date.fromisocalendar(int(semana[:4]),int(semana[-2:]),1)
        except ValueError:
            return {'estado':'semana_invalida','error':'Semana ISO inexistente'}
        if self.memoria.obtener_reporte(semana) is not None:
            registrar(self.log, {'semana':semana},{'estado':'reporte_existente'}, {'tipo':'no_duplicar_reporte'})
            return {'estado':'ya_cerrada','reporte':self.memoria.obtener_reporte(semana)}
        actual=self.memoria.datos_semana(semana)
        if not actual['total']:
            registrar(self.log, {'semana':semana}, {'estado':'sin_resenas'}, {'tipo':'no_crear_reporte_vacio'})
            return {'estado':'sin_resenas','error':'No hay reseñas en esa semana'}
        historial=self.memoria.semanas_previas(semana,self.config.semanas_de_referencia)
        decision=evaluar_alerta(actual,historial,self.config)
        creado_utc=instante_utc()
        cierre_teorico=fin_de_semana_iso_utc(semana).isoformat()
        plazo_reporte=evaluar_plazo(cierre_teorico,creado_utc)
        reporte={'semana':semana,'resumen':actual,'decision_alerta':decision,
                 'cierre_calendario_utc':cierre_teorico,'generado_utc':creado_utc,
                 'plazo_reporte':plazo_reporte,
                 'notificacion':'registrada_en_panel' if decision['alertar'] else 'no_necesaria',
                 'plazo_notificacion_externa':'NO_IMPLEMENTADO',
                 'fuente':'Datos de prueba o entradas del usuario; no conexión a plataformas externas'}
        self.memoria.guardar_reporte(semana,reporte)
        if decision['alertar']:
            descripcion=f"Anomalía de {', '.join(decision['tipos_anomalia'])} en {semana}; negativas: {actual['proporcion_negativa']:.1%}; volumen: {actual['total']}"
            self.memoria.guardar_alerta(semana,descripcion)
        registrar(self.log,{'semana':semana,'resumen':actual,'historial':historial},decision,
                 {'tipo':'guardar_reporte_y_alerta_en_panel' if decision['alertar'] else 'guardar_reporte',
                  'medio':'base_de_datos_local','envio_externo':False})
        return {'estado':'cerrada','reporte':reporte}
