# Control documental previo a la entrega final de ReviewPulse

## Tabla de cambios sugerida al INICIO del documento ajustado

La tabla describe cambios verificados del diseño original; **verificar primero si el profesor envió retroalimentación específica**, porque este material no contiene esa retroalimentación.

| Sección | Antes | Ahora (para reflejar implementación real) | Motivo |
|---|---|---|---|
| Inicio | Documento de diseño sin Fase 1 ni bitácora de cambios | Incorporar tabla de cambios y la matriz de selección ponderada/justificación antes de la introducción | Requisito del profesor; matriz y justificación de Fase 1 elaboradas por separado |
| 2. Tipo de agente | Basado en modelo y orientado a objetivos | Conservar tipología y vincular a `AgenteReviewPulse` y `Memoria` | Estado persistente y metas de clasificación, alerta y reporte |
| 3. Ambiente | Estocástico, parcialmente observable, secuencial, dinámico, discreto y agente único | Conservar y describir simulación estocástica con 12 escenarios × 5 repeticiones | Demostración operacional |
| 5. Entradas | Reseñas de TripAdvisor/Google más metadatos y umbrales del gerente | Formulario, CSV o simulador; validación concreta; configuración en clase Python | Conectores y control gerencial en GUI no implementados |
| 6. Actuadores | Clasificación, reporte y notificación por correo/mensajería | Persistencia SQLite, panel Streamlit y log JSONL; sin correo | Reflejar efecto real |
| 7. SMART | 85 %, 24 h, 24 h, <10 % | Mantener umbrales, añadir fórmulas y estado de evidencia; documentar incumplimiento 36 % estricto | Prueba auditable sin redefinir la meta posteriormente |
| 8. IBM | Siete módulos proyectados | Tabla de correspondencia con archivos reales, parciales/no implementados | Arquitectura real frente a diseño |
| 9. Conclusiones | Conclusiones originales | Insertar sección 9 Desarrollo del agente y mover conclusiones a 10 | Numeración exigida |
| Nuevas secciones | No había apartado de desarrollo | Arquitectura, tecnologías, entradas, salidas, UML, diferencias, pruebas, límites y enlaces | Requisitos de Fase 2 y 3 |

## Matriz de cumplimiento previa a la entrega

| Entregable o criterio | Estado según evidencia proporcionada | Acción verificable pendiente |
|---|---|---|
| Fase 1 matriz y justificación | Disponibles como archivos separados; ReviewPulse elegido | Insertarlas antes del diseño inicial y verificar consistencia con matriz final (3,80 frente a 3,20) |
| Correcciones del profesor | No se aportó retroalimentación específica del diseño ReviewPulse en esta auditoría | Confirmar si existen observaciones y documentar cada corrección |
| Código reproducible | Código local con `requirements.txt`, README y 49 pruebas originales | Publicar repositorio limpio y probar instalación en otro equipo |
| Ambiente estocástico | 12 escenarios × 5 repeticiones, 4 fallas esperadas | Adjuntar resultados finales y logs con semilla, media y desviación estándar |
| SMART exactitud | 36 % estricta; incumplida | Reconocer incumplimiento; validación nueva si se mejora modelo |
| SMART alerta en 24 h | Solo cálculos aislados simulados | Cronometrar anomalías con modelo real y cierre real; programar ejecución |
| SMART reporte entregado en 24 h | No existe envío externo | Implementar entrega con evidencia o declarar incumplimiento |
| SMART <10 % falsas alertas | 6,25 % solo oráculo simulado | Evaluar sistema con textos reales y eventos temporales etiquetados |
| UML normal/excepción | Mermaid editable generado y figura de referencia | Verificar visualmente en editor Mermaid si se modifica |
| Enlace de evidencia | No proporcionado | Publicar plataforma o video ≤20 min con cámara y voz de ambas integrantes |
| Bitácora de IA | No incorporada aquí | Documentar herramienta, tarea, resultado, validación humana y modificaciones |

## Nota metodológica del Paso 9

- Las 9 pruebas del módulo de umbrales terminaron en `OK`; además pasaron las 49 de regresión que probó la usuaria en el Paso 8.
- En 292 predicciones de validación cruzada fuera de pliegue, el detector binario de quejas (`resena_palabras`) con `t=0,50`: TP=28, FP=15, FN=28, TN=221, precisión 65,12 %, recall 50 %.
- El umbral `t=0,45` retrospectivo: TP=40, FP=40, FN=16, TN=196, precisión 50 %, recall 71,43 %.
- El umbral **no** se modificó en el agente. Los FP de reseña **no** son FP de alerta semanal y estos umbrales no se optimizaron en un conjunto completamente independiente.
