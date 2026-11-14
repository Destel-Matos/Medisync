from typing import List, Dict, Any, Optional
from application.ports.reserva_port import ReservaPort
from domain.models import ReservaRequest

HORARIOS_BASE = ["08:00", "09:00", "10:30", "11:30", "14:00", "15:30", "16:30"]

class ServicioCitas:
    def __init__(self, reserva_port: ReservaPort):
        self.reserva_port = reserva_port

    def obtener_medicos(self, especialidad: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.reserva_port.listar_medicos(especialidad)

    def consultar_disponibilidad(self, medico_id: int, fecha: str) -> List[str]:
        ocupados = self.reserva_port.obtener_horarios_ocupados(medico_id, fecha)
        return [h for h in HORARIOS_BASE if h not in ocupados]

    def agendar_cita(self, datos: ReservaRequest) -> Dict[str, Any]:
        if datos.hora not in HORARIOS_BASE:
            raise ValueError("El horario seleccionado no pertenece a la jornada médica.")

        disponibles = self.consultar_disponibilidad(datos.medico_id, datos.fecha)
        if datos.hora not in disponibles:
            raise ValueError("Conflicto de concurrencia: el horario ya no está disponible.")

        cita = self.reserva_port.guardar_cita(
            paciente_nombre=datos.paciente_nombre,
            paciente_email=datos.paciente_email,
            medico_id=datos.medico_id,
            fecha=datos.fecha,
            hora=datos.hora
        )

        # Contingencia R-01: Registro de notificación automática (Mock Service)
        print(f"[NOTIFICACIÓN EMAIL -> {datos.paciente_email}] Cita #{cita['id']} confirmada con {cita['medico_nombre']} el {datos.fecha} a las {datos.hora}.")
        cita["notificacion_enviada"] = True
        return cita

    def obtener_todas_las_citas(self) -> List[Dict[str, Any]]:
        return self.reserva_port.listar_citas()

    def obtener_expediente(self, paciente_nombre: str, rol: str) -> Dict[str, Any]:
        if rol not in ("MEDICO", "ADMIN"):
            raise PermissionError("Acceso denegado (RF-02/RF-03): Solo personal médico autorizado puede consultar expedientes clínicos.")
        
        expediente = self.reserva_port.consultar_expediente(paciente_nombre)
        if not expediente:
            raise LookupError(f"No se encontró expediente clínico para '{paciente_nombre}'.")
        return expediente