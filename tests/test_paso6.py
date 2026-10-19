import unittest
from collections import Counter
from src.evaluacion_real import convertir, evaluar, agregar_sentimiento, recuperar_texto

class PruebasPaso6(unittest.TestCase):
    def test_palabras_tokenizadas(self):
        self.assertEqual(recuperar_texto('Hola//hola/0.0 mundo/n/mundo/0.0 !//!/0.0'),'Hola mundo!')
    def test_sentimiento_agregado_solo_positivo(self):
        self.assertEqual(agregar_sentimiento(Counter({'p':2})), 'positivo')
    def test_sentimiento_agregado_mezcla(self):
        self.assertEqual(agregar_sentimiento(Counter({'p':1,'n':1})), 'neutro_o_mixto')
    def test_neutral_x_es_mixto(self):
        self.assertEqual(agregar_sentimiento(Counter({'x':1})), 'neutro_o_mixto')
    def test_validacion_alineacion(self):
        with self.assertRaises(ValueError): convertir({'segments':['a','b'],'segmentLabels':[{}], 'reviewId':1})
    def test_referencia_preserva_varios_temas(self):
        v=convertir({'reviewId':'abc','segments':['buen/a/bueno/0','sucio/a/sucio/0'],
                      'segmentLabels':[{'SERVICE':'p'},{'CLEANLINESS':'n'}]})
        self.assertEqual(v['referencia_por_tema'],{'limpieza':'negativo','servicio':'positivo'})
    def test_metricas_no_mezclan_tema_y_sentimiento(self):
        casos=[{'id':'1','texto':'bueno','referencia_por_tema':{'servicio':'positivo'}}]
        def pred(_):
            return {'sentimiento_por_tema':{'servicio':'negativo'},'tiene_senal_negativa':True}
        m,r=evaluar(casos,pred)
        self.assertEqual(m['exactitud_temas_conjunto'],1)
        self.assertEqual(m['exactitud_estricta_temas_y_sentimientos'],0)
        self.assertFalse(m['cumple_85_estricto'])
    def test_tema_ausente_no_es_error_si_verdad_vacia(self):
        casos=[{'id':'2','texto':'sin tema','referencia_por_tema':{}}]
        m,_=evaluar(casos,lambda _: {'sentimiento_por_tema':{},'tiene_senal_negativa':False})
        self.assertEqual(m['exactitud_estricta_temas_y_sentimientos'],1)
        self.assertIsNone(m['acierto_polaridad_para_aspectos_reales'])

if __name__=='__main__': unittest.main()
