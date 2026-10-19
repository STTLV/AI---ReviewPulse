"""Percepciones del hotel piloto; los conectores externos NO están implementados."""
from datetime import date
from uuid import uuid4

class EntradaInvalida(ValueError):
    pass

FUENTES = {"simulador", "formulario", "archivo"}

def validar_resena(datos: dict) -> dict:
    if not isinstance(datos, dict):
        raise EntradaInvalida("Se esperaba una reseña como diccionario")
    texto = datos.get("texto")
    if not isinstance(texto, str) or not texto.strip():
        raise EntradaInvalida("El texto de la reseña no puede estar vacío")
    if len(texto.strip()) > 10000:
        raise EntradaInvalida("La reseña supera 10.000 caracteres")
    fecha_str = datos.get("fecha")
    try:
        if not isinstance(fecha_str, str):
            raise ValueError("Fecha no es texto")
        fecha = date.fromisoformat(fecha_str)
        if fecha.isoformat() != fecha_str:
            raise ValueError("Formato ambiguo")
    except ValueError as exc:
        raise EntradaInvalida("Fecha inválida: utilice AAAA-MM-DD") from exc
    fuente = str(datos.get("plataforma", "")).lower().strip()
    if fuente not in FUENTES:
        raise EntradaInvalida("Origen inválido: simulador, formulario o archivo")
    calificacion = datos.get("estrellas")
    if calificacion in ("", None):
        calificacion = None
    else:
        try:
            valor = float(calificacion)
        except (TypeError,ValueError) as exc:
            raise EntradaInvalida("Calificación numérica inválida") from exc
        if valor < 1 or valor > 5:
            raise EntradaInvalida("Las estrellas deben estar entre 1 y 5")
        calificacion = valor
    identificador = str(datos.get("id") or f"R-{uuid4().hex[:12]}").strip()
    if not identificador or len(identificador)>80:
        raise EntradaInvalida("ID inválido")
    anyo, semana, _ = fecha.isocalendar()
    return {"id":identificador, "fecha":fecha.isoformat(), "semana":f"{anyo}-W{semana:02d}",
            "texto":texto.strip(), "plataforma":fuente, "estrellas":calificacion}
