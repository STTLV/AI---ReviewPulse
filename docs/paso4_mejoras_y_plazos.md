# Fase 2 · Paso 4: detector de volumen y control temporal

## Procedencia y objetivos

El archivo del usuario `metricas_politica.json` y los resultados de Paso 3 muestran 60 ejecuciones: 12 escenarios, 5 repeticiones; en 30 casos evaluables, TP=10, FP=1, FN=5, TN=14. E05 (incremento de volumen solamente) originó cinco falsos negativos. El dataset de estas pruebas es **sintético**, con oráculo controlado independiente del clasificador NLP.

## Hipótesis fijadas antes de volver a ejecutar esta batería

1. Mantener el umbral de negatividad en 0,30 puntos porcentuales (30 p. p.).
2. Generar alerta independiente si el conteo de la semana es al menos el **doble** del promedio histórico **y** la diferencia absoluta es >= 10 reseñas.
3. Exigir mínimo de cinco reseñas actuales y dos semanas históricas; promediar hasta tres.
4. Guardar una sola alerta semanal, aun si aumentan negatividad y volumen simultáneamente.

Los umbrales no son estándares clínicos o industriales: son parámetros **hipotéticos de demostración** que requieren justificación o calibración adicional. No se ha ajustado la regla observando un conjunto de prueba ciego. El ejercicio E05 es conocido y se utiliza como prueba de regresión.

## Evaluación reproducida (semilla base 20261018)

| Indicador | Antes | Después |
|---|---:|---:|
| TP | 10 | 15 |
| FP | 1 | 1 |
| FN | 5 | 0 |
| TN | 14 | 14 |
| Recall anomalías (TP/(TP+FN)) | 0,6667 | 1,0000 |
| Proporción alertas falsas (FP/(TP+FP)) | 0,0909 | 0,0625 |
| E05 alertas (5 repeticiones) | 0 | 5 |

Estos resultados **solo corresponden a la batería sintética de la política de alertas**. No acreditan el objetivo SMART <10 % en operación real ni la detección de reseñas desde TripAdvisor/Google.

## Registro de tiempos

Los reportes nuevos guardan:
- `cierre_calendario_utc`: medianoche UTC del lunes siguiente a la semana ISO (convención provisional).
- `generado_utc`: instante real de creación local del reporte, representado en UTC.
- `plazo_reporte`: horas transcurridas y regla <=24 h, solo si la creación ocurre después del cierre.

Se agregaron seis escenarios con fechas **SIMULADAS** para comprobar la regla: 6 h, exactamente 24 h, 24 h + 1 s, 30 h, entrega ausente y creación antes del cierre. Las seis comprobaciones concuerdan con sus resultados esperados. Este cálculo **no** demuestra ejecución autónoma en el momento adecuado ni recepción de notificaciones por el gerente.

## Lo que falta antes de afirmar cumplimiento SMART

1. Evaluación final del clasificador en reseñas completas con etiquetas de referencia válidas, diferenciando clasificación multiaspecto de sentimiento global y evitando contaminación de entrenamiento/prueba.
2. Integrar el clasificador NLP real en las pruebas de anomalías y medir tasas con escenarios validados.
3. Implementar planificador de ejecución automática, temporización desde cierre semanal en la zona horaria del hotel piloto y medio de entrega apropiado; ensayar ambos plazos de 24 h y registrar acuse o evidencia de recepción.
4. Completar la tabla de medidas SMART, análisis de fallas de máximo una página y trazabilidad de logs de acuerdo con la rúbrica.
5. Ajustar documentación UML y siete componentes IBM a los módulos efectivamente implementados.

## Corrección documental propuesta

En sección 9.6 del diseño ajustado registrar: «Se amplió la regla de detección histórica para incorporar anomalías de volumen además de variaciones de negatividad. Se añadieron marcas de tiempo y cálculo de latencia, pero la ejecución del cierre sigue siendo manual y las alertas se publican solo en el panel. Los tests temporales utilizan fechas simuladas.»
