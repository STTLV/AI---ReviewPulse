import tempfile, unittest, json
from pathlib import Path
from src.agente import AgenteReviewPulse
from src.decision import Configuracion, evaluar_alerta
from src.modelo import clasificar, cargar_modelo


def clasificacion_fake(texto):
    es_negativo='NEGATIVA' in texto
    return {'temas_detectados':['servicio'],'sentimiento_por_tema':{'servicio':'negativo' if es_negativo else 'positivo'},
       'tema_principal':'servicio','polaridad_resumen':'negativo' if es_negativo else 'positivo',
       'tiene_senal_negativa':es_negativo,'estado':'un_tema'}

class PruebasReviewPulse(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.agente=AgenteReviewPulse(self.tmp.name,clasificador=clasificacion_fake)
    def tearDown(self):self.tmp.cleanup()
    def entrada(self,id,texto='Excelente servicio',fecha='2026-09-07'):
        return {'id':id,'texto':texto,'fecha':fecha,'plataforma':'simulador','estrellas':4}
    def test_rechazo_vacio(self):
        r=self.agente.procesar(self.entrada('A','  '))
        self.assertEqual(r['estado'],'rechazada')
        self.assertEqual(self.agente.memoria.conteo(),0)
    def test_rechazo_fecha(self):
        self.assertEqual(self.agente.procesar(self.entrada('A','bien','2026-99-99'))['estado'],'rechazada')
    def test_rechazo_calificacion(self):
        x=self.entrada('A');x['estrellas']=7
        self.assertEqual(self.agente.procesar(x)['estado'],'rechazada')
    def test_duplicado(self):
        self.assertEqual(self.agente.procesar(self.entrada('A'))['estado'],'aceptada')
        self.assertEqual(self.agente.procesar(self.entrada('A'))['estado'],'duplicada')
        self.assertEqual(self.agente.memoria.conteo(),1)
    def test_memoria_entre_instancias(self):
        self.agente.procesar(self.entrada('A'))
        nuevo=AgenteReviewPulse(self.tmp.name,clasificador=clasificacion_fake)
        self.assertEqual(nuevo.memoria.conteo(),1)
    def test_alerta_con_historial(self):
        for numero,fecha,texto in [(1,'2026-09-07','buena'),(2,'2026-09-14','buena'),(3,'2026-09-21','buena'),
                                   (4,'2026-09-28','NEGATIVA')]:
            for i in range(6):self.agente.procesar(self.entrada(f'{numero}-{i}',texto,fecha))
            r=self.agente.cerrar_semana(__import__('datetime').date.fromisoformat(fecha).strftime('%G-W%V'))
        self.assertTrue(r['reporte']['decision_alerta']['alertar'])
        self.assertEqual(len(self.agente.memoria.lista_alertas()),1)
    def test_historial_insuficiente_no_alerta(self):
        for i in range(6):self.agente.procesar(self.entrada(str(i),'NEGATIVA'))
        r=self.agente.cerrar_semana('2026-W37')
        self.assertFalse(r['reporte']['decision_alerta']['alertar'])
    def test_cierre_idempotente(self):
        self.agente.procesar(self.entrada('A'))
        r=self.agente.cerrar_semana('2026-W37')
        otra=self.agente.cerrar_semana('2026-W37')
        self.assertEqual(r['estado'],'cerrada')
        self.assertEqual(otra['estado'],'ya_cerrada')
        self.assertEqual(len(self.agente.memoria.lista_reportes()),1)
    def test_semana_cerrada_no_se_modifica(self):
        self.agente.procesar(self.entrada('A'))
        self.agente.cerrar_semana('2026-W37')
        r=self.agente.procesar(self.entrada('B'))
        self.assertEqual(r['estado'],'semana_cerrada')
        self.assertEqual(self.agente.memoria.conteo(),1)
    def test_no_crear_reporte_sin_resenas(self):
        self.assertEqual(self.agente.cerrar_semana('2026-W37')['estado'],'sin_resenas')
    def test_semana_iso_invalida(self):
        self.assertEqual(self.agente.cerrar_semana('2026-W99')['estado'],'semana_invalida')
    def test_logs_estructura(self):
        self.agente.procesar(self.entrada('A'))
        r=json.loads(self.agente.log.read_text(encoding='utf-8').splitlines()[0])
        self.assertTrue(all(k in r for k in ('timestamp_utc','percepcion','decision','accion')))
    def test_sin_alerta_variacion_baja(self):
        prev=[{'semana':'W1','proporcion_negativa':0.2},{'semana':'W2','proporcion_negativa':0.2}]
        resultado=evaluar_alerta({'total':10,'proporcion_negativa':0.25},prev,Configuracion())
        self.assertFalse(resultado['alertar'])
    def test_modelo_real_carga(self):
        paquete=cargar_modelo()
        self.assertEqual(set(paquete['modelos_tema']),{'limpieza','servicio','ubicacion','precio_valor'})
        p=clasificar('El servicio del hotel fue excelente y el personal muy amable.')
        self.assertIn(p['polaridad_resumen'], {'positivo','negativo','neutro_o_mixto','indeterminada'})

if __name__=='__main__':unittest.main()
