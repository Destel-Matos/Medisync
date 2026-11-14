# MediSync — Sistema de Gestión de Citas Médicas

Implementación funcional de **MediSync** bajo **Arquitectura Hexagonal (Puertos y Adaptadores)** con Python, FastAPI y SQLite.

## Arquitectura del Proyecto
* `domain/`: Modelos de datos y validación (`Pydantic`).
* `application/`: Puertos (`reserva_port.py`) y casos de uso (`servicio_citas.py`).
* `infrastructure/`: Adaptador de persistencia SQLite (`reserva_adapter.py`) con control de concurrencia e interfaz web multipantalla (`index.html`).
* `tests/`: Pruebas unitarias y de integración con `pytest`.

## Usuarios de Demostración (Clave: `1234`)
* **Paciente:** `paciente@medisync.com`
* **Médico:** `medico@medisync.com`
* **Administrador:** `admin@medisync.com`

## Ejecución Rápida
```bash
pip install -r requirements.txt
pytest -v
uvicorn main:app --host 0.0.0.0 --port 8000
