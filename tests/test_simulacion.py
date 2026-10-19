import json
import tempfile
import unittest
from pathlib import Path
from src.simulacion import (ESCENARIOS,clasificador_controlado,
    ejecutar_escenario,ejecutar_bateria,calcular_metricas,resumen_por_escenario)

class TestSimulacion(unittest.TestCase):
    def test_minimo_escenarios_y_fallos(self):
        self.assertGreaterEqual(len(ESCENARIOS),10)
        self.assertGreaterEqual(sum(s.tipo=='fallo_esperado' for s in ESCENARIOS),2)
    def test_clasificador_controlado(self):
        self.assertTrue(clasificador_controlado('[NEGATIVA_SIMULADA] algo')['tiene_senal_negativa'])
        self.assertFalse(clasificador_controlado('[POSITIVA_SIMULADA] algo')['tiene_senal_negativa'])
    def test_repetibilidad_semilla(self):
        esc=ESCENARIOS[1]
        f1,_=ejecutar_escenario(esc,1,12345)
        f2,_=ejecutar_escenario(esc,1,12345)
        for clave in ('numero_resenas_actual','proporcion_negativa_observada','alertas_emitidas'):
            self.assertEqual(f1[clave],f2[clave])
    def test_excepcion_texto(self):
        fila,registros=ejecutar_escenario(ESCENARIOS[8],1,12)
        self.assertEqual(fila['rechazos'],1)
        self.assertTrue(any(x['accion']['tipo']=='abstenerse' for x in registros))
    def test_excepcion_fecha(self):
        fila,_=ejecutar_escenario(ESCENARIOS[9],1,12)
        self.assertEqual(fila['rechazos'],1)
    def test_caso_duplicado(self):
        fila,_=ejecutar_escenario(ESCENARIOS[10],1,12)
        self.assertEqual(fila['duplicados'],1)
    def test_limite_menos_de_cinco_reseñas(self):
        fila,_=ejecutar_escenario(ESCENARIOS[6],1,12)
        self.assertEqual(fila['alertas_emitidas'],0)
    def test_no_division_por_cero_sin_alertas(self):
        datos=[{'id_escenario':'Z','tipo':'normal','evaluable_alertas':True,
                'anomalia_real':False,'alertas_emitidas':0,'respuesta_controlada_correcta':True}]
        m=calcular_metricas(datos)
        self.assertIsNone(m['proporcion_alertas_falsas'])
    def test_outputs_bateria(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=ejecutar_bateria(tmp)
            self.assertEqual(len(r['filas']),len(ESCENARIOS)*5)
            self.assertEqual(r['metricas']['repeticiones_por_escenario'],5)
            for archivo in ('resultados_ejecuciones.csv','resumen_por_escenario.csv',
                'metricas_politica.json','logs_escenarios.jsonl','escenarios_configuracion.json'):
                self.assertTrue((Path(tmp)/archivo).is_file())
            self.assertEqual(r['metricas']['evaluacion_exactitud_NLP'],'NO_REALIZADA')
            self.assertEqual(len(r['resumen']),len(ESCENARIOS))

if __name__=='__main__':unittest.main()
