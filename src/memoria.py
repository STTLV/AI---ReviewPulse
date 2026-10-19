"""Estado interno persistente y acciones del hotel piloto."""
import json, sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections import Counter
from src.registro import instante_utc

class Memoria:
    def __init__(self, ruta):
        self.ruta=Path(ruta)
        self.ruta.parent.mkdir(parents=True,exist_ok=True)
        self._preparar()
    @contextmanager
    def conexion(self):
        con=sqlite3.connect(self.ruta)
        con.row_factory=sqlite3.Row
        try:
            with con:
                yield con
        finally:
            con.close()
    def _preparar(self):
        with self.conexion() as con:
            con.executescript("""
             CREATE TABLE IF NOT EXISTS resenas (
                id TEXT PRIMARY KEY, fecha TEXT NOT NULL, semana TEXT NOT NULL,
                plataforma TEXT NOT NULL, texto TEXT NOT NULL, estrellas REAL,
                clasificacion_json TEXT NOT NULL, senal_negativa INTEGER NOT NULL,
                procesado_utc TEXT NOT NULL);
             CREATE INDEX IF NOT EXISTS idx_semana ON resenas(semana);
             CREATE TABLE IF NOT EXISTS reportes (
                semana TEXT PRIMARY KEY, reporte_json TEXT NOT NULL, creado_utc TEXT NOT NULL);
             CREATE TABLE IF NOT EXISTS alertas (
                semana TEXT PRIMARY KEY, descripcion TEXT NOT NULL, creado_utc TEXT NOT NULL);
            """)
    def existe(self, rid):
        with self.conexion() as con:
            return con.execute('SELECT 1 FROM resenas WHERE id=?',(rid,)).fetchone() is not None
    def guardar_resena(self, r, pred):
        with self.conexion() as con:
            con.execute("""INSERT INTO resenas(id,fecha,semana,plataforma,texto,estrellas,clasificacion_json,senal_negativa,procesado_utc)
              VALUES(?,?,?,?,?,?,?,?,?)""", (r['id'],r['fecha'],r['semana'],r['plataforma'],r['texto'],r['estrellas'],
                       json.dumps(pred,ensure_ascii=False),int(pred['tiene_senal_negativa']),instante_utc()))
    def datos_semana(self,semana):
        with self.conexion() as con:
            filas=con.execute('SELECT clasificacion_json, senal_negativa FROM resenas WHERE semana=?',(semana,)).fetchall()
        temas=Counter()
        for f in filas:
            temas.update(json.loads(f['clasificacion_json'])['temas_detectados'])
        negativas=sum(r['senal_negativa'] for r in filas)
        return {'semana':semana, 'total':len(filas),'con_senal_negativa':negativas,
                'proporcion_negativa':negativas/len(filas) if filas else 0.0, 'temas':dict(temas)}
    def semanas_previas(self,semana,max_semanas=3):
        with self.conexion() as con:
            semanas=[r[0] for r in con.execute("SELECT DISTINCT semana FROM resenas WHERE semana < ? ORDER BY semana DESC LIMIT ?",
                (semana,max_semanas)).fetchall()]
        return [self.datos_semana(s) for s in semanas]
    def guardar_reporte(self,semana,reporte):
        with self.conexion() as con:
            con.execute('INSERT INTO reportes(semana,reporte_json,creado_utc) VALUES(?,?,?)',
                        (semana,json.dumps(reporte,ensure_ascii=False),instante_utc()))
    def obtener_reporte(self,semana):
        with self.conexion() as con:
            r=con.execute('SELECT reporte_json FROM reportes WHERE semana=?',(semana,)).fetchone()
        return json.loads(r[0]) if r else None
    def guardar_alerta(self,semana,descripcion):
        with self.conexion() as con:
            con.execute('INSERT INTO alertas(semana,descripcion,creado_utc) VALUES(?,?,?)',(semana,descripcion,instante_utc()))
    def lista_reportes(self):
        with self.conexion() as con:
            filas=con.execute('SELECT reporte_json FROM reportes ORDER BY semana DESC').fetchall()
        return [json.loads(f[0]) for f in filas]
    def lista_alertas(self):
        with self.conexion() as con:
            return [dict(f) for f in con.execute('SELECT * FROM alertas ORDER BY semana DESC').fetchall()]
    def conteo(self):
        with self.conexion() as con:
            return con.execute('SELECT COUNT(*) FROM resenas').fetchone()[0]
