# Evidencia técnica · Paso 8

**Alcance:** experimento controlado de clasificación binaria de presencia de críticas hoteleras, sin cambiar el agente desplegado localmente.

Se utilizaron los archivos originales del corpus Trip-MAML en español, **únicamente** el fichero `spanish_training.json`. De sus 292 reseñas, 56 contienen por lo menos un segmento con una etiqueta negativa `n` en CLEANLINESS, SERVICE, LOCATION o VALUE.

## Resultados (validación cruzada agrupada, 5 pliegues)

| Configuración | TP | FP | FN | Precisión | Recall | F1 | F2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| TF-IDF palabras, regresión logística balanceada, reseña completa | 28 | 15 | 28 | 65,12 % | 50,00 % | 56,57 % | 52,43 % |
| TF-IDF caracteres, regresión logística balanceada, reseña completa | 27 | 15 | 29 | 64,29 % | 48,21 % | 55,10 % | 50,75 % |
| TF-IDF caracteres por segmento, máximo de puntuaciones, umbral 0,70 | 3 | 2 | 53 | 60,00 % | 5,36 % | 9,84 % | 6,55 % |

**Selección:** se conserva provisionalmente `resena_palabras` por máximo F2 de CV; este no es un resultado de test independiente.

La configuración por segmentos no mostró la mejora esperada con umbral predefinido de 0,70. No se ajustó ese valor mirando `spanish_test.json`, y cambiarlo posteriormente requeriría validación anidada o datos de ajuste independientes.

## Decisión de ingeniería

**No integrar todavía** el detector binario con `tiene_senal_negativa`. Aunque identifica algunas quejas que el módulo multiaspecto puede omitir, este experimento presenta 15 falsos positivos entre 43 señales positivas predichas, lo cual obliga a comprobar consecuencias sobre alertas semanales. La proporción 15/43 = 34,88 % **NO equivale** a la proporción de alertas falsas en el módulo de anomalías: las unidades y denominadores son distintos.

Como futura mejora, separar internamente `polaridad_resumen`, `sentimiento_por_tema` y `contiene_critica_negativa`. No reinterpretar `neutro_o_mixto` como ausencia de opiniones negativas. Exigir evaluación por reseña completa con nueva muestra etiquetada no vista antes de afirmar que mejoró el comportamiento real.

## Próximo trabajo

1. Preparar una pequeña muestra externa de reseñas no vistas, con anotación independiente de temas, polaridad y presencia de críticas.
2. Fijar de antemano métricas y criterios para decidir si añadir el detector complementario.
3. Validar que cualquier mejora no perjudique la proporción de alertas falsas a nivel de **semana**, ni el estado de memoria y los reportes.
4. Mantener las 49 pruebas del proyecto como regresión y preparar el UML y la bitácora académica.

**Transparencia:** ningún dato de prueba original de 125 reseñas se utilizó para entrenar o elegir este detector. La regla binaria no satisface por sí misma el SMART de exactitud conjunta de 85 %.
