"""Decisión histórica por negatividad Y volumen.
Umbrales de piloto (hipótesis previas a pruebas Paso 4):
negatividad +30 puntos porcentuales; volumen >=100 % y >=10 reseñas extra.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Configuracion:
    aumento_umbral: float = 0.30
    minimo_resenas: int = 5
    minimo_semanas_historicas: int = 2
    semanas_de_referencia: int = 3
    aumento_volumen_relativo: float = 1.0
    aumento_volumen_absoluto: int = 10

    def __post_init__(self):
        if not isinstance(self.aumento_umbral,(int,float)) or not isfinite(self.aumento_umbral) or not 0<self.aumento_umbral<=1:
            raise ValueError('Umbral de negatividad inválido')
        if self.minimo_resenas < 1 or self.minimo_semanas_historicas < 1 or self.semanas_de_referencia < self.minimo_semanas_historicas:
            raise ValueError('Configuración de historial incoherente')
        if not isinstance(self.aumento_volumen_relativo,(int,float)) or not isfinite(self.aumento_volumen_relativo) or self.aumento_volumen_relativo <= 0:
            raise ValueError('Umbral relativo de volumen inválido')
        if not isinstance(self.aumento_volumen_absoluto,int) or self.aumento_volumen_absoluto < 1:
            raise ValueError('Umbral absoluto de volumen inválido')


def evaluar_alerta(actual, historico, config: Configuracion) -> dict:
    suficientes=len(historico)>=config.minimo_semanas_historicas
    referencia=sum(x['proporcion_negativa'] for x in historico)/len(historico) if historico else None
    delta=actual['proporcion_negativa']-referencia if referencia is not None else None
    vol=[x.get('total') for x in historico]
    comparable=(suficientes and bool(vol) and all(type(x) is int and x>=0 for x in vol))
    media=sum(vol)/len(vol) if comparable else None
    delta_abs=actual['total']-media if media is not None else None
    delta_rel=delta_abs/media if media and media>0 else None
    evaluable=actual['total']>=config.minimo_resenas and suficientes
    neg=bool(evaluable and delta is not None and delta>=config.aumento_umbral-1e-12)
    volumen=bool(evaluable and delta_rel is not None and delta_rel>=config.aumento_volumen_relativo-1e-12
                 and delta_abs>=config.aumento_volumen_absoluto-1e-12)
    tipos=(['negatividad'] if neg else []) + (['volumen'] if volumen else [])
    if not evaluable: razon='Muestra semanal insuficiente' if actual['total']<config.minimo_resenas else 'Historial insuficiente'
    elif neg and volumen: razon='Aumento significativo de negatividad y volumen'
    elif neg: razon='Aumento significativo de negatividad'
    elif volumen: razon='Aumento significativo del volumen de reseñas'
    else: razon='Variación inferior a los umbrales evaluables'
    return {'alertar':bool(tipos),'razon':razon,'tipos_anomalia':tipos,
      'alerta_por_negatividad':neg,'alerta_por_volumen':volumen,
      'referencia_historica':referencia,'incremento_proporcion':delta,
      'umbral_aumento':config.aumento_umbral,
      'referencia_volumen':media,'incremento_absoluto_volumen':delta_abs,
      'incremento_relativo_volumen':delta_rel,
      'umbral_volumen_relativo':config.aumento_volumen_relativo,
      'umbral_volumen_absoluto':config.aumento_volumen_absoluto,
      'semanas_referencia':[x['semana'] for x in historico],
      'volumen_evaluable':comparable}
