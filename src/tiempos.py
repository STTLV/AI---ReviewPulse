"""Reloj y cálculo de plazos, no constituye entrega automática."""
from datetime import date, datetime, timedelta, timezone
import re

def fin_de_semana_iso_utc(semana: str) -> datetime:
    if not isinstance(semana,str) or not re.fullmatch(r'\d{4}-W\d{2}',semana):
        raise ValueError('Semana ISO inválida')
    try: lunes=date.fromisocalendar(int(semana[:4]),int(semana[-2:]),1)
    except ValueError as exc: raise ValueError('Semana ISO inexistente') from exc
    return datetime.combine(lunes+timedelta(days=7),datetime.min.time(),timezone.utc)

def _utc(valor):
    if isinstance(valor,str): valor=datetime.fromisoformat(valor.replace('Z','+00:00'))
    if not isinstance(valor,datetime) or valor.tzinfo is None or valor.utcoffset() is None:
        raise ValueError('Marca de tiempo sin zona horaria')
    return valor.astimezone(timezone.utc)

def evaluar_plazo(cierre,creado,umbral_horas=24):
    inicio=_utc(cierre)
    final=_utc(creado) if creado is not None else None
    if final is None: return {'plazo_horas':umbral_horas,'latencia_horas':None,'cumple':False,'estado':'entrega_ausente'}
    horas=(final-inicio).total_seconds()/3600
    valido=0<=horas<=umbral_horas
    return {'plazo_horas':umbral_horas,'latencia_horas':round(horas,6),
        'cumple':valido,'estado':'dentro_plazo' if valido else ('anterior_al_cierre' if horas<0 else 'fuera_plazo')}
