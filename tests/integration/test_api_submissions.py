from fastapi import status


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "sandbox_mode" in data
    assert "docker_available" in data


def test_post_submission_run_success(client):
    payload = {
        "problem_id": "two_sum_001",
        "language": "python",
        "code": "import sys\nline = sys.stdin.read().strip()\nprint(f'Processed: {line}')",
        "input": "sample test data",
    }
    response = client.post("/submissions/run", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "submission_id" in data
    assert data["problem_id"] == "two_sum_001"
    assert data["result"]["status"] == "success"
    assert "Processed: sample test data" in data["result"]["stdout"]
    assert data["result"]["exit_code"] == 0

    # Test retrieval of the persisted submission
    sub_id = data["submission_id"]
    get_res = client.get(f"/submissions/{sub_id}")
    assert get_res.status_code == status.HTTP_200_OK
    detail = get_res.json()
    assert detail["id"] == sub_id
    assert detail["status"] == "success"
    assert "Processed: sample test data" in detail["stdout"]


def test_post_submission_run_runtime_error(client):
    payload = {
        "problem_id": "problem_err",
        "language": "python",
        "code": "raise ValueError('Custom failure message')",
    }
    response = client.post("/submissions/run", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["result"]["status"] == "runtime_error"
    assert "ValueError" in data["result"]["stderr"]


def test_post_submission_validation_error(client):
    # Missing required field 'problem_id'
    payload = {
        "code": "print('hello')",
    }
    response = client.post("/submissions/run", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_submission_not_found(client):
    response = client.get("/submissions/non-existent-uuid")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_problems(client):
    response = client.get("/problems")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
