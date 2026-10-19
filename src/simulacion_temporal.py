"""Seis escenarios HIPOTÉTICOS de tiempo sin automatización ni envíos.
Evalúan SOLO la fórmula de latencia en UTC y su umbral.
"""
from datetime import timedelta
from pathlib import Path
import csv, json
from src.tiempos import fin_de_semana_iso_utc, evaluar_plazo

ESCENARIOS_TEMPORALES=(
    ('T01','Reporte a las 6 h',6,True),
    ('T02','Reporte a las 24 h exactas',24,True),
    ('T03','Reporte a las 24 h y un segundo',24+1/3600,False),
    ('T04','Reporte a las 30 h',30,False),
    ('T05','Sin entrega del reporte',None,False),
    ('T06','Reporte antes del cierre',-1,False),
)

def ejecutar_pruebas_temporales(salida,semana='2026-W40'):
    destino=Path(salida); destino.mkdir(parents=True,exist_ok=True)
    cierre=fin_de_semana_iso_utc(semana)
    filas=[]
    for codigo,descripcion,horas,esperado in ESCENARIOS_TEMPORALES:
        creado=cierre+timedelta(hours=horas) if horas is not None else None
        r=evaluar_plazo(cierre,creado)
        filas.append({'id_escenario':codigo,'escenario':descripcion,'fecha_simulada':True,
          'cierre_utc':cierre.isoformat(),'creado_utc_simulado':creado.isoformat() if creado else '',
          'latencia_horas':r['latencia_horas'],'umbral_horas':24,
          'cumple_calculo':r['cumple'],'esperado':esperado,'prueba_correcta':r['cumple']==esperado,
          'estado':r['estado']})
    with (destino/'resultados_temporales.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)
    resumen={'escenarios':len(filas),'verificaciones_correctas':sum(r['prueba_correcta'] for r in filas),
             'evaluacion_automatizacion_real':'NO_REALIZADA',
             'evaluacion_envio_externo':'NO_IMPLEMENTADO',
             'uso':'Prueba del cálculo de plazo con fechas simuladas; no acredita SMART de 24 h.'}
    (destino/'resumen_temporal.json').write_text(json.dumps(resumen,indent=2,ensure_ascii=False),encoding='utf-8')
    return {'filas':filas,'resumen':resumen,'directorio':str(destino.resolve())}
