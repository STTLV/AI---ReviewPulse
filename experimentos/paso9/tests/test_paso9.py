import csv
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analizar_umbrales import cargar_predicciones, metricas, ejecutar

class PruebasPaso9(unittest.TestCase):
    def test_conteos(self):
        m = metricas([1, 0, 1, 0], [0.9, 0.8, 0.2, 0.1], 0.5)
        self.assertEqual([m[k] for k in ('tp','fp','fn','tn')],[1,1,1,1])
    def test_precision(self):
        self.assertEqual(metricas([1,0],[.9,.7],.8)['precision'],1.0)
    def test_recall(self):
        self.assertEqual(metricas([1,1],[.9,.1],.8)['recall'],.5)
    def test_f2(self):
        self.assertAlmostEqual(metricas([1,1,0],[.9,.1,.8],.5)['f2'], 5*.5*.5/(4*.5+.5))
    def test_sin_predicciones_positivas(self):
        self.assertIsNone(metricas([0,1],[.1,.2],.9)['fraccion_predicciones_positivas_falsas'])
    def test_datos_desalineados(self):
        with self.assertRaises(ValueError): metricas([1,0],[.2],.5)
    def test_csv_duplicados(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'dup.csv'
            p.write_text('modelo,review_id,real_contiene_critica,probabilidad,pliegue\nx,1,0,0.1,1\nx,1,1,0.4,2\n',encoding='utf-8')
            with self.assertRaises(ValueError): cargar_predicciones(p)
    def test_ejecucion_archivos(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv'
            with p.open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f); w.writerow(['modelo','review_id','real_contiene_critica','probabilidad','pliegue'])
                w.writerows([['resena_palabras','1','1','0.45','1'],['resena_palabras','2','0','0.40','1']])
            resultados=ejecutar(p,Path(d)/'out')
            self.assertEqual(len(resultados),7)
            self.assertTrue((Path(d)/'out'/'resumen.json').is_file())
    def test_monotonico_recall(self):
        y=[1,0,1,1]; scores=[.1,.5,.4,.9]
        self.assertGreaterEqual(metricas(y,scores,.3)['recall'],metricas(y,scores,.7)['recall'])

if __name__=='__main__': unittest.main()
