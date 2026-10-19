# ReviewPulse-Agent · Repositorio reproducible · versión académica de entrega

**Universidad Tecnológica de Bolívar · Inteligencia Artificial**  
**Estado:** prototipo de investigación/curso; no producto hotelero de producción. Este repositorio contiene la versión consolidada y validada en Windows, preparada para publicación en GitHub. El modelo activo **no fue reemplazado**.

## ¿Qué hace?

Recibe reseñas de hoteles en español mediante formulario local o CSV para la demostración. Las valida, predice temas (*limpieza, servicio, ubicación, precio/valor*) y sentimiento por tema con un artefacto de aprendizaje automático entrenado previamente, registra estado persistente SQLite y genera reportes semanales. Con historial suficiente, emite alertas **en el panel local** si crece la proporción negativa o el volumen. Registra percepciones, decisiones y acciones en JSONL con UTC.

- **No** se conecta a TripAdvisor ni Google Reviews, **no** envía correos y **no** garantiza dos plazos de 24 horas. El cierre de semanas vencidas corre **solo cuando se invoca** el ejecutor o botón; para recurrencia se necesita un programador externo.
- El modelo real obtuvo **36,00 % de coincidencia exacta en tema+sentimiento** sobre 125 reseñas del conjunto de prueba ya examinado en una fase exploratoria; **no alcanza** la meta SMART ≥85 %. Las etiquetas de referencia por reseña son agregaciones de anotaciones por segmento.
- La batería **sintética** de alertas (12 escenarios × 5 repeticiones) produjo 15 TP, 1 FP, 0 FN y 14 TN: `FP/(TP+FP)=6,25 %`. **No** representa la tasa de falsas alarmas del agente conectado a reseñas reales.
- El detector de quejas de `experimentos/paso8` y la comparación de umbrales de `experimentos/paso9` **no están integrados** al agente y no se deben presentar como mejoras de producción.

## Requisitos y procedencia

Python recomendado: **3.11–3.14**, con instalador `py` disponible en Windows. La usuaria ejecutó las pruebas en Windows con Python 3.14; la consolidación de código se comprobó por separado con Python 3.13 y scikit-learn 1.8.0. Las dependencias admiten rangos, **no son un lockfile exacto**; conserva el resultado de `pip freeze` en la evidencia si necesitas reproducir el entorno al detalle. Streamlit está en `requirements.txt`.

El artefacto `modelos/modelos_multiaspecto.joblib` es un modelo previamente entrenado con reseñas españolas de **Trip-MAML** (`ES/spanish_training.json`, 292 reseñas). Comprueba su checksum con `verificar_proyecto.py`. **No cargues artefactos `.joblib` procedentes de desconocidos**: la deserialización no es segura para archivos no confiables. El dataset original **no se redistribuye aquí**; para repetir la evaluación deberás obtener `trip-maml-main.zip` desde su fuente original y respetar sus condiciones de uso.

## Instalación limpia desde PowerShell

Abre la carpeta `ReviewPulse_Entrega_Final` en VS Code. No abras una carpeta superior diferente cuando lances los comandos.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verificar_proyecto.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest discover -s experimentos\paso8\tests -v
.\.venv\Scripts\python.exe -m unittest discover -s experimentos\paso9\tests -v
```

Se esperan **49, 8 y 9 pruebas** respectivamente. Estas prueban funcionamiento de código, no la exactitud del clasificador ni el cumplimiento integral de los cuatro SMART.

## Demostración local

```powershell
.\.venv\Scripts\python.exe ejecutar_demo.py --salida salida_demo_nueva
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre `http://localhost:8501` si el navegador no se abre solo. El demo CLI utiliza 40 reseñas **sintéticas** y guarda su propia memoria en `salida_demo_nueva/`. La aplicación usa **otra** base en `salida_app/` (se crea vacía al iniciar). No verás las reseñas del CLI en la interfaz si no las introduces allí.

El panel contiene seis pestañas: **Percepción**, **Reportes semanales**, **Alertas e historial**, **Evidencia**, **Pruebas controladas** y **Cierre semanal**. No uses textos con información personal de clientes reales.

## Escenarios controlados y tiempo simulado

```powershell
.\.venv\Scripts\python.exe ejecutar_pruebas_escenarios.py --salida salida_paso4_alertas --repeticiones 5 --semilla 20261018
.\.venv\Scripts\python.exe ejecutar_pruebas_temporales.py --salida salida_paso4_tiempos
.\.venv\Scripts\python.exe ejecutar_cierre_pendiente.py --salida salida_app
```

- La primera batería usa un **oráculo sintético** para aislar memoria y política de alertas; **no evalúa el modelo NLP**.
- La segunda evalúa **seis casos con marcas temporales simuladas**, no envío real.
- El tercer comando hace **una sola pasada** sobre las semanas de `salida_app`. Puede devolver `0` reportes si no hay semanas vencidas con reseñas. No es un programador autónomo ni envía alertas externas.

## Evaluación de seguimiento con reseñas del corpus

Cuando tengas el ZIP original `trip-maml-main.zip` en Descargas:

```powershell
.\.venv\Scripts\python.exe ejecutar_evaluacion_real.py --zip "$env:USERPROFILE\Downloads\trip-maml-main.zip" --salida salida_paso6_evaluacion_real
```

Se procesan **125 reseñas** del `ES/spanish_test.json` del corpus original, con referencia derivada de segmentos. El `replay` les asigna fechas ficticias y guarda estados en SQLite aparte: no mide anomalías temporales reales. El conjunto de test ya había sido observado en una fase anterior, **no es validación ciega**.

## Experimentos NO integrados en alertas

Entrenamiento binario de quejas usando **solo el train**:

```powershell
.\.venv\Scripts\python.exe experimentos\paso8\entrenar_quejas.py --zip "$env:USERPROFILE\Downloads\trip-maml-main.zip" --salida experimentos\paso8\salida_local
.\.venv\Scripts\python.exe experimentos\paso8\comparar_predictores.py --texto "El servicio fue excelente pero la habitación estaba muy sucia." --modelo experimentos\paso8\salida_local\detector_quejas_experimental.joblib
.\.venv\Scripts\python.exe experimentos\paso9\analizar_umbrales.py --entrada experimentos\paso8\salida_local\predicciones_cv.csv --salida experimentos\paso9\salida_local
```

El modelo experimental no se incluye dentro de `src/modelo.py` ni activa alertas. Los scripts producen archivos bajo `salida_local/`, ignorados por Git.

## Arquitectura y documentación

- `src/percepcion.py`: validación y percepción.
- `src/modelo.py`: modelo activo multiaspecto.
- `src/memoria.py`: SQLite, historial semanal y estado.
- `src/decision.py`: umbrales de negatividad y volumen.
- `src/agente.py`: coordinación percepción → decisión → acción.
- `src/automatizacion.py` y `src/tiempos.py`: pasada de cierre pendiente y registro de latencia.
- `src/registro.py`: trazas JSONL.
- `src/simulacion.py` / `src/simulacion_temporal.py`: escenarios reproducibles (oráculo controlado y fechas simuladas).
- `docs/ESTADO_ACTUAL.md`: matriz de cumplimiento, limitaciones y siguientes entregables.
- `docs/PASO10_Seccion9_desarrollo.md`, `docs/PASO10_Tabla_cambios_y_control.md` y `docs/uml/`: borradores de arquitectura, UML y sección de desarrollo para **integrar** al documento académico original, no documento final.

## Seguridad y publicación

Nunca subas a GitHub `.venv`, `salida_app/`, bases SQLite, `.env`, logs de reseñas reales ni resultados de usuarios. `.gitignore` ayuda, pero revisa siempre `git status` antes de publicar. Los modelos `.joblib` solo deben cargarse cuando su procedencia sea confiable. La copia de **evidencias privadas** se entrega separada del código publicable; revisa permisos de redistribución antes de publicar muestras del corpus Trip-MAML.

## Entregables pendientes

**Preparada para GitHub, todavía sin URL pública confirmada.** Faltan: publicación y comprobación del enlace; documento PDF unificado con Fase 1, diseño original y sección 9; enlaces a demostración en vídeo (ambas integrantes con voz/cámara, ≤20 min) o despliegue; bitácora de uso de IA; tabla definitiva SMART, fórmulas y limitaciones de 24 horas. Ver `docs/ESTADO_ACTUAL.md`.


## Resultados resumidos y publicación

- [Resumen agregado de los cuatro SMART y sus limitaciones](docs/RESULTADOS_SMART_AGREGADOS.md). La evidencia completa de los ensayos se conserva como entregable académico separado.
- [Instrucciones precisas para publicar este proyecto](docs/GUIA_PUBLICACION_GITHUB.md), incluyendo privacidad, `git status` y comprobación del enlace.
- [Procedencia de datos y cuestiones de licencia](docs/PROCEDENCIA_Y_LICENCIAS.md). No se redistribuyen reseñas originales. La autorización/licencia para distribuir el modelo derivado debe verificarse antes de publicar.
- [Flujo de pruebas automáticas de GitHub](.github/workflows/pruebas.yml), pendiente de comprobar en GitHub después del primer `push`.

La versión pública debe señalar expresamente que las 66 pruebas de software aprobadas **no prueban** el cumplimiento integral de las metas SMART.
