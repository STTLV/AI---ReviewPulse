"""Bitácora JSONL de ejecuciones: percepción, decisión, acción y UTC."""
import json
from datetime import datetime,timezone
from pathlib import Path

def instante_utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')

def registrar(path: Path, percepcion: dict, decision: dict, accion: dict):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    entrada={'timestamp_utc':instante_utc(),'percepcion':percepcion,
             'decision':decision,'accion':accion}
    with path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(entrada,ensure_ascii=False,default=str)+'\n')
    return entrada
