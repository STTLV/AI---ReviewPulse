# Resultados agregados y alcance de la evidencia

Esta página resume resultados **históricos ya verificados**; no son pruebas nuevas ni resultados de producción. Los datos agregados están en [`resultados/metricas_agregadas.json`](resultados/metricas_agregadas.json) y [`resultados/escenarios_agregados.csv`](resultados/escenarios_agregados.csv). Los registros completos se entregan al docente por separado tras revisar privacidad y derechos del corpus.

| Compromiso SMART original | Fórmula o criterio | Resultado disponible | Evaluación |
|---|---|---|---|
| Exactitud de tema + sentimiento ≥85 % | Reseñas con todos los temas y sentimientos correctos / total | 45/125 = **36,00 %** | **No alcanza**. Test explorado previamente; referencias agregadas desde segmentos |
| Detectar variaciones en ≤24 h | Horas desde cierre semanal hasta detectar anomalía | Sin medición integral | **No demostrado**. No existe serie temporal etiquetada para validar detección real |
| Reportar y entregar en ≤24 h | Horas desde cierre hasta entrega efectiva al gerente | 6/6 pruebas de cálculo con fechas **simuladas** | **No demostrado**. El cierre requiere ejecución; no hay envío externo |
| Fracción de alertas falsas <10 % | FP / (TP + FP) | 1/(15+1)=**6,25 %** | Se satisface **solo en simulación controlada** con oráculo, no de extremo a extremo |

## Pruebas funcionales

- 49 tests de agente y módulos, ocho de experimento de quejas y nueve de umbrales: **66 tests** aprobados en Windows (Paso 11).
- En simulación reproducible: 12 escenarios × 5 repeticiones = **60 ejecuciones**, cuatro escenarios de falla esperada, 30 decisiones evaluables de alerta (TP=15, FP=1, FN=0, TN=14).
- Las métricas de clasificación real evalúan 125 reseñas de prueba de Trip-MAML cuyo conjunto se había consultado en investigación exploratoria. Por ello **no se presenta validación ciega**.

## Cómo reproducir

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest discover -s experimentos\paso8\tests -v
.\.venv\Scripts\python.exe -m unittest discover -s experimentos\paso9\tests -v
.\.venv\Scripts\python.exe ejecutar_pruebas_escenarios.py --salida salida_paso4_alertas --repeticiones 5 --semilla 20261018
.\.venv\Scripts\python.exe ejecutar_pruebas_temporales.py --salida salida_paso4_tiempos
```

Para volver a calcular la evaluación de 125 reseñas, obtén el ZIP original Trip-MAML y sigue el README principal. Los scripts de pruebas generan salidas bajo `salida_*`, excluidas de Git.

**Precaución:** éxito de tests, oráculo sintético y cálculo de fechas simuladas no acreditan exactitud ≥85 %, detección real en ≤24 h ni entrega efectiva al gerente.
