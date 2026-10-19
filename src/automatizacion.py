"""Cierre semanal reproducible ejecutable desde un proceso externo.

No es un servicio de correo ni garantiza la ejecución continua: el proceso
cron/Task Scheduler que lo invoque es responsable de ejecutarlo a tiempo.
Se usa UTC para el fin teórico de la semana ISO del prototipo.
"""
from datetime import datetime, timezone
from src.tiempos import fin_de_semana_iso_utc
from src.registro import registrar


def tiempo_utc(valor=None):
    if valor is None:
        return datetime.now(timezone.utc)
    if not isinstance(valor, datetime) or valor.tzinfo is None or valor.utcoffset() is None:
        raise ValueError('ahora_utc necesita datetime con zona horaria')
    return valor.astimezone(timezone.utc)


def semanas_pendientes(agente, ahora_utc=None):
    """Semanas con reseñas y sin reporte cuyo cierre UTC ya transcurrió."""
    ahora = tiempo_utc(ahora_utc)
    with agente.memoria.conexion() as con:
        filas = con.execute('''
            SELECT DISTINCT r.semana FROM resenas AS r
            LEFT JOIN reportes AS p ON p.semana = r.semana
            WHERE p.semana IS NULL ORDER BY r.semana
        ''').fetchall()
    pendientes = []
    for fila in filas:
        semana = fila['semana']
        try:
            cierre = fin_de_semana_iso_utc(semana)
        except ValueError:
            # Los datos normales son validados antes de guardarse. Un registro
            # heredado corrupto no debe hacer caer todas las demás semanas.
            continue
        if cierre <= ahora:
            pendientes.append(semana)
    return pendientes


def ejecutar_cierre_pendiente(agente, ahora_utc=None):
    """Procesa una sola pasada de semanas vencidas y deja evidencia JSONL."""
    ahora = tiempo_utc(ahora_utc)
    pendientes = semanas_pendientes(agente, ahora)
    resultados = []
    for semana in pendientes:
        try:
            salida = agente.cerrar_semana(semana)
        except Exception as exc:
            # El proceso de varias semanas continúa, pero no oculta el error.
            salida = {'estado':'error','semana':semana,'error':type(exc).__name__ + ': ' + str(exc)}
        resultados.append({'semana':semana,'estado':salida['estado'],
                           'plazo_reporte':salida.get('reporte',{}).get('plazo_reporte')})
    resumen = {'marca_comprobacion_utc':ahora.isoformat(),
               'semanas_pendientes':pendientes,
               'reportes_generados':sum(x['estado']=='cerrada' for x in resultados),
               'errores':sum(x['estado']=='error' for x in resultados),
               'resultados':resultados,
               'modo':'pasada_iniciada_por_usuario_o_proceso_externo',
               'correo_enviado':False,
               'garantia_24h':False}
    registrar(agente.carpeta/'cierres_automaticos.jsonl',
             {'semanas_candidatas':pendientes,'marca_comprobacion_utc':ahora.isoformat()},
             {'semanas_vencidas':len(pendientes)},
             {'tipo':'cierre_semanal_ejecutado','resumen':resumen})
    return resumen
