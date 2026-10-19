import tempfile, unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
from src.decision import evaluar_alerta,Configuracion
from src.tiempos import fin_de_semana_iso_utc,evaluar_plazo
from src.simulacion import ESCENARIOS,ejecutar_escenario
from src.simulacion_temporal import ejecutar_pruebas_temporales

class PruebasPaso4(unittest.TestCase):
    def setUp(self):
        self.c=Configuracion()
        self.h=[{'semana':'W1','total':12,'proporcion_negativa':0.1},{'semana':'W2','total':12,'proporcion_negativa':0.1},{'semana':'W3','total':12,'proporcion_negativa':0.1}]
    def test_detecta_volumen_sin_negatividad(self):
        d=evaluar_alerta({'total':64,'proporcion_negativa':0.1},self.h,self.c)
        self.assertTrue(d['alertar']);self.assertEqual(d['tipos_anomalia'],['volumen'])
    def test_incremento_no_supera_umbral(self):
        d=evaluar_alerta({'total':23,'proporcion_negativa':0.1},self.h,self.c)
        self.assertFalse(d['alertar'])
    def test_ambas_anomalias_no_doble_alerta(self):
        d=evaluar_alerta({'total':64,'proporcion_negativa':0.8},self.h,self.c)
        self.assertTrue(d['alertar']);self.assertEqual(d['tipos_anomalia'],['negatividad','volumen'])
    def test_sin_referencia_volumen_conserva_negatividad(self):
        d=evaluar_alerta({'total':15,'proporcion_negativa':0.9},[{'semana':'A','proporcion_negativa':0.1},{'semana':'B','proporcion_negativa':0.1}],self.c)
        self.assertTrue(d['alertar']);self.assertFalse(d['alerta_por_volumen'])
    def test_e05_corregido(self):
        fila,_=ejecutar_escenario(ESCENARIOS[4],1,20265001)
        self.assertEqual(fila['alertas_emitidas'],1)
    def test_cierre_utc_semana_iso(self):
        self.assertEqual(fin_de_semana_iso_utc('2026-W40').isoformat(),'2026-10-05T00:00:00+00:00')
    def test_regla_24h_borde(self):
        f=fin_de_semana_iso_utc('2026-W40')
        self.assertTrue(evaluar_plazo(f,f+timedelta(hours=24))['cumple'])
        self.assertFalse(evaluar_plazo(f,f+timedelta(hours=24,seconds=1))['cumple'])
        self.assertFalse(evaluar_plazo(f,f-timedelta(seconds=1))['cumple'])
    def test_sin_entrega_temporal(self):
        f=fin_de_semana_iso_utc('2026-W40')
        self.assertEqual(evaluar_plazo(f,None)['estado'],'entrega_ausente')
    def test_plazo_rechaza_fecha_sin_tz(self):
        with self.assertRaises(ValueError): evaluar_plazo(datetime(2026,10,5),datetime.now(timezone.utc))
    def test_reproduce_escenarios_temporales(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=ejecutar_pruebas_temporales(tmp)
            self.assertEqual(r['resumen']['verificaciones_correctas'],6)
            self.assertTrue((Path(tmp)/'resultados_temporales.csv').is_file())
    def test_rechaza_configuracion_volumen_invalida(self):
        with self.assertRaises(ValueError): Configuracion(aumento_volumen_relativo=0)

if __name__=='__main__':unittest.main()
