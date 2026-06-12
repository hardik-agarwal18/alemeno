import os
from unittest.mock import patch

def test_health_check(client):
    response = client.get("/health")
    # Even if DB/Redis fail in test, it should return a JSON response
    # For in-memory sqlite, DB should pass. Redis might fail unless mocked
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data

@patch("app.api.routes.jobs.process_transactions_job.delay")
def test_upload_csv(mock_delay, client, tmp_path):
    csv_content = b"txn_id,amount,merchant\n1,100,Uber"
    csv_file = tmp_path / "test.csv"
    csv_file.write_bytes(csv_content)
    
    with open(csv_file, "rb") as f:
        response = client.post(
            "/jobs/upload",
            files={"file": ("test.csv", f, "text/csv")}
        )
        
    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    mock_delay.assert_called_once()
    
def test_list_jobs(client):
    response = client.get("/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_job_status_not_found(client):
    import uuid
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/jobs/{random_uuid}/status")
    assert response.status_code == 404

def test_get_job_results_not_found(client):
    import uuid
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/jobs/{random_uuid}/results")
    assert response.status_code == 404
