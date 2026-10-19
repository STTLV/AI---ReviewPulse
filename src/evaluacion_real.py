"""Evaluacion de seguimiento del modelo real con Trip-MAML ES/test.

Test fue examinado en Fase 1: NO es una prueba final ciega ni una etiqueta
humana de sentimiento global. Etiquetas agregadas por aspecto con una regla.
"""
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
import csv
import json
import re
import zipfile

from src.agente import AgenteReviewPulse
from src.modelo import clasificar, NOMBRES_TEMAS

RUTA_ES_TEST = 'trip-maml-main/ES/spanish_test.json'
TEMAS = {'CLEANLINESS':'limpieza', 'SERVICE':'servicio', 'LOCATION':'ubicacion', 'VALUE':'precio_valor'}


def recuperar_texto(segmento):
    if not isinstance(segmento, str):
        raise ValueError('Segmento no textual')
    palabras=[]
    for token in segmento.split():
        palabra=token.split('//',1)[0] if '//' in token else token.split('/',1)[0]
        if not palabra and token.startswith('////'):
            palabra='/'
        if palabra:
            palabras.append(palabra.replace('_',' '))
    texto=' '.join(palabras)
    texto=re.sub(r'\s+([.,;:!?%)\]}])',r'\1',texto)
    texto=re.sub(r'([([{¿¡])\s+',r'\1',texto)
    return re.sub(r'\s+',' ',texto).strip()


def agregar_sentimiento(conteos):
    presentes={pol for pol,n in conteos.items() if n>0}
    if presentes=={'p'}: return 'positivo'
    if presentes=={'n'}: return 'negativo'
    return 'neutro_o_mixto' if presentes else ''


def convertir(registro):
    segmentos=registro.get('segments')
    labels=registro.get('segmentLabels')
    if not isinstance(segmentos,list) or not isinstance(labels,list) or len(segmentos)!=len(labels):
        raise ValueError('Anotaciones y segmentos no alineados')
    cont=defaultdict(Counter)
    for etiqueta in labels:
        if not isinstance(etiqueta,dict): raise ValueError('Etiqueta no es diccionario')
        for tema,pol in etiqueta.items():
            if tema in TEMAS:
                if pol not in ('p','n','x'): raise ValueError('Polaridad desconocida')
                cont[TEMAS[tema]][pol]+=1
    verdad={t:agregar_sentimiento(cont[t]) for t in NOMBRES_TEMAS if cont[t]}
    texto=' '.join(recuperar_texto(s) for s in segmentos).strip()
    return {'id':str(registro['reviewId']),'texto':texto,'referencia_por_tema':verdad}


def leer_test(archivo_zip):
    archivo_zip=Path(archivo_zip)
    if not archivo_zip.exists(): raise FileNotFoundError(archivo_zip)
    with zipfile.ZipFile(archivo_zip) as z:
        if RUTA_ES_TEST not in z.namelist(): raise ValueError('No se encontro ES/spanish_test.json')
        with z.open(RUTA_ES_TEST) as f:
            filas=[convertir(json.loads(line)) for line in f if line.strip()]
    if not filas: raise ValueError('El conjunto de test está vacío')
    if len({r['id'] for r in filas})!=len(filas): raise ValueError('IDs de reseñas duplicados')
    return filas


def evaluar(filas, clasificador=clasificar):
    predicciones=[]
    temas=list(NOMBRES_TEMAS)
    acierto_tema=acierto_total=0
    por_tema={t:{'tp':0,'fp':0,'fn':0,'tn':0,'real_presentes':0,'polaridad_correcta_con_tema_real':0} for t in temas}
    totalsent=correctsent=0
    for r in filas:
        p=clasificador(r['texto'])
        pr=p['sentimiento_por_tema']; ref=r['referencia_por_tema']
        conjuntos_iguales=set(pr)==set(ref)
        conjunto_correcto=(pr==ref)
        acierto_tema+=int(conjuntos_iguales)
        acierto_total+=int(conjunto_correcto)
        for t in temas:
            es_real=t in ref; es_pred=t in pr
            k='tp' if es_real and es_pred else 'fn' if es_real else 'fp' if es_pred else 'tn'
            por_tema[t][k]+=1
            if es_real:
                por_tema[t]['real_presentes']+=1
                totalsent+=1
                if pr.get(t)==ref[t]:
                    correctsent+=1
                    por_tema[t]['polaridad_correcta_con_tema_real']+=1
        predicciones.append({'review_id':r['id'],
            'referencia_por_tema_json':json.dumps(ref,sort_keys=True,ensure_ascii=False),
            'prediccion_por_tema_json':json.dumps(pr,sort_keys=True,ensure_ascii=False),
            'temas_exactos':int(conjuntos_iguales),
            'temas_y_sentimientos_exactos':int(conjunto_correcto),
            'referencia_senal_negativa':int(any(v=='negativo' for v in ref.values())),
            'prediccion_senal_negativa':int(p['tiene_senal_negativa'])})
    for t, val in por_tema.items():
        tp,fp,fn=val['tp'],val['fp'],val['fn']
        val['precision_tema']=tp/(tp+fp) if tp+fp else None
        val['recall_tema']=tp/(tp+fn) if tp+fn else None
        val['f1_tema']=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0
    n=len(filas)
    return {'fuente': 'Trip-MAML / ES/spanish_test.json','cantidad_resenas':n,
        'exactitud_temas_conjunto':acierto_tema/n,
        'exactitud_estricta_temas_y_sentimientos':acierto_total/n,
        'aciertos_estrictos':acierto_total,
        'acierto_polaridad_para_aspectos_reales':correctsent/totalsent if totalsent else None,
        'aspectos_reales_evaluados':totalsent,
        'f1_macro_temas':sum(v['f1_tema'] for v in por_tema.values())/len(temas),
        'por_tema':por_tema,
        'cumple_85_estricto':acierto_total/n>=0.85,
        'advertencias':[
            'Evaluación de seguimiento: conjunto test ya examinado en experimentos de Fase 1. No es prueba final ciega.',
            'Etiqueta de sentimiento por tema DERIVADA de anotaciones por segmento; no es etiqueta global humana.',
            'x equivale a neutro/mixto; no exclusivamente neutro.',
            'La exactitud estricta exige coincidencia de todos los temas y sentimientos de la reseña.',
            'Las fechas originales de publicación no están disponibles: no evalúa anomalías temporales reales.',
            'No demuestra las otras tres medidas SMART ni la entrega a gerencia.'
        ]}, predicciones


def integrar(filas, ruta):
    """Replay de software sin oracle NLP: fechas y semanas son SINTÉTICAS.

    Etiquetas de anomalía real desconocidas para estas semanas sintéticas.
    NO se calculan FP/TP de alertas ni exactitud de detección real.
    """
    ag=AgenteReviewPulse(ruta)  # clasificador REAL src.modelo.clasificar
    semanas=[37,38,39,40]
    eventos=[]
    conteo_estados=Counter()
    for i,r in enumerate(filas):
        semana=semanas[i*len(semanas)//len(filas)]
        fecha=date.fromisocalendar(2026,semana,1)+timedelta(days=i%7)
        resultado=ag.procesar({'id':'TRIP-TEST-'+r['id'],'texto':r['texto'],
                              'fecha':fecha.isoformat(),'plataforma':'archivo','estrellas':None})
        conteo_estados[resultado['estado']]+=1
        eventos.append({'id':r['id'],'semana_sintetica':f'2026-W{semana:02d}',
                        'fecha_sintetica':fecha.isoformat(),'estado':resultado['estado'],
                        'tipo_accion':resultado.get('accion',{}).get('tipo','')})
    cierres=[]
    for semana in semanas:
        resp=ag.cerrar_semana(f'2026-W{semana:02d}')
        cierres.append({'semana':f'2026-W{semana:02d}','estado':resp['estado'],
            'alerta':resp.get('reporte',{}).get('decision_alerta',{}).get('alertar'),
            'razon':resp.get('reporte',{}).get('decision_alerta',{}).get('razon','')})
    return {'origen_textos':'Reseñas reales del corpus anotado de prueba',
        'fechas_y_distribucion':'SIMULADAS para verificar flujo, NO reflejan la llegada real',
        'conteo_estados':dict(conteo_estados),'reseñas_guardadas':ag.memoria.conteo(),
        'reportes_guardados':len(ag.memoria.lista_reportes()),
        'alertas_guardadas':len(ag.memoria.lista_alertas()),
        'cierres':cierres,'fp_fn_alertas':'NO_EVALUABLES: sin verdad temporal de anomalía',
        'plazos_24h':'NO_EVALUABLES: no hay fechas reales de llegada y entrega externa'},eventos


def guardar_csv(ruta,filas):
    with Path(ruta).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(filas[0]));writer.writeheader();writer.writerows(filas)


def ejecutar(zip_path,salida, integracion=True):
    salida=Path(salida);salida.mkdir(parents=True,exist_ok=True)
    filas=leer_test(zip_path)
    metricas,pred=evaluar(filas)
    guardar_csv(salida/'predicciones_test_reseñas.csv',pred)
    resumen={'modelo_real':metricas}
    if integracion:
        sim,eventos=integrar(filas,salida/'replay_aislado')
        resumen['replay_integracion']=sim
        guardar_csv(salida/'traza_integracion.csv',eventos)
    (salida/'informe_evaluacion.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2),encoding='utf-8')
    return resumen
