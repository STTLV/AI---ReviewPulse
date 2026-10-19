> **DOCUMENTO HISTÓRICO.** Refleja el estado al finalizar el paso indicado y algunas limitaciones ya se corrigieron en pasos posteriores. Para el estado actual consulte `docs/ESTADO_ACTUAL.md`.

# Estado de implementación, Fase 2, Paso 2

## Qué está implementado
- Clasificación con modelo real multiaspecto previamente entrenado en Trip-MAML ES / `spanish_training.json` (292 reseñas).
- Percepción por formulario y archivo CSV en CLI, normalización y validación de texto, fecha, origen y calificación.
- Memoria persistente en SQLite y control de duplicados por `id`.
- Detección semanal por diferencia entre proporciones: proporción con alguna señal negativa de la semana frente a la media de hasta tres semanas previas, mínimo dos semanas y cinco reseñas. Umbral de 30 puntos porcentuales provisional, no validado.
- Reporte por tema y decisión, alerta registrada en base local y visible en Streamlit.
- Logs JSONL en UTC con percepción, decisión y acción.
- Interfaz Streamlit inicial y CLI para demostración.

## Qué NO está implementado ni probado
- Conector API real a Google, TripAdvisor u otra plataforma, ni extracción automática de reseñas.
- Envío externo por correo / mensajería.
- Programación de cierre semanal automática ni garantía de notificación o reporte en 24 h.
- Alcanzar 85 % de exactitud de sentimiento y tema sobre reseñas completas. El experimento previo solo informó 31,85 % de coincidencia estricta OOF por temas y polaridades derivadas, que NO equivale a la SMART original.
- Validación de tasa de alertas falsas menor del 10 % ni conjunto de >=10 escenarios / >=5 repeticiones para entorno estocástico.
- Entorno estocástico completo, evaluación histórica cronológica y pruebas de variaciones de volumen (solo proporciones de señales negativas).
- Publicación o control de permisos de un despliegue.
- Aprendizaje en línea: deliberadamente ausente de acuerdo con el diseño original.

## Diferencias frente a diseño original a justificar en el informe
- Entrada simulada / formulario / CSV en lugar de conector real.
- Reseña multi-aspecto; si hay más de un tema no se inventa un único principal: se deja nulo, y la polaridad resumen se deriva sin referencia humana global.
- Las etiquetas `neutro_o_mixto` no se equiparan con neutral puro.
- El aviso se almacena y aparece en el panel; no se envía fuera del sistema.
- El cierre de semana se activa manualmente para este hito.
- No se admiten nuevas reseñas en una semana ya cerrada, para impedir que un reporte histórico quede desactualizado.

## Procedencia y límites
- El modelo `.joblib` se generó en Fase 1 a partir de 292 reseñas de entrenamiento de Trip-MAML.
- Para la demo se redactaron 40 reseñas sintéticas, no se usan para validar la exactitud.
- No publicar datos identificables de huéspedes. Los datos de prueba y logs deben contener solo información autorizada.
