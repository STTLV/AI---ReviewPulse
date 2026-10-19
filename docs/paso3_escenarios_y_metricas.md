> **DOCUMENTO HISTÓRICO.** Refleja el estado al finalizar el paso indicado y algunas limitaciones ya se corrigieron en pasos posteriores. Para el estado actual consulte `docs/ESTADO_ACTUAL.md`.

# Fase 2 · Paso 3: Simulación estocástica, pruebas y trazabilidad

## Alcance
Este módulo ejecuta **12 escenarios diferentes**, con **5 repeticiones por escenario** (60 ejecuciones independientes), introduciendo aleatoriedad reproducible en la cantidad y distribución de reseñas negativas observadas. Las semillas quedan archivadas.

Se ejecuta el código real de `AgenteReviewPulse`, `Memoria` (SQLite), `evaluar_alerta` y `registrar`. Se usa un **clasificador controlado** que lee los marcadores `[NEGATIVA_SIMULADA]` y `[POSITIVA_SIMULADA]`. Este oráculo no es el modelo de lenguaje Trip-MAML. Es imprescindible distinguir entre **prueba de política** y **prueba de exactitud de IA**.

## Escenarios
| ID | Descripción | Tipo | Condición evaluada |
|---|---|---|---|
| E01 | Sentimiento semanal estable | Normal | No alertar |
| E02 | Aumento marcado de negatividad | Anomalía | Alertar con historial suficiente |
| E03 | Aumento moderado de negatividad | Anomalía | Detectar cuando supera umbral |
| E04 | Fluctuación pequeña | Límite | Evitar falsas alarmas |
| E05 | Aumento del volumen sin cambio de proporción | Límite | **Limitación conocida**: el agente actual no detecta volumen independientemente |
| E06 | Cero reseñas negativas | Normal | No alertar |
| E07 | Menos de 5 reseñas | Límite | Abstenerse de alertar |
| E08 | Una sola semana histórica | Límite | Abstenerse de alertar |
| E09 | Texto vacío | Falla esperada | Rechazar y registrar |
| E10 | Fecha imposible | Falla esperada | Rechazar y registrar |
| E11 | ID duplicado | Falla esperada | Ignorar duplicado |
| E12 | Fecha ausente | Falla esperada | Rechazar y registrar |

Se definen anomalías de negocio antes de ejecutar: E02, E03 y E05. El caso E05 muestra deliberadamente una diferencia entre el problema original (volumen o tono) y la regla actual (variación de la proporción negativa); no debemos ocultar sus omisiones.

## Fórmulas e interpretación

- `TP`: ejecuciones evaluables en las que se genera alerta y había anomalía definida.
- `FP`: se alerta sin anomalía definida.
- `FN`: no se alerta ante anomalía definida.
- `TN`: no hay alerta ni anomalía definida.
- **Proporción de alertas falsas** (la métrica SMART de la propuesta): `FP / (TP+FP)` si hay alertas; de lo contrario, **no definida**.
- **Tasa clásica de falsos positivos**: `FP / (FP+TN)` si su denominador es positivo. **No confundir ambas.**
- `recall` de anomalías: `TP / (TP+FN)` cuando existe algún evento positivo.
- Media y **desviación estándar muestral** (n−1) de alertas y tasa negativa observada por escenario.

Las métricas están asociadas **solo a este simulador y su oráculo**, no demuestran el objetivo SMART general del agente. La precisión de sentimiento/tema sigue pendiente, y el cierre semanal permanece manual.

## Exportaciones

- `escenarios_configuracion.json`: definición previa de cada caso, su alcance y su verdad de simulación.
- `resultados_ejecuciones.csv`: una fila por escenario × repetición, con semilla y tiempos reales.
- `resumen_por_escenario.csv`: medias, desviaciones y número de ejecuciones.
- `metricas_politica.json`: matriz agregada TP, FP, FN, TN y proporciones.
- `logs_escenarios.jsonl`: percepciones, decisiones y acciones, con fecha UTC, escenario y repetición.

Los escenarios se ejecutan en **bases de datos temporales independientes**. No cambian la memoria del usuario (`salida_app`) ni el estado de la demo (`salida_demo_nueva`).

## Limitaciones pendientes

1. `E05` exhibe una omisión: falta modelar alertas de volumen que consideren nivel histórico y estacionalidad.
2. La clasificación multiaspecto actual puede devolver temas incorrectos. En la prueba manual de la frase *«El servicio del hotel fue excelente y el personal muy amable»* apareció `ubicacion` junto con `servicio`, aunque el texto no menciona la ubicación explícitamente. Debe conservarse como caso de evaluación del modelo, no «corregirse» a mano en el conjunto de test.
3. El sistema aún no verifica **exactitud ≥85 % sobre reseñas completas**.
4. No existe un calendario ni servicio externo que garantice reportes o detección **dentro de 24 horas**. Las marcas de tiempo de los logs no demuestran por sí solas cumplimiento de ese plazo.
5. La **proporción de alertas falsas bajo el 10 %**, si aparece satisfecha en este laboratorio, solo es evidencia de una política con señales controladas; se requiere validación del sistema completo antes de concluir cumplimiento SMART.
6. La simulación incorpora aleatoriedad en la generación de entradas, pero el modelo NLP propiamente dicho sigue siendo determinista en inferencia con artefacto fijo. Esto es compatible con un entorno estocástico, no con aprendizaje en línea.

## Comandos

```powershell
.\.venv\Scripts\python.exe ejecutar_pruebas_escenarios.py --salida salida_pruebas_controladas --repeticiones 5 --semilla 20261018
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```
