"""Verifica estructura e integridad del modelo local sin deserializar .joblib."""
from pathlib import Path
from hashlib import sha256
from importlib import metadata
import re
import sys

BASE = Path(__file__).resolve().parent
OBLIGATORIOS = (
    'app.py','requirements.txt','src/agente.py','src/modelo.py',
    'src/memoria.py','src/decision.py','src/automatizacion.py',
    'datos/resenas_sinteticas.csv','modelos/modelos_multiaspecto.joblib',
    'modelos/SHA256.txt','tests/test_agente.py',
    'ejecutar_demo.py','ejecutar_pruebas_escenarios.py',
    'experimentos/paso8/entrenar_quejas.py','experimentos/paso9/analizar_umbrales.py',
)

def verificar():
    faltantes = [f for f in OBLIGATORIOS if not (BASE / f).is_file()]
    ruta = BASE / 'modelos/modelos_multiaspecto.joblib'
    checksum_file = BASE / 'modelos/SHA256.txt'
    registrado = checksum_file.read_text(encoding='utf-8').split()[0].lower() if checksum_file.exists() else ''
    real = sha256(ruta.read_bytes()).hexdigest() if ruta.exists() else ''
    valid_hash = bool(re.fullmatch(r'[0-9a-f]{64}', registrado)) and registrado == real
    print('REVIEWPULSE: VERIFICACIÓN DE ESTRUCTURA Y SHA-256')
    print('Python:',sys.version.split()[0])
    for paquete in ('scikit-learn','numpy','scipy','joblib','streamlit'):
        try: valor=metadata.version(paquete)
        except metadata.PackageNotFoundError: valor='NO INSTALADO'
        print(paquete+':',valor)
    print('Archivos obligatorios:', 'OK' if not faltantes else f'FALTAN: {faltantes}')
    print('Integridad del modelo SHA-256:', 'OK' if valid_hash else 'NO COINCIDE')
    print('NOTA: No se evalúan aquí exactitud del modelo, plazos SMART ni entrega externa.')
    return 0 if not faltantes and valid_hash else 1

if __name__=='__main__':
    raise SystemExit(verificar())
