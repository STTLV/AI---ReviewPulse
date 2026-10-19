"""Pruebas estocásticas de la POLÍTICA del agente, separadas de la calidad del NLP.

Genera percepciones con una verdad de simulación conocida y aleatoriedad reproducible.
El clasificador inyectado lee señales sintéticas codificadas; NO es el modelo Trip-MAML.
La API del agente, la memoria SQLite y el motor de decisiones sí son los reales.
"""
from __future__ import annotations

import csv
import json
import random
import statistics
import tempfile
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from collections import Counter

from src.agente import AgenteReviewPulse
from src.registro import instante_utc


@dataclass(frozen=True)
class Escenario:
    id: str
    nombre: str
    tipo: str
    n_actual: int
    prob_negativa: float
    n_historico: int = 16
    prob_historica: float = 0.10
    semanas_historicas: int = 3
    anomalia_real: bool | None = False
    evaluable_alertas: bool = True
    modo: str = 'normal'
    nota: str = ''


ESCENARIOS = (
    Escenario('E01','Comportamiento habitual','normal',24,0.10),
    Escenario('E02','Aumento marcado de negatividad','anomalia',24,0.72,anomalia_real=True),
    Escenario('E03','Aumento moderado de negatividad','anomalia',24,0.55,anomalia_real=True),
    Escenario('E04','Fluctuación pequeña','limite',24,0.20),
    Escenario('E05','Aumento de volumen solamente','limite',64,0.10,n_historico=12,anomalia_real=True,
              nota='Prueba dirigida al nuevo detector independiente de volumen (revisión de la brecha Paso 3).'),
    Escenario('E06','Sin comentarios negativos','normal',24,0.00),
    Escenario('E07','Muy pocas reseñas','limite',4,0.90,anomalia_real=None,evaluable_alertas=False,
              nota='La regla se abstiene de alertar con menos de cinco reseñas.'),
    Escenario('E08','Histórico insuficiente','limite',24,0.75,semanas_historicas=1,
              anomalia_real=None,evaluable_alertas=False,
              nota='Solo existe una semana histórica: no hay base suficiente para decidir.'),
    Escenario('E09','Texto vacío','fallo_esperado',0,0.0,anomalia_real=None,evaluable_alertas=False,modo='texto_vacio'),
    Escenario('E10','Fecha imposible','fallo_esperado',0,0.0,anomalia_real=None,evaluable_alertas=False,modo='fecha_invalida'),
    Escenario('E11','ID repetido','fallo_esperado',0,0.0,anomalia_real=None,evaluable_alertas=False,modo='duplicado'),
    Escenario('E12','Sensor sin fecha','fallo_esperado',0,0.0,anomalia_real=None,evaluable_alertas=False,modo='fecha_ausente'),
)


def clasificador_controlado(texto):
    """Oráculo de señales simuladas para aislar la lógica de decisión.

    ATENCIÓN: no predice el sentimiento del español natural.
    """
    negativa = texto.startswith('[NEGATIVA_SIMULADA]')
    pol = 'negativo' if negativa else 'positivo'
    return {'temas_detectados':['servicio'], 'sentimiento_por_tema':{'servicio':pol},
            'tema_principal':'servicio', 'polaridad_resumen':pol,
            'tiene_senal_negativa':negativa, 'estado':'un_tema'}


def _entrada(identificador, fecha, negativa):
    marcador = '[NEGATIVA_SIMULADA]' if negativa else '[POSITIVA_SIMULADA]'
    return {'id':identificador, 'texto':f'{marcador} Reseña ficticia de servicio',
            'fecha':fecha.isoformat() if isinstance(fecha,date) else fecha,
            'plataforma':'simulador','estrellas':2 if negativa else 5}


def _cargar_semana(agente, escenario, rng, codigo, semana, n, prob):
    lunes=date.fromisocalendar(2026,semana,1)
    neg=0
    for i in range(n):
        es_neg=rng.random()<prob
        neg+=int(es_neg)
        fecha=lunes+timedelta(days=rng.randrange(7))
        r=agente.procesar(_entrada(f'{codigo}-{semana}-{i:03d}',fecha,es_neg))
        if r['estado']!='aceptada':
            raise RuntimeError(f'Fallo inesperado en la simulación: {r}')
    resultado=agente.cerrar_semana(f'2026-W{semana:02d}')
    if resultado['estado']!='cerrada':
        raise RuntimeError(f'No pudo cerrar semana {semana}: {resultado}')
    return neg, resultado


def ejecutar_escenario(escenario:Escenario, repeticion:int, semilla:int):
    """Devuelve fila numérica, más logs; nunca mezcla instancias ni modifica salida_app."""
    rng=random.Random(semilla)
    inicio=instante_utc()
    with tempfile.TemporaryDirectory(prefix='reviewpulse_caso_') as carpeta:
        agente=AgenteReviewPulse(carpeta,clasificador=clasificador_controlado)
        for semana in (37,38,39)[:escenario.semanas_historicas]:
            _cargar_semana(agente,escenario,rng,f'{escenario.id}-R{repeticion}',semana,
                          escenario.n_historico,escenario.prob_historica)
        rechazadas=duplicadas=0
        alertas_emitidas=0
        total_actual=0
        propor_negativa=None
        if escenario.modo=='normal':
            cantidad_neg,resultado=_cargar_semana(agente,escenario,rng,f'{escenario.id}-R{repeticion}',40,
                                               escenario.n_actual,escenario.prob_negativa)
            total_actual=escenario.n_actual
            propor_negativa=cantidad_neg/total_actual if total_actual else None
            alertas_emitidas=int(resultado['reporte']['decision_alerta']['alertar'])
        else:
            valido=_entrada(f'{escenario.id}-R{repeticion}-A',date(2026,9,28),False)
            if escenario.modo=='texto_vacio':
                valido['texto']='  '
                rechazadas=int(agente.procesar(valido)['estado']=='rechazada')
            elif escenario.modo=='fecha_invalida':
                valido['fecha']='2026-99-99'
                rechazadas=int(agente.procesar(valido)['estado']=='rechazada')
            elif escenario.modo=='fecha_ausente':
                valido.pop('fecha')
                rechazadas=int(agente.procesar(valido)['estado']=='rechazada')
            elif escenario.modo=='duplicado':
                primero=agente.procesar(valido)
                segundo=agente.procesar(valido)
                if primero['estado']!='aceptada':
                    raise RuntimeError('No fue posible crear el registro base del caso duplicado')
                duplicadas=int(segundo['estado']=='duplicada')
                total_actual=1
            else:
                raise ValueError('Modo no previsto')
        log_path=Path(carpeta)/'ejecuciones.jsonl'
        registros=[json.loads(x) for x in log_path.read_text(encoding='utf-8').splitlines()] if log_path.exists() else []
        acciones_consistentes = ((escenario.modo=='normal') or
                                (escenario.modo=='duplicado' and duplicadas==1) or
                                (escenario.modo not in ('normal','duplicado') and rechazadas==1))
        fila={
            'id_escenario':escenario.id,'escenario':escenario.nombre,
            'tipo':escenario.tipo,'repeticion':repeticion,'semilla':semilla,
            'prob_negativa_generacion':escenario.prob_negativa,
            'numero_resenas_actual':total_actual,'proporcion_negativa_observada':propor_negativa,
            'anomalia_real':escenario.anomalia_real,'evaluable_alertas':escenario.evaluable_alertas,
            'alertas_emitidas':alertas_emitidas,'rechazos':rechazadas,'duplicados':duplicadas,
            'respuesta_controlada_correcta':acciones_consistentes,
            'registros_log':len(registros),'inicio_utc':inicio,'fin_utc':instante_utc(),
            'clasificador':'oraculo_simulado_NO_modelo_NLP',
            'nota':escenario.nota}
        for item in registros:
            item['escenario']=escenario.id
            item['repeticion']=repeticion
            item['semilla']=semilla
        return fila, registros


def calcular_metricas(filas):
    evaluables=[f for f in filas if f['evaluable_alertas'] and f['anomalia_real'] is not None]
    tp=sum(bool(f['alertas_emitidas']) and f['anomalia_real'] for f in evaluables)
    fp=sum(bool(f['alertas_emitidas']) and not f['anomalia_real'] for f in evaluables)
    fn=sum(not bool(f['alertas_emitidas']) and f['anomalia_real'] for f in evaluables)
    tn=sum(not bool(f['alertas_emitidas']) and not f['anomalia_real'] for f in evaluables)
    alertas=tp+fp
    return {
       'ejecuciones_totales':len(filas), 'escenarios':len(set(f['id_escenario'] for f in filas)),
       'repeticiones_por_escenario':min(Counter(f['id_escenario'] for f in filas).values()),
       'escenarios_falla_esperada':sum(1 for f in filas if f['tipo']=='fallo_esperado')//min(Counter(f['id_escenario'] for f in filas).values()),
       'ejecuciones_evaluables_alerta':len(evaluables),
       'tp':int(tp),'fp':int(fp),'fn':int(fn),'tn':int(tn),
       'proporcion_alertas_falsas':fp/alertas if alertas else None,
       'tasa_falsos_positivos_clasica':fp/(fp+tn) if fp+tn else None,
       'recall_anomalias':tp/(tp+fn) if tp+fn else None,
       'respuesta_controlada_correcta':sum(f['respuesta_controlada_correcta'] for f in filas),
       'evaluacion_exactitud_NLP':'NO_REALIZADA',
       'evaluacion_plazo_24h':'NO_REALIZADA',
       'lectura':'Prueba la lógica de alertas con percepciones simuladas y oráculo controlado; NO el modelo NLP.'
    }


def resumen_por_escenario(filas):
    salida=[]
    for esc in ESCENARIOS:
        grupo=[f for f in filas if f['id_escenario']==esc.id]
        proporciones=[f['proporcion_negativa_observada'] for f in grupo if f['proporcion_negativa_observada'] is not None]
        numero=[f['alertas_emitidas'] for f in grupo]
        salida.append({'id_escenario':esc.id,'escenario':esc.nombre,'tipo':esc.tipo,
            'casos_ejecutados':len(grupo),'alertas_media':statistics.mean(numero),
            'alertas_desv_estandar':statistics.stdev(numero) if len(numero)>1 else 0.0,
            'proporcion_negativa_media':statistics.mean(proporciones) if proporciones else None,
            'proporcion_negativa_desv_estandar':statistics.stdev(proporciones) if len(proporciones)>1 else None,
            'anomalia_real':esc.anomalia_real,'evaluable_alertas':esc.evaluable_alertas,'nota':esc.nota})
    return salida


def _csv(path, filas):
    if not filas: return
    with Path(path).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)


def ejecutar_bateria(salida, repeticiones=5, semilla_base=20261018):
    if repeticiones<5: raise ValueError('Mínimo cinco repeticiones por escenario estocástico')
    if not isinstance(semilla_base,int): raise ValueError('La semilla debe ser entera')
    salida=Path(salida)
    salida.mkdir(parents=True,exist_ok=True)
    filas=[]
    with (salida/'logs_escenarios.jsonl').open('w',encoding='utf-8') as log:
        for idx,esc in enumerate(ESCENARIOS):
            for rep in range(1,repeticiones+1):
                semilla=semilla_base+idx*1000+rep
                fila,registros=ejecutar_escenario(esc,rep,semilla)
                filas.append(fila)
                for r in registros:
                    log.write(json.dumps(r,ensure_ascii=False,default=str)+'\n')
    resumen=resumen_por_escenario(filas)
    metricas=calcular_metricas(filas)
    _csv(salida/'resultados_ejecuciones.csv',filas)
    _csv(salida/'resumen_por_escenario.csv',resumen)
    (salida/'metricas_politica.json').write_text(json.dumps(metricas,ensure_ascii=False,indent=2),encoding='utf-8')
    (salida/'escenarios_configuracion.json').write_text(json.dumps([asdict(e) for e in ESCENARIOS],ensure_ascii=False,indent=2),encoding='utf-8')
    return {'filas':filas,'resumen':resumen,'metricas':metricas,'directorio':str(salida.resolve())}
