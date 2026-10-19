"""Demostración reproducible con reseñas sintéticas y el modelo real de Fase 1."""
import argparse,csv,json
from pathlib import Path
from src.agente import AgenteReviewPulse

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--salida',default='salida_demo')
    p.add_argument('--datos',default=str(Path(__file__).resolve().parent/'datos'/'resenas_sinteticas.csv'))
    args=p.parse_args()
    agente=AgenteReviewPulse(args.salida)
    con_errores=0
    semanas=[]
    with open(args.datos,encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            resultado=agente.procesar(r)
            if resultado['estado']!='aceptada':
                con_errores+=1
            if resultado.get('semana') and resultado['semana'] not in semanas:
                semanas.append(resultado['semana'])
    for semana in sorted(semanas):
        res=agente.cerrar_semana(semana)
        resumen=res['reporte']['resumen']
        decision=res['reporte']['decision_alerta']
        print(f"{semana}: {resumen['total']} reseñas; señales negativas {resumen['con_senal_negativa']}; "
              f"decisión: {decision['razon']}")
    print(f'Reseñas almacenadas: {agente.memoria.conteo()}; errores o duplicados: {con_errores}')
    print('Alertas guardadas:',len(agente.memoria.lista_alertas()))
    print('Salida:',Path(args.salida).resolve())
    print('AVISO: datos sintéticos + clasificador experimental. No acredita los 4 SMART.')
if __name__=='__main__':main()
