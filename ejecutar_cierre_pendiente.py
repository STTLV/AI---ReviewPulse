"""Ejecutor invocable desde Task Scheduler/cron o manualmente.

Por seguridad NO se queda en segundo plano: una ejecución hace una pasada.
Un programador externo debe llamarlo periódicamente para automatizarlo.
"""
import argparse
import json
from src.agente import AgenteReviewPulse
from src.automatizacion import ejecutar_cierre_pendiente


def main():
    parser = argparse.ArgumentParser(description='Cierra semanas ISO que ya terminaron y aún no tienen reporte.')
    parser.add_argument('--salida',default='salida_app',help='Carpeta que comparte SQLite con Streamlit')
    argumentos = parser.parse_args()
    agente=AgenteReviewPulse(argumentos.salida)
    resumen=ejecutar_cierre_pendiente(agente)
    print(json.dumps(resumen,ensure_ascii=False,indent=2))
    if resumen['errores']:
        raise SystemExit(1)

if __name__=='__main__': main()
