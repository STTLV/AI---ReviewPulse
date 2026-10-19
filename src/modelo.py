"""Inferencia sobre reseñas completas con artefacto Trip-MAML entrenado en Fase 1.

NO usa datos sintéticos para entrenar y NO alcanza por sí solo el SMART 85%.
La etiqueta 'neutro_o_mixto' es una agregación, no una etiqueta humana global.
"""
from functools import lru_cache
from pathlib import Path

MODELO_RUTA = Path(__file__).resolve().parents[1] / 'modelos' / 'modelos_multiaspecto.joblib'
NOMBRES_TEMAS = ('limpieza','servicio','ubicacion','precio_valor')

@lru_cache(maxsize=1)
def cargar_modelo():
    import joblib
    if not MODELO_RUTA.is_file():
        raise FileNotFoundError(f"No se encontró el modelo: {MODELO_RUTA}")
    # joblib.load solamente se utiliza con el artefacto propio incluido, nunca con subidas de usuario.
    paquete = joblib.load(MODELO_RUTA)
    if not all(k in paquete for k in ('modelos_tema','modelos_sentimiento')):
        raise ValueError('El modelo no tiene los componentes esperados')
    return paquete


def clasificar(texto: str) -> dict:
    paquete = cargar_modelo()
    pred = {}
    for tema in NOMBRES_TEMAS:
        presencia = int(paquete['modelos_tema'][tema].predict([texto])[0])
        if presencia:
            pred[tema] = str(paquete['modelos_sentimiento'][tema].predict([texto])[0])
    if not pred:
        global_pol = 'indeterminada'
    elif all(p == 'positivo' for p in pred.values()):
        global_pol = 'positivo'
    elif all(p == 'negativo' for p in pred.values()):
        global_pol = 'negativo'
    else:
        global_pol = 'neutro_o_mixto'
    return {'temas_detectados':list(pred), 'sentimiento_por_tema':pred,
            'tema_principal':next(iter(pred)) if len(pred)==1 else None,
            'polaridad_resumen':global_pol,
            'tiene_senal_negativa':any(p=='negativo' for p in pred.values()),
            'estado': 'sin_tema_detectado' if not pred else 'un_tema' if len(pred)==1 else 'varios_temas'}
