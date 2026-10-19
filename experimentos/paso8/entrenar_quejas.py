"""Experimento del Paso 8: detección de críticas negativas con SOLO ES/spanish_training.json.

Nota: se trata de la presencia de al menos una anotación negativa n en un aspecto
objetivo, NO de la polaridad global de la reseña. No mide el SMART de 85 %.
No lee spanish_test.json, tampoco cambia src/modelo.py ni la app.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sys
import zipfile

import numpy as np
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
from src.evaluacion_real import recuperar_texto

RUTA_ENTRENAMIENTO = 'trip-maml-main/ES/spanish_training.json'
TEMAS_OBJETIVO = frozenset(('CLEANLINESS', 'SERVICE', 'LOCATION', 'VALUE'))
VERSION = 'paso8.1-entrenamiento-only'


def etiqueta_critica(labels):
    """Cuenta una queja si existe al menos un aspecto objetivo con polaridad n."""
    return int(any(k in TEMAS_OBJETIVO and v == 'n' for k, v in labels.items()))


def cargar_entrenamiento(archivo_zip):
    archivo_zip = Path(archivo_zip)
    with zipfile.ZipFile(archivo_zip) as z:
        if RUTA_ENTRENAMIENTO not in z.namelist():
            raise ValueError('No se encontró spanish_training.json en el ZIP')
        records = [json.loads(line) for line in z.open(RUTA_ENTRENAMIENTO) if line.strip()]
    resultado=[]
    ids=set()
    for registro in records:
        sid=str(registro['reviewId'])
        if sid in ids:
            raise ValueError('ID de reseña repetido')
        ids.add(sid)
        segmentos=registro['segments']; anotaciones=registro['segmentLabels']
        if len(segmentos)!=len(anotaciones):
            raise ValueError('Desalineación entre segmentos y anotaciones')
        textos=[recuperar_texto(s) for s in segmentos]
        ys=[etiqueta_critica(a) for a in anotaciones]
        resultado.append({'id':sid, 'texto':' '.join(textos), 'segmentos':textos,
                          'etiquetas_segmento':ys, 'critica':int(any(ys))})
    return resultado


def grupos_sin_texto_duplicado(reviews):
    """Conecta reseñas que comparten un segmento idéntico suficientemente largo.
    Se aplica ANTES de CV, sin usar etiquetas del conjunto de prueba.
    """
    parent=list(range(len(reviews)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def union(i,j):
        parent[find(i)]=find(j)
    visto={}
    for i,r in enumerate(reviews):
        for s in r['segmentos']:
            t=' '.join(s.lower().split())
            if len(t)<30:
                continue
            if t in visto:
                union(i,visto[t])
            else:
                visto[t]=i
    return [find(i) for i in range(len(reviews))]


def pipeline(candidato):
    if candidato=='resena_palabras':
        vec=TfidfVectorizer(analyzer='word',ngram_range=(1,2),min_df=2,strip_accents='unicode',sublinear_tf=True)
    elif candidato in ('resena_caracteres','segmentos_caracteres'):
        vec=TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=2,sublinear_tf=True,max_features=30000)
    else:
        raise ValueError('Candidato no reconocido')
    return Pipeline([('tfidf',vec),('logreg',LogisticRegression(C=1.0,class_weight='balanced',max_iter=1200,random_state=42))])


def ajustar_y_predecir(train, valid, candidato):
    modelo=pipeline(candidato)
    if candidato.startswith('resena_'):
        modelo.fit([r['texto'] for r in train],[r['critica'] for r in train])
        probs=modelo.predict_proba([r['texto'] for r in valid])[:,1]
        limite=0.5
    else:
        textos=[s for r in train for s in r['segmentos']]
        labels=[y for r in train for y in r['etiquetas_segmento']]
        modelo.fit(textos,labels)
        # OR entre segmentos: el límite se define previamente para reducir falsos positivos.
        # NO se ajusta utilizando los ejemplos de validación o test.
        limite=0.70
        probs=np.array([float(max(modelo.predict_proba(r['segmentos'])[:,1]))
                        if r['segmentos'] else 0.0 for r in valid])
    return probs,(probs>=limite).astype(int), modelo,limite


def calcular_metricas(real,pred):
    cm=confusion_matrix(real,pred,labels=[0,1]); tn,fp,fn,tp=[int(x) for x in cm.ravel()]
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    f2=(5*precision*recall/(4*precision+recall)) if 4*precision+recall else 0.0
    return {'n':len(real),'tp':tp,'fp':fp,'fn':fn,'tn':tn,
            'precision':precision,'recall':recall,'f1':f1,'f2':f2,
            'fraccion_alertas_falsas':fp/(tp+fp) if tp+fp else None,
            'accuracy':accuracy_score(real,pred)}


def guardar_csv(ruta,filas):
    with open(ruta,'w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(filas[0]));writer.writeheader();writer.writerows(filas)


def evaluar_candidatos(reviews):
    grupos=np.array(grupos_sin_texto_duplicado(reviews))
    y=np.array([r['critica'] for r in reviews]); xx=np.arange(len(reviews))
    splitter=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=42)
    folds=list(splitter.split(xx,y,groups=grupos))
    for a,b in folds:
        if set(grupos[a]) & set(grupos[b]):
            raise AssertionError('Solapamiento en grupos entre entrenamiento y validación')
    nombres=('resena_palabras','resena_caracteres','segmentos_caracteres')
    filas=[]; resultados=[]
    for cand in nombres:
        pred=np.zeros(len(reviews),dtype=int)
        proba=np.zeros(len(reviews),dtype=float)
        for fold,(ia,iv) in enumerate(folds,1):
            tr=[reviews[i] for i in ia]; va=[reviews[i] for i in iv]
            score,p,_,limite=ajustar_y_predecir(tr,va,cand)
            pred[iv]=p;proba[iv]=score
            print(f'{cand} · pliegue {fold}/5: {len(tr)} entrenamiento, {len(va)} validación',flush=True)
            for j,s,pj in zip(iv,score,p):
                filas.append({'modelo':cand,'pliegue':fold,'review_id':reviews[j]['id'],
                              'real_contiene_critica':int(y[j]),'probabilidad':round(float(s),6),
                              'umbral':limite,'prediccion':int(pj)})
        met=calcular_metricas(y,pred)
        resultados.append({'modelo':cand,'umbral':limite,**met})
    # Criterio de selección explícito: máximo F2 de CV (premia recall sobre precision),
    # desempate por precisión y después por orden definido. NO usa spanish_test.json.
    elegido=max(resultados,key=lambda r:(r['f2'],r['precision']))
    return resultados,filas,elegido,len(set(grupos))


def entrenar_final(reviews,nombre):
    model=pipeline(nombre)
    if nombre.startswith('resena_'):
        X=[r['texto'] for r in reviews]; y=[r['critica'] for r in reviews]
        umbral=0.5
    else:
        X=[s for r in reviews for s in r['segmentos']]
        y=[v for r in reviews for v in r['etiquetas_segmento']]
        umbral=0.70
    model.fit(X,y)
    return {'modelo':model,'tipo':nombre,'umbral_fijo':umbral,'version':VERSION,
            'unidad_objetivo':'presencia_de_n_en_aspectos_objetivo',
            'fuente':RUTA_ENTRENAMIENTO,'segmentador':'limites_segmento_trip_maml_para_entrenamiento'}


def ejecutar(archivo_zip,salida):
    salida=Path(salida);salida.mkdir(parents=True,exist_ok=True)
    reviews=cargar_entrenamiento(archivo_zip)
    if len(reviews)<50 or len(set(r['critica'] for r in reviews))!=2:
        raise ValueError('Insuficientes datos o falta una clase')
    resultados,filas,elegido,grupos=evaluar_candidatos(reviews)
    paquete=entrenar_final(reviews,elegido['modelo'])
    dump(paquete,salida/'detector_quejas_experimental.joblib')
    info={'estado':'EXPERIMENTAL_NO_INTEGRADO_EN_ALERTAS',
          'datos':'SOLO spanish_training.json','n_resenas':len(reviews),
          'n_resenas_con_critica':sum(r['critica'] for r in reviews),
          'grupos_cuidados_en_cv':grupos,
          'etiqueta':'Existe al menos un segmento con polaridad n en CLEANLINESS/SERVICE/LOCATION/VALUE',
          'configuraciones_propuestas_antes_de_cv':['resena_palabras','resena_caracteres','segmentos_caracteres'],
          'comparacion_cv':resultados,'seleccionado_por_f2_en_cv':elegido['modelo'],
          'modelo_entrenado_final':'detector_quejas_experimental.joblib',
          'no_acredita':'85% de exactitud de temas y sentimiento por reseña; ni alertas en ventanas temporales, ni 24h',
          'advertencias':['Todas las filas analizadas provienen de entrenamiento; NO se abrió spanish_test.json.',
                          'Las métricas de selección de modelo son exploratorias sobre OOF; el F2 del ganador es optimista por selección.',
                          'Las etiquetas negativas de segmentos no equivalen a polaridad global.',
                          'Una clasificación binaria de crítica no reemplaza el clasificador multiaspecto del diseño.',
                          'No se usa el detector nuevo para alertar en la aplicación existente.']}
    (salida/'informe_paso8.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    guardar_csv(salida/'predicciones_cv.csv',filas)
    guardar_csv(salida/'comparacion_modelos.csv',resultados)
    print('AUDITORIA: ',len(reviews),'reseñas originales de entrenamiento; con alguna queja:',info['n_resenas_con_critica'])
    for res in resultados:
        print(f"{res['modelo']}: P={res['precision']:.3f} R={res['recall']:.3f} F1={res['f1']:.3f} F2={res['f2']:.3f} TP={res['tp']} FP={res['fp']} FN={res['fn']}")
    print('SELECCIONADO POR F2 DE CV:',elegido['modelo'])
    print('IMPORTANTE: train ONLY, modelo nuevo NO integrado con alertas; no mide SMART 85 %.')
    print('Archivos:',salida.resolve())
    return info

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--zip',required=True,help='ZIP Trip-MAML original')
    parser.add_argument('--salida',default='salida_paso8_cv')
    args=parser.parse_args()
    ejecutar(args.zip,args.salida)
