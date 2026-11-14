from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ReservaPort(ABC):
    @abstractmethod
    def listar_medicos(self, especialidad: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def obtener_horarios_ocupados(self, medico_id: int, fecha: str) -> List[str]:
        pass

    @abstractmethod
    def guardar_cita(self, paciente_nombre: str, paciente_email: str, medico_id: int, fecha: str, hora: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def listar_citas(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def consultar_expediente(self, paciente_nombre: str) -> Optional[Dict[str, Any]]:
        pass