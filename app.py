"""Interfaz del hotel piloto; requiere Streamlit."""
from datetime import date
from pathlib import Path
import json
import streamlit as st
from src.agente import AgenteReviewPulse

st.set_page_config(page_title='ReviewPulse-Agent | Hotel piloto',page_icon='🏨',layout='wide')
RUTA=Path(__file__).resolve().parent/'salida_app'
@st.cache_resource
def agente():
    return AgenteReviewPulse(RUTA)

st.title('🏨 ReviewPulse-Agent')
st.caption('Prototipo consolidado: clasificación Trip-MAML, memoria SQLite, alertas de volumen/negatividad y cierre semanal a demanda.')
st.warning('Sin conexión a TripAdvisor/Google ni envío de correos. El 85 % SMART y la entrega automática en 24 h NO están demostrados.')
agent=agente()
tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['Percepción','Reportes semanales','Alertas e historial','Evidencia','Pruebas controladas','Cierre semanal'])
with tab1:
    st.subheader('Procesar una reseña')
    with st.form('nuevo'):
        texto=st.text_area('Texto de la reseña',placeholder='El servicio fue excelente, pero el precio fue demasiado alto.')
        c1,c2=st.columns(2)
        with c1: fecha=st.date_input('Fecha de la reseña',value=date.today())
        with c2: estrellas=st.selectbox('Calificación opcional', ['No indicada',1,2,3,4,5])
        enviada=st.form_submit_button('Ejecutar agente',type='primary')
    if enviada:
        entrada={'fecha':fecha.isoformat(),'texto':texto,'plataforma':'formulario',
                 'estrellas':None if estrellas=='No indicada' else estrellas}
        with st.spinner('Clasificando y guardando percepción...'):
            resultado=agent.procesar(entrada)
        if resultado['estado']=='aceptada':
            st.success('Percepción procesada y almacenada')
            st.json(resultado,expanded=True)
        else: st.error(resultado.get('error',str(resultado)))
with tab2:
    st.subheader('Cerrar una semana ISO y evaluar si corresponde alerta')
    st.caption('Cierre MANUAL. Se guardan tiempos reales de generación y un cierre ISO teórico (UTC) para comparar, pero no existe programación ni entrega externa automática.')
    semana=st.text_input('Semana ISO, por ejemplo 2026-W40','2026-W40')
    if st.button('Generar reporte semanal'):
        import re
        if not re.fullmatch(r'\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])',semana):
            st.error('Formato incorrecto. Ejemplo: 2026-W40')
        else:
            salida=agent.cerrar_semana(semana)
            st.json(salida,expanded=True)
    st.subheader('Reportes ya guardados')
    st.json(agent.memoria.lista_reportes(),expanded=False)
with tab3:
    st.metric('Reseñas registradas',agent.memoria.conteo())
    st.subheader('Alertas visibles para el gerente')
    st.json(agent.memoria.lista_alertas(),expanded=True)
    st.info('Las alertas se registran únicamente en el panel, no se envían fuera de la aplicación.')
with tab4:
    st.subheader('Registros de ejecución')
    ruta=agent.log
    if ruta.exists():
        texto=ruta.read_text(encoding='utf-8')
        st.download_button('Descargar logs JSONL',texto,file_name='ejecuciones.jsonl',mime='application/x-ndjson')
        ultimas=texto.splitlines()[-10:]
        st.json([json.loads(x) for x in ultimas],expanded=False)
    else:st.info('Aún no hay ejecuciones. Procesa una reseña en la primera pestaña.')
    st.caption('No subir información personal real. SQLite y JSONL guardan el texto y los resultados localmente.')

with tab5:
    st.subheader('Pruebas reproducibles de la política de alertas')
    st.info('12 escenarios × 5 repeticiones: oráculo simulado para evaluar alertas por NEGATIVIDAD y VOLUMEN. NO evalúa la exactitud del NLP ni la entrega real en 24 horas.')
    semilla=st.number_input('Semilla de simulación',min_value=1,max_value=2_000_000_000,value=20261018,step=1)
    if st.button('Ejecutar 60 escenarios-repetición',type='primary'):
        from uuid import uuid4
        from src.simulacion import ejecutar_bateria
        destino=Path(__file__).resolve().parent/'salida_pruebas' / uuid4().hex[:12]
        with st.spinner('Ejecutando y registrando las simulaciones...'):
            st.session_state['resultado_pruebas']=ejecutar_bateria(destino,repeticiones=5,semilla_base=int(semilla))
    if 'resultado_pruebas' in st.session_state:
        datos=st.session_state['resultado_pruebas']
        st.success(f"Se ejecutaron {datos['metricas']['ejecuciones_totales']} repeticiones de {datos['metricas']['escenarios']} escenarios")
        st.write('Métricas de la política, no del clasificador NLP')
        st.json(datos['metricas'],expanded=False)
        st.write('Media y desviación estándar por escenario')
        st.dataframe(datos['resumen'],width='stretch')
        volumen=[r for r in datos['resumen'] if r['id_escenario']=='E05'][0]
        st.info(f"Control E05 (solo volumen): media de alertas {volumen['alertas_media']:.2f} por ejecución. Este escenario permite comprobar el detector de volumen agregado en el Paso 4.")
        carpeta=Path(datos['directorio'])
        for nombre,titulo,mime in (
            ('resultados_ejecuciones.csv','Descargar ejecuciones CSV','text/csv'),
            ('resumen_por_escenario.csv','Descargar resumen CSV','text/csv'),
            ('metricas_politica.json','Descargar métricas JSON','application/json'),
            ('logs_escenarios.jsonl','Descargar logs JSONL','application/x-ndjson'),
            ('escenarios_configuracion.json','Descargar especificación de escenarios','application/json')):
            st.download_button(titulo,data=(carpeta/nombre).read_bytes(),file_name=nombre,mime=mime,key='descarga_'+nombre)
    st.caption('La batería conserva marcas de tiempo reales, pero no demuestra entrega automática dentro de 24 h desde el cierre semanal. Las reseñas y etiquetas de prueba son sintéticas.')

    st.divider()
    st.subheader('Comprobación temporal aislada (fechas simuladas)')
    st.caption('Evalúa una regla matemática de latencia desde el cierre semanal; NO crea programadores ni realiza entrega a un gerente.')
    if st.button('Ejecutar comprobación temporal'):
        from src.simulacion_temporal import ejecutar_pruebas_temporales
        carpeta_temporal=Path(__file__).resolve().parent/'salida_pruebas_temporales'
        st.session_state['pruebas_temporales']=ejecutar_pruebas_temporales(carpeta_temporal)
    if 'pruebas_temporales' in st.session_state:
        temporal=st.session_state['pruebas_temporales']
        st.dataframe(temporal['filas'],width='stretch')
        st.json(temporal['resumen'],expanded=False)
        st.download_button('Descargar escenarios temporales CSV',
          data=(Path(temporal['directorio'])/'resultados_temporales.csv').read_bytes(),
          file_name='resultados_temporales.csv',mime='text/csv')


with tab6:
    from src.automatizacion import semanas_pendientes, ejecutar_cierre_pendiente
    st.subheader('Cerrar automáticamente semanas vencidas')
    st.info('Este botón realiza una pasada de cierre de semanas ya terminadas (UTC). Para ejecución recurrente se requiere un programador EXTERNO, como el Programador de tareas de Windows. No envía correos y no garantiza un reporte dentro de 24 h.')
    pendientes=semanas_pendientes(agent)
    st.write('Semanas pendientes con reseñas:', pendientes if pendientes else 'Ninguna')
    if st.button('Comprobar y cerrar semanas vencidas',type='primary'):
        st.session_state['resultado_cierre']=ejecutar_cierre_pendiente(agent)
    if 'resultado_cierre' in st.session_state:
        resultado=st.session_state['resultado_cierre']
        st.json(resultado,expanded=True)
        if resultado['errores']:
            st.error('Una o más semanas no se pudieron cerrar. Revise el log.')
        else:
            st.success('Pasada completada y registrada.')
    bitacora=agent.carpeta/'cierres_automaticos.jsonl'
    if bitacora.exists():
        st.download_button('Descargar log de cierres JSONL',data=bitacora.read_bytes(),
                           file_name='cierres_automaticos.jsonl',mime='application/x-ndjson')
    st.caption('Solo se cierran semanas con reseñas. Los reportes quedan en SQLite y en el panel; una aplicación Streamlit abierta no sustituye un servicio programado.')
