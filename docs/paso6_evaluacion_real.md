# Fase 2 · Paso 6: evaluación del modelo real en reseñas completas

## Alcance y procedencia
- Modelo: artefacto propio `modelos/modelos_multiaspecto.joblib`, entrenado en la Fase 1 con `ES/spanish_training.json` de Trip-MAML.
- Evaluación: **125 reseñas** de `ES/spanish_test.json` extraídas directamente de `trip-maml-main.zip` original.
- Advertencia metodológica: el conjunto de prueba ya fue inspeccionado en experimentos de la Fase 1 y, por ello, estos resultados son **de seguimiento y no completamente ciegos**. El paso actual no reentrena modelos ni usa las etiquetas del test para ajustar decisiones.
- El corpus anota **aspectos y polaridades a nivel de segmentos**. La etiqueta por reseña y aspecto es una **agregación calculada**, no un juicio humano independiente de sentimiento global. Regla: solo `p` → positivo; solo `n` → negativo; `x`, combinaciones de `p` y `n` u otros conjuntos mixtos → `neutro_o_mixto`. Solo se miden limpieza, servicio, ubicación y precio/valor.

## Fórmulas de evaluación
- Exactitud de temas = reseñas con el **conjunto exacto** de temas predichos / reseñas evaluadas.
- Exactitud estricta de temas y polaridades = reseñas con el **diccionario completo** aspecto→polaridad idéntico a la referencia derivada / reseñas evaluadas.
- F1 macro de temas = media aritmética de los F1 binarios de las cuatro categorías, cada una usando `F1 = 2 TP/(2 TP+FP+FN)`.
- Recuentos y predicciones están en `predicciones_test_reseñas.csv` y `informe_evaluacion.json`.

## Resultados de la ejecución de referencia
- 125 reseñas; exactitud de temas: 64/125 = **51,20 %**.
- Exactitud estricta de temas y sentimientos: 45/125 = **36,00 %**.
- F1 macro de detección de temas: **0,8112**.
- Con la definición estricta anterior, **no alcanza 85 %**.

## Integración con el agente completo
Se inyectan los 125 textos en una base SQLite **aislada** y se procesa cada uno mediante `AgenteReviewPulse.procesar()`, usando el clasificador real. Luego se cierran cuatro semanas, también dentro de esa base aislada. La distribución por semanas y las fechas se asignan **artificialmente**, porque Trip-MAML no conserva fechas originales aptas para evaluar series semanales. Los logs registran las percepciones, decisiones y acciones.

En la ejecución de referencia: 125 reseñas aceptadas, cuatro reportes, cero alertas. **No** podemos llamar TP/TN/FP/FN a esas alertas: no existe una referencia independiente de las anomalías temporales reales. Las fechas ficticias tampoco acreditan el plazo SMART de 24 horas, ni existe correo externo.

## Cómo usar estos resultados en el informe
- Presentar los 41+8 tests automatizados como validación funcional del código, **no como exactitud**.
- Reportar por separado el rendimiento del NLP real, las decisiones con oráculo simulado y la integración con textos reales.
- Declarar incumplimiento de la meta estricta de 85 % y analizar ambigüedad/multiaspecto, clase `neutro_o_mixto`, desbalance y limitaciones del corpus.
- No atribuir fechas a Trip-MAML ni afirmar conexión a plataformas o envíos automáticos.
- Para una evaluación final verdaderamente independiente sería necesario reservar u obtener otro corpus etiquetado antes de ajustar el modelo; el profesor permite documentar y justificar métricas incumplidas.
