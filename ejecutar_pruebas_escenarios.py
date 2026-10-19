"""Ejecuta 12 escenarios, 5 repeticiones por caso; exporta CSV/JSONL/JSON."""
import argparse, json
from src.simulacion import ejecutar_bateria

def main():
    parser=argparse.ArgumentParser(description='Batería estocástica de la política de alertas de ReviewPulse')
    parser.add_argument('--salida',default='salida_pruebas_controladas')
    parser.add_argument('--repeticiones',type=int,default=5)
    parser.add_argument('--semilla',type=int,default=20261018)
    args=parser.parse_args()
    salida=ejecutar_bateria(args.salida,args.repeticiones,args.semilla)
    print('RESUMEN DE PRUEBAS CONTROLADAS (NO mide exactitud del modelo NLP)')
    print(json.dumps(salida['metricas'],indent=2,ensure_ascii=False))
    for r in salida['resumen']:
        print(f"{r['id_escenario']}: {r['escenario']} | n={r['casos_ejecutados']} "
              f"| media alertas={r['alertas_media']:.2f} "
              f"| desv.={r['alertas_desv_estandar']:.3f}")
    print('Archivos:',salida['directorio'])
    print('AVISO: Las 4 métricas SMART del diseño NO quedan acreditadas con esta batería.')

if __name__=='__main__':main()
