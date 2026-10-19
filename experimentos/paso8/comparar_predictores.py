"""Compara una reseña con el clasificador ORIGINAL y el detector de quejas EXPERIMENTAL.

No envía alertas, no guarda en SQLite y no modifica la aplicación.
"""
import argparse
import json
from pathlib import Path
import sys

import joblib

RAIZ=Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0,str(RAIZ))
from src.modelo import clasificar


def detector_experimental(texto,artefacto):
    paquete=joblib.load(artefacto)  # abrir únicamente artefactos propios, no subidos por terceros
    nombre=paquete['tipo'];modelo=paquete['modelo'];umbral=float(paquete['umbral_fijo'])
    if nombre.startswith('resena_'):
        prob=float(modelo.predict_proba([texto])[:,1][0])
    else:
        raise ValueError('El comparador no incluye segmentador de producción para modelo por segmentos')
    return {'puntaje_queja':round(prob,4),'umbral_fijado':umbral,
            'indicio_critica':bool(prob>=umbral),'advertencia':'Puntaje discriminativo, NO probabilidad calibrada ni decisión de alerta validada'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--texto',required=True)
    p.add_argument('--modelo',default='experimentos/paso8/salida_verificada/detector_quejas_experimental.joblib')
    args=p.parse_args()
    if not args.texto.strip():raise ValueError('Texto vacío')
    print(json.dumps({'original':clasificar(args.texto),
                      'quejas_experimental':detector_experimental(args.texto,args.modelo),
                      'integrado_en_agente':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
