import sqlite3
from typing import List, Dict, Any, Optional
from application.ports.reserva_port import ReservaPort

class SQLiteReservaAdapter(ReservaPort):
    def __init__(self, db_path: str = "medisync.db"):
        self.db_path = db_path
        self._inicializar_bd()

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_bd(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS medicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    especialidad TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS citas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_nombre TEXT NOT NULL,
                    paciente_email TEXT NOT NULL,
                    medico_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    estado TEXT DEFAULT 'CONFIRMADA',
                    FOREIGN KEY (medico_id) REFERENCES medicos(id),
                    UNIQUE(medico_id, fecha, hora)
                );

                CREATE TABLE IF NOT EXISTS expedientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_nombre TEXT UNIQUE NOT NULL,
                    tipo_sangre TEXT NOT NULL,
                    alergias TEXT NOT NULL,
                    antecedentes TEXT NOT NULL,
                    ultima_consulta TEXT NOT NULL
                );
            """)

            # Datos semilla iniciales
            cursor.execute("SELECT COUNT(*) FROM medicos")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    "INSERT INTO medicos (nombre, especialidad) VALUES (?, ?)",
                    [
                        ("Dra. Laura Méndez", "Cardiología"),
                        ("Dr. Carlos Gómez", "Pediatría"),
                        ("Dra. Ana Sofía Reyes", "Medicina General"),
                        ("Dr. Roberto Santana", "Dermatología")
                    ]
                )

            cursor.execute("SELECT COUNT(*) FROM expedientes")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    "INSERT INTO expedientes (paciente_nombre, tipo_sangre, alergias, antecedentes, ultima_consulta) VALUES (?, ?, ?, ?, ?)",
                    [
                        ("Juan Pérez", "O+", "Penicilina", "Hipertensión leve controlada", "2026-09-12 - Chequeo general estable"),
                        ("María Rodríguez", "A+", "Ninguna conocida", "Asma estacional en infancia", "2026-10-03 - Evaluación preventiva sin hallazgos")
                    ]
                )
            conn.commit()

    def listar_medicos(self, especialidad: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            if especialidad:
                rows = conn.execute("SELECT * FROM medicos WHERE especialidad = ?", (especialidad,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM medicos").fetchall()
            return [dict(r) for r in rows]

    def obtener_horarios_ocupados(self, medico_id: int, fecha: str) -> List[str]:
        with self._conectar() as conn:
            rows = conn.execute(
                "SELECT hora FROM citas WHERE medico_id = ? AND fecha = ? AND estado = 'CONFIRMADA'",
                (medico_id, fecha)
            ).fetchall()
            return [r["hora"] for r in rows]

    def guardar_cita(self, paciente_nombre: str, paciente_email: str, medico_id: int, fecha: str, hora: str) -> Dict[str, Any]:
        with self._conectar() as conn:
            try:
                cursor = conn.execute(
                    """INSERT INTO citas (paciente_nombre, paciente_email, medico_id, fecha, hora)
                       VALUES (?, ?, ?, ?, ?)""",
                    (paciente_nombre, paciente_email, medico_id, fecha, hora)
                )
                cita_id = cursor.lastrowid
                conn.commit()

                row = conn.execute(
                    """SELECT c.id, c.paciente_nombre, c.paciente_email, c.medico_id,
                              m.nombre AS medico_nombre, m.especialidad, c.fecha, c.hora, c.estado
                       FROM citas c
                       JOIN medicos m ON c.medico_id = m.id
                       WHERE c.id = ?""",
                    (cita_id,)
                ).fetchone()
                return dict(row)
            except sqlite3.IntegrityError:
                raise ValueError("Error de integridad (RNF-03): Ya existe una cita registrada para este médico, fecha y hora.")

    def listar_citas(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            rows = conn.execute(
                """SELECT c.id, c.paciente_nombre, c.paciente_email, c.medico_id,
                          m.nombre AS medico_nombre, m.especialidad, c.fecha, c.hora, c.estado
                   FROM citas c
                   JOIN medicos m ON c.medico_id = m.id
                   ORDER BY c.fecha DESC, c.hora ASC"""
            ).fetchall()
            return [dict(r) for r in rows]

    def consultar_expediente(self, paciente_nombre: str) -> Optional[Dict[str, Any]]:
        with self._conectar() as conn:
            row = conn.execute(
                "SELECT * FROM expedientes WHERE LOWER(paciente_nombre) LIKE LOWER(?)",
                (f"%{paciente_nombre.strip()}%",)
            ).fetchone()
            return dict(row) if row else None