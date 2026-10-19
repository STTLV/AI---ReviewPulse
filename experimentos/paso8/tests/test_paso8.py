import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from entrenar_quejas import etiqueta_critica, calcular_metricas, grupos_sin_texto_duplicado, pipeline

class TestPaso8(unittest.TestCase):
    def test_critica_en_tema_objetivo(self):
        self.assertEqual(etiqueta_critica({'SERVICE':'n'}),1)
    def test_negativo_fuera_del_alcance(self):
        self.assertEqual(etiqueta_critica({'FOOD':'n','SERVICE':'p'}),0)
    def test_neutro_mixto_no_equivale_a_queja(self):
        self.assertEqual(etiqueta_critica({'SERVICE':'x'}),0)
    def test_etiqueta_negativa_en_multiple_temas(self):
        self.assertEqual(etiqueta_critica({'CLEANLINESS':'p','VALUE':'n'}),1)
    def test_denom_alertas_falsas(self):
        m=calcular_metricas([1,1,0,0],[1,0,1,0])
        self.assertEqual((m['tp'],m['fp'],m['fn'],m['tn']),(1,1,1,1))
        self.assertEqual(m['fraccion_alertas_falsas'],0.5)
    def test_sin_alertas_regresa_nulo(self):
        self.assertIsNone(calcular_metricas([0],[0])['fraccion_alertas_falsas'])
    def test_duplicado_largo_unifica_grupos(self):
        rows=[{'segmentos':['Esta es una frase suficientemente extensa duplicada']},
              {'segmentos':['Esta es una frase suficientemente extensa duplicada']},
              {'segmentos':['Texto original de ejemplo que no coincide']}]
        g=grupos_sin_texto_duplicado(rows)
        self.assertEqual(g[0],g[1]);self.assertNotEqual(g[1],g[2])
    def test_modelos_conocidos(self):
        self.assertEqual(pipeline('resena_palabras').steps[0][0],'tfidf')
        with self.assertRaises(ValueError):pipeline('modelo_inventado')

if __name__=='__main__':unittest.main()
