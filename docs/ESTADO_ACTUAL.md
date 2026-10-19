# Estado consolidado del proyecto · Paso 11

> Fuente: ZIP entregado por la estudiante en el Paso 11, más los borradores UML/documentales elaborados en el Paso 10. Se preservó la lógica activa de inferencia, decisión y memoria sin modificaciones; solo cambió el subtítulo descriptivo de `app.py`. Los resultados proceden de pruebas documentadas del proyecto, **no de un sistema de producción**.

## Componentes verificables

| Componente | Ruta principal | Situación |
|---|---|---|
| Validación de entrada | `src/percepcion.py` | Implementada |
| Inferencia multiaspecto | `src/modelo.py` y `modelos/modelos_multiaspecto.joblib` | Implementada; exactitud conjunta 36,00 % en evaluación de seguimiento de 125 reseñas; SMART 85 % incumplida |
| Estado y memoria | `src/memoria.py` | Implementada en SQLite |
| Detección de anomalías de negatividad y volumen | `src/decision.py` | Funciona en batería sintética con oráculo controlado; falsos avisos FP/(TP+FP) 6,25 % solo en ese escenario |
| Coordinación y acciones | `src/agente.py` | Percepción → decisión → acción y reportes locales |
| Cierre de semanas vencidas | `src/automatizacion.py`, `ejecutar_cierre_pendiente.py` | Se ejecuta a demanda; no existe programador recurrente integrado ni envío externo |
| Interfaz local | `app.py` | Seis pestañas, probada previamente en Windows de la estudiante; **no se ejecutó Streamlit en el entorno de auditoría del Paso 11** |
| Logs | `src/registro.py` | Bitácora JSONL con UTC |
| Pruebas de código | `tests/`, `experimentos/paso8/tests/`, `experimentos/paso9/tests/` | 49 + 8 + 9 suites de unittest |
| Diagramas y sección de desarrollo | `docs/PASO10_*.md`, `docs/uml/` | Borradores por integrar al PDF académico |

## SMART originales y límites

| Objetivo | Definición observada | Resultado y alcance | Estado académico |
|---|---|---|---|
| Precisión/ exactitud de sentimiento y tema ≥85 % | Coincidencia conjunta estricta de mapa de aspectos/polaridad por reseña completa | 45/125 = **36,00 %** (datos de test ya observados, etiquetas agregadas) | **No cumple**, según definición estricta de este prototipo |
| Anomalía detectada en ≤24 h tras cierre | Tiempo desde fin de semana ISO hasta la detección útil | Solo escenarios temporales con fechas simuladas; sin activación recurrente real ni alertas externas | **No demostrado integralmente** |
| Reporte semanal entregado ≤24 h tras cierre | Tiempo de cierre teórico a entrega verificable al gerente | Se registra tiempo de generación local. No existe envío externo | **No demostrado / entrega externa no implementada** |
| Falsos avisos <10 % | FP/(TP+FP) sobre alertas emitidas | 1/16 = **6,25 %** en 30 casos evaluables de política simulada con oráculo, 60 ejecuciones en total | **Resultado sintético parcial**, no verificación en hotel real |

**Importante:** pruebas de software aprobadas ≠ calidad del modelo real ≠ validación de la meta de 24 h.

## Escenarios y trazabilidad

- 12 escenarios × 5 repeticiones con semilla base `20261018` y **4 escenarios de fallo esperado**; 30 ejecuciones de decisión de alerta evaluables, restantes de excepción o insuficiencia.
- Modelo de sentimiento probado por separado con 125 reseñas Trip-MAML y referencia agregada de segmentos; éxito exacto 45/125 = 36 %.
- Replay de textos del corpus en base SQLite aislada: 125 reseñas, 4 reportes, 0 alertas, **fechas ficticias**. No es evaluación temporal real.
- Casos temporales: 6/6 verificaciones matemáticas con fechas simuladas, sin planificador operativo.
- Detector experimental binario `experimentos/paso8`: validación cruzada sobre 292 muestras de entrenamiento, 28 TP, 15 FP, 28 FN al umbral 0,50; NO integrado.
- Análisis retrospectivo `experimentos/paso9`: a umbral 0,45, 40 TP, 40 FP y 16 FN; no selecciona umbral para producción.

## Riesgos antes de publicar y entregar

1. **Sin conexión ni envío:** no proclamar fuentes TripAdvisor/Google conectadas, programación autónoma de reportes ni correos.
2. **Umbrales piloto:** parámetros de muestra/negatividad/volumen seleccionados como hipótesis del curso; no validados en hotel real.
3. **Seguridad y privacidad:** SQLite y JSONL pueden contener texto proporcionado por usuarios. No subirlos a GitHub. La aplicación está pensada para uso local de demostración, no para exposición pública con autenticación.
4. **Reproducibilidad:** `requirements.txt` utiliza rangos y no fija todas las versiones transitivas. Guardar `pip freeze` de la máquina usada en la demo.
5. **Concurrencia:** controles de duplicación y cierre están diseñados para demo de usuario único, no garantía transaccional bajo muchas instancias concurrentes.
6. **Derechos del corpus:** la evaluación requiere obtener Trip-MAML de su fuente original. Las evidencias privadas con predicciones/identificadores del corpus deben revisarse antes de su publicación.
7. **Fase 1 e informe final:** existe matriz/justificación en documentos previos, pero todavía falta integrarlos físicamente con el diseño original y sección 9/10 en un solo PDF.
8. **Repositorio y video:** publicar, validar links y preparar demostración de ≤20 min con participación de ambas integrantes.
9. **Bitácora de IA:** registrar herramientas realmente usadas, instrucciones importantes, validación y modificaciones.

## Integridad

El archivo `modelos/SHA256.txt` del proyecto recibido coincide con el SHA-256 del modelo `modelos/modelos_multiaspecto.joblib`. Ejecutar `python verificar_proyecto.py` para volver a verificarlo en cualquier equipo. No cargar modelos `.joblib` de origen desconocido.
