from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ReservaRequest(BaseModel):
    paciente_nombre: str = Field(..., min_length=2)
    paciente_email: str = Field(..., min_length=5)
    medico_id: int
    fecha: str       # Formato YYYY-MM-DD
    hora: str        # Formato HH:MM

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("La fecha debe tener el formato YYYY-MM-DD.") from exc
        return value

    @field_validator("hora")
    @classmethod
    def validar_hora(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("La hora debe tener el formato HH:MM.") from exc
        return value

class CitaResponse(BaseModel):
    id: int
    paciente_nombre: str
    paciente_email: str
    medico_id: int
    medico_nombre: str
    especialidad: str
    fecha: str
    hora: str
    estado: str
    notificacion_enviada: bool

class ExpedienteClinico(BaseModel):
    paciente_nombre: str
    tipo_sangre: str
    alergias: str
    antecedentes: str
    ultima_consulta: str