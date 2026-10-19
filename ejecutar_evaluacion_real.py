"""Ejecuta evaluación de seguimiento NLP y replay de integración auditables."""
import argparse
import json
from pathlib import Path
from src.evaluacion_real import ejecutar

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--zip',type=Path,required=True,help='ZIP ORIGINAL de trip-maml-main')
    p.add_argument('--salida',type=Path,default=Path('salida_paso6_evaluacion_real'))
    p.add_argument('--solo-nlp',action='store_true')
    args=p.parse_args()
    r=ejecutar(args.zip,args.salida,not args.solo_nlp)
    x=r['modelo_real']
    print('RESEÑAS REALES DE PRUEBA:',x['cantidad_resenas'])
    print('EXACTITUD TEMA (CONJUNTO):',round(100*x['exactitud_temas_conjunto'],2),'%')
    print('EXACTITUD ESTRICTA TEMA+SENTIMIENTO:',round(100*x['exactitud_estricta_temas_y_sentimientos'],2),'%')
    print('F1 MACRO TEMAS:',round(x['f1_macro_temas'],4))
    print('CUMPLE 85% ESTRICTO:',x['cumple_85_estricto'])
    if 'replay_integracion' in r:
        v=r['replay_integracion'];print('REPLAY: ',json.dumps({k:v[k] for k in ('reseñas_guardadas','reportes_guardados','alertas_guardadas')},ensure_ascii=False))
    print('ATENCIÓN: test ya observado en Fase 1, no validación ciega. Etiquetas agregadas.')
    print('Las semanas del replay son SINTÉTICAS; no mide detección de anomalías reales ni 24h.')
    print('ARCHIVOS:',args.salida.resolve())
