"""Pruebas del cierre automático, sin utilizar fuentes externas ni alterar datos reales."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from src.agente import AgenteReviewPulse
from src.automatizacion import tiempo_utc, semanas_pendientes, ejecutar_cierre_pendiente
from src.tiempos import fin_de_semana_iso_utc


def clasificador_falso(_):
    return {'temas_detectados':['servicio'], 'sentimiento_por_tema':{'servicio':'positivo'},
            'tema_principal':'servicio','polaridad_resumen':'positivo',
            'tiene_senal_negativa':False,'estado':'un_tema'}

class PruebasCierreProgramado(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.agente=AgenteReviewPulse(Path(self.temp.name)/'evidencia',clasificador=clasificador_falso)

    def guardar(self, semana, ident):
        lunes=datetime.fromisocalendar(int(semana[:4]),int(semana[-2:]),1).date()
        salida=self.agente.procesar({'id':ident,'texto':'Servicio excelente','fecha':lunes.isoformat(),
                                     'plataforma':'simulador','estrellas':5})
        self.assertEqual(salida['estado'],'aceptada')

    def test_no_ejecutar_semana_aun_abierta(self):
        semana='2032-W01'
        self.guardar(semana,'futuro')
        salida=ejecutar_cierre_pendiente(self.agente,datetime(2026,10,18,tzinfo=timezone.utc))
        self.assertEqual(salida['reportes_generados'],0)
        self.assertIsNone(self.agente.memoria.obtener_reporte(semana))

    def test_cerrar_semana_vencida_y_persistir(self):
        semana='2020-W08'
        self.guardar(semana,'pasado')
        salida=ejecutar_cierre_pendiente(self.agente,datetime(2026,10,18,tzinfo=timezone.utc))
        self.assertEqual(salida['reportes_generados'],1)
        self.assertIsNotNone(self.agente.memoria.obtener_reporte(semana))
        self.assertTrue((self.agente.carpeta/'cierres_automaticos.jsonl').exists())

    def test_idempotencia_segunda_pasada(self):
        semana='2020-W09'
        self.guardar(semana,'cierre_unico')
        primero=ejecutar_cierre_pendiente(self.agente)
        segundo=ejecutar_cierre_pendiente(self.agente)
        self.assertEqual(primero['reportes_generados'],1)
        self.assertEqual(segundo['reportes_generados'],0)
        self.assertEqual(len(self.agente.memoria.lista_reportes()),1)

    def test_filtro_respeta_cierre_utc(self):
        semana='2020-W09'
        self.guardar(semana,'lindero')
        fin=fin_de_semana_iso_utc(semana)
        self.assertNotIn(semana,semanas_pendientes(self.agente,fin-timedelta(microseconds=1)))
        self.assertIn(semana,semanas_pendientes(self.agente,fin))

    def test_exige_zona_horaria(self):
        with self.assertRaises(ValueError):
            tiempo_utc(datetime(2026,10,18))

    def test_reporte_sigue_siendo_panel_sin_envio_externo(self):
        self.guardar('2020-W10','solo_panel')
        resumen=ejecutar_cierre_pendiente(self.agente)
        self.assertFalse(resumen['correo_enviado'])
        self.assertFalse(resumen['garantia_24h'])
        reporte=self.agente.memoria.obtener_reporte('2020-W10')
        self.assertEqual(reporte['plazo_notificacion_externa'],'NO_IMPLEMENTADO')

    def test_bitacora_tiene_percepcion_decision_accion(self):
        self.guardar('2020-W11','log_cli')
        ejecutar_cierre_pendiente(self.agente)
        entradas=(self.agente.carpeta/'cierres_automaticos.jsonl').read_text(encoding='utf8').splitlines()
        ultima=json.loads(entradas[-1])
        self.assertTrue(all(k in ultima for k in ('timestamp_utc','percepcion','decision','accion')))

if __name__=='__main__': unittest.main()
