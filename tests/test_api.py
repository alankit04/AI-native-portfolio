import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient", reason="fastapi is not available in this environment")
pytest.importorskip("sqlmodel", reason="sqlmodel is not available in this environment")

from fastapi.testclient import TestClient
from main import app
from worker import process_one_job

client = TestClient(app)

def test_case_flow():
    data = {"case_id": "CASE-1", "patient_name": "Jane Roe", "payer": "Aetna"}
    files = {"file": ("note.txt", b"Diagnosis severe back pain\nTreatment physical therapy failed\nNeed MRI due to persistent symptoms", "text/plain")}
    r = client.post("/v1/cases", data=data, files=files)
    assert r.status_code == 200

    r = client.post("/v1/cases/CASE-1/generate")
    assert r.status_code == 202

    assert process_one_job() is True

    r = client.get("/v1/cases/CASE-1")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "generated"
    assert "Prior Authorization Request" in body["draft_text"]
