# Origen de datos, atribuciones y licencias

## Datos y citas científicas

ReviewPulse trabaja con reseñas del corpus **Trip-MAML: Multi-Aspect Multi-Lingual review dataset**, con anotaciones de sentimientos por aspecto y por segmento. En los experimentos se usaron 292 reseñas españolas de entrenamiento y 125 del conjunto de prueba. La partición de test ya había sido consultada exploratoriamente; no la describimos como evaluación ciega.

Referencias indicadas en el README del corpus original:

1. Marcheggiani, D., Täckström, O., Esuli, A. y Sebastiani, F. (2014). *Hierarchical multi-label conditional random fields for aspect-oriented opinion mining*. ECIR.
2. Jiménez Zafra, S. M., Berardi, G., Esuli, A., Marcheggiani, D., Martín-Valdivia, M. T. y Moreo Fernández, A. (2015). *A Multi-lingual Annotated Dataset for Aspect-Oriented Opinion Mining*. EMNLP.

El ZIP del corpus disponible para este proyecto contiene un README que cita estos trabajos, pero **no contiene un archivo LICENSE que autorice explícitamente su redistribución**. En consecuencia, no se incluyen en este repositorio los JSON con las reseñas originales, predicciones fila por fila ni logs con textos de ese corpus. Verifica los términos actuales del proveedor antes de cualquier reutilización pública de datos. El archivo `datos/resenas_sinteticas.csv` es una muestra creada para demostración.

## Modelo entrenado

El archivo `modelos/modelos_multiaspecto.joblib` fue generado durante la práctica académica a partir del corpus. Se conserva por reproducibilidad, pero su distribución pública también merece revisión de los términos del origen de datos. Antes de hacer público el repositorio, las autoras deberán decidir si están autorizadas a distribuir este modelo. Si no pueden confirmarlo, mantengan el repositorio privado temporalmente y consulten al docente cómo dar acceso evaluable sin redistribuir indebidamente.

La integridad se comprueba con `modelos/SHA256.txt` y `verificar_proyecto.py`. No abras modelos `.joblib` de fuentes desconocidas: el formato ejecuta deserialización de Python.

## Licencia del código

**No se impone una licencia de software automáticamente** en este paquete. Las integrantes deberán elegir si desean conceder una licencia de uso/modificación al código. Si optan por hacerlo, añadan el archivo `LICENSE` correspondiente. Publicar un repositorio no equivale por sí solo a conceder una licencia abierta.
