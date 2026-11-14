import pytest
from fastapi.testclient import TestClient
from infrastructure.adapters.reserva_adapter import SQLiteReservaAdapter
from application.services.servicio_citas import ServicioCitas
import main

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_medisync.db"
    test_adapter = SQLiteReservaAdapter(str(db_file))
    main.adapter = test_adapter
    main.servicio = ServicioCitas(test_adapter)

client = TestClient(main.app)

def test_flujo_reserva_y_prevencion_duplicados():
    # 1. Consultar disponibilidad inicial
    resp_disp = client.get("/api/citas/disponibilidad?medico_id=1&fecha=2026-11-20")
    assert resp_disp.status_code == 200
    assert "09:00" in resp_disp.json()["horarios_disponibles"]

    # 2. Reservar cita (debe responder 201 Created según TSK-04)
    payload = {
        "paciente_nombre": "Carlos Prueba",
        "paciente_email": "carlos@test.com",
        "medico_id": 1,
        "fecha": "2026-11-20",
        "hora": "09:00"
    }
    resp_reserva = client.post("/api/citas/reservar", json=payload)
    assert resp_reserva.status_code == 201
    assert resp_reserva.json()["notificacion_enviada"] is True

    # 3. Intentar doble reserva en el mismo horario (debe rechazar con 409 Conflict)
    resp_duplicada = client.post("/api/citas/reservar", json=payload)
    assert resp_duplicada.status_code == 409

def test_control_acceso_expediente_por_rol():
    # Paciente no puede ver expediente (403 Forbidden)
    resp_paciente = client.get("/api/expedientes/Juan Pérez", headers={"X-Rol": "PACIENTE"})
    assert resp_paciente.status_code == 403

    # Médico sí puede ver expediente (200 OK)
    resp_medico = client.get("/api/expedientes/Juan Pérez", headers={"X-Rol": "MEDICO"})
    assert resp_medico.status_code == 200
    assert resp_medico.json()["tipo_sangre"] == "O+"