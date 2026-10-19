"""Exploración RETROSPECTIVA de umbrales usando predicciones OOF de Paso 8.

No entrena, no usa spanish_test.json, no modifica ReviewPulse ni recomienda
activar alertas. No hay evaluación independiente para elegir umbral.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

UMBRALES = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60)


def cargar_predicciones(ruta):
    with Path(ruta).open('r', encoding='utf-8-sig', newline='') as archivo:
        filas = list(csv.DictReader(archivo))
    requeridas = {'modelo', 'review_id', 'real_contiene_critica', 'probabilidad', 'pliegue'}
    if not filas or not requeridas.issubset(filas[0]):
        raise ValueError('CSV vacío o columnas incompatibles con el Paso 8')
    modelos = defaultdict(list)
    for fila in filas:
        modelo = fila['modelo'].strip()
        if not modelo:
            raise ValueError('Modelo sin nombre')
        y = int(fila['real_contiene_critica'])
        p = float(fila['probabilidad'])
        if y not in (0, 1) or not (0 <= p <= 1):
            raise ValueError('Etiqueta o puntuación fuera de rango')
        modelos[modelo].append((fila['review_id'], y, p, fila['pliegue']))
    for nombre, valores in modelos.items():
        if len({r[0] for r in valores}) != len(valores):
            raise ValueError(f'Review ID duplicado en {nombre}')
    referencias = {nombre: {id_: y for id_, y, _, _ in rows} for nombre, rows in modelos.items()}
    if len({frozenset(r.items()) for r in referencias.values()}) > 1:
        raise ValueError('No son comparables las mismas reseñas y etiquetas entre modelos')
    return modelos


def metricas(reales, puntuaciones, umbral):
    if len(reales) != len(puntuaciones) or not reales:
        raise ValueError('Entradas vacías o desalineadas')
    tp = fp = fn = tn = 0
    for y, score in zip(reales, puntuaciones):
        pred = score >= umbral
        if y == 1 and pred: tp += 1
        elif y == 0 and pred: fp += 1
        elif y == 1 and not pred: fn += 1
        else: tn += 1
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    f2 = 5 * precision * recall / (4 * precision + recall) if 4 * precision + recall else 0
    return {'umbral': umbral, 'n': len(reales), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': precision, 'recall': recall, 'f1': f1, 'f2': f2,
            'fraccion_predicciones_positivas_falsas': fp / (tp + fp) if tp + fp else None}


def guardar_csv(ruta, filas):
    with Path(ruta).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0]))
        writer.writeheader()
        writer.writerows(filas)


def ejecutar(entrada, salida):
    modelos = cargar_predicciones(entrada)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    resultados = []
    for nombre in sorted(modelos):
        valores = modelos[nombre]
        y = [r[1] for r in valores]
        s = [r[2] for r in valores]
        for umbral in UMBRALES:
            resultados.append({'modelo': nombre, **metricas(y, s, umbral)})
    guardar_csv(salida / 'comparacion_umbrales.csv', resultados)
    referencia = [r for r in resultados if r['modelo'] == 'resena_palabras']
    if not referencia:
        raise ValueError('No se encuentra el modelo resena_palabras del Paso 8')
    comparacion = {str(r['umbral']): r for r in referencia}
    meta = {
        'estado': 'DIAGNOSTICO_EXPLORATORIO_SIN_INTEGRACION',
        'fuente': str(Path(entrada).name),
        'n_reseñas': len(modelos['resena_palabras']),
        'metodologia': 'Recalcula métricas con predicciones fuera de cada pliegue de entrenamiento (OOF).',
        'modelo_referencia': 'resena_palabras',
        'umbral_original': comparacion['0.5'],
        'umbral_comparativo': comparacion['0.45'],
        'advertencias': [
            'Revisar muchos umbrales sobre estas mismas predicciones sesga al alza el mejor resultado; NO hay validación independiente.',
            'Este es un DETECTOR BINARIO POR RESEÑA; la fracción de predicciones falsas NO es la medida SMART de alertas semanales.',
            'NO se estima 85% de sentimiento+tema, ni detección en 24 horas, ni envío de reportes.',
            'Puntuaciones de regresión logística no sustituyen una validación de calibración en la población objetivo.',
            'El Paso 9 NO cambia modelo, umbral, SQLite, interfaz, ni política de alertas del agente.'
        ]
    }
    (salida/'resumen.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    with (salida/'lectura.txt').open('w', encoding='utf-8') as f:
        f.write('PASO 9: comparaciones exploratorias de umbral; NO integración\n')
        f.write('Modelo resena_palabras. P=precisión, R=recall, FP=reseñas sin queja clasificadas como con queja.\n')
        for r in referencia:
            f.write(f"t={r['umbral']:.2f} TP={r['tp']:2} FP={r['fp']:3} FN={r['fn']:2} P={r['precision']:.3f} R={r['recall']:.3f} F2={r['f2']:.3f}\n")
        f.write('\nAVISO: No es válida la comparación directa con falsos positivos de alertas semanales.\n')
    print((salida/'lectura.txt').read_text(encoding='utf-8'))
    return resultados


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diagnóstico retrospectivo de umbrales del Paso 8')
    parser.add_argument('--entrada', required=True)
    parser.add_argument('--salida', required=True)
    args = parser.parse_args()
    ejecutar(args.entrada, args.salida)
