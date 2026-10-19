"""Ejecutar las seis comprobaciones de latencia HIPOTÉTICAS."""
import argparse
from src.simulacion_temporal import ejecutar_pruebas_temporales

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--salida',default='salida_temporal_paso4')
    args=p.parse_args()
    r=ejecutar_pruebas_temporales(args.salida)
    print('PRUEBAS TEMPORALES SIMULADAS:',r['resumen'])
    print('Carpeta:',r['directorio'])
if __name__=='__main__':main()
