from fastapi import FastAPI, HTTPException, Header, Query, status
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Optional

from domain.models import ReservaRequest
from application.services.servicio_citas import ServicioCitas
from infrastructure.adapters.reserva_adapter import SQLiteReservaAdapter

app = FastAPI(title="MediSync API", version="0.1.0-academic")

# Inyección de dependencias (Arquitectura Hexagonal)
adapter = SQLiteReservaAdapter("medisync.db")
servicio = ServicioCitas(adapter)

@app.get("/", response_class=HTMLResponse)
def servir_interfaz():
    html_path = Path("infrastructure/web/index.html")
    return html_path.read_text(encoding="utf-8")

@app.get("/api/medicos")
def get_medicos(especialidad: Optional[str] = None):
    return servicio.obtener_medicos(especialidad)

@app.get("/api/citas/disponibilidad")
def get_disponibilidad(medico_id: int = Query(...), fecha: str = Query(...)):
    horarios = servicio.consultar_disponibilidad(medico_id, fecha)
    return {"medico_id": medico_id, "fecha": fecha, "horarios_disponibles": horarios}

@app.post("/api/citas/reservar", status_code=status.HTTP_201_CREATED)
def post_reservar_cita(datos: ReservaRequest):
    try:
        return servicio.agendar_cita(datos)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.get("/api/citas")
def get_citas():
    return servicio.obtener_todas_las_citas()

@app.get("/api/expedientes/{paciente_nombre}")
def get_expediente(paciente_nombre: str, x_rol: str = Header(default="PACIENTE")):
    try:
        return servicio.obtener_expediente(paciente_nombre, x_rol.upper())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))