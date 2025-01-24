import json

from unittest.mock import patch, Mock, AsyncMock
from fastapi.responses import JSONResponse

from florist.api.routes.server.job import change_job_status, get_job
from florist.api.db.server_entities import JobStatus


@patch("florist.api.db.entities.Job.find_by_id")
async def test_get_job_success(mock_find_by_id: Mock) -> None:
    mock_job = Mock()
    mock_find_by_id.return_value = mock_job

    mock_request = Mock()
    mock_request.app.database = Mock()

    test_id = "test_id"

    response = await get_job(test_id, mock_request)

    mock_find_by_id.assert_called_once_with(test_id, mock_request.app.database)

    assert response == mock_job


@patch("florist.api.db.entities.Job.find_by_id")
async def test_get_job_fail_none_job(mock_find_by_id: Mock) -> None:
    mock_find_by_id.return_value = None

    mock_request = Mock()
    mock_request.app.database = Mock()

    test_id = "test_id"

    response = await get_job(test_id, mock_request)

    mock_find_by_id.assert_called_once_with(test_id, mock_request.app.database)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert json.loads(response.body.decode("utf-8")) == {"error": f"Job with ID {test_id} does not exist."}


@patch("florist.api.db.entities.Job.find_by_id")
async def test_change_job_status_success(mock_find_by_id: Mock) -> None:
    mock_job = Mock()
    mock_job.set_status = AsyncMock()

    mock_find_by_id.return_value = mock_job

    mock_request = Mock()
    mock_request.app.database = Mock()

    test_id = "test_id"
    test_status = JobStatus.NOT_STARTED

    response = await change_job_status(test_id, test_status, mock_request)

    mock_find_by_id.assert_called_once_with(test_id, mock_request.app.database)
    mock_job.set_status.assert_called_once_with(test_status, mock_request.app.database)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert json.loads(response.body.decode("utf-8")) == {"status": "success"}


@patch("florist.api.db.entities.Job.find_by_id")
async def test_change_job_status_failure_in_find_by_id(mock_find_by_id: Mock) -> None:
    mock_find_by_id.return_value = None

    mock_request = Mock()
    mock_request.app.database = Mock()

    test_id = "test_id"
    test_status = JobStatus.NOT_STARTED

    response = await change_job_status(test_id, test_status, mock_request)

    mock_find_by_id.assert_called_once_with(test_id, mock_request.app.database)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert json.loads(response.body.decode("utf-8")) == {"error": "Job test_id not found"}


@patch("florist.api.db.entities.Job.find_by_id")
async def test_change_job_status_failure_in_set_status(mock_find_by_id: Mock) -> None:
    mock_job = Mock()
    mock_job.set_status = AsyncMock()
    mock_job.set_status.side_effect = ValueError("Test Error")

    mock_find_by_id.return_value = mock_job

    mock_request = Mock()
    mock_request.app.database = Mock()

    test_id = "test_id"
    test_status = JobStatus.NOT_STARTED

    response = await change_job_status(test_id, test_status, mock_request)

    mock_find_by_id.assert_called_once_with(test_id, mock_request.app.database)
    mock_job.set_status.assert_called_once_with(test_status, mock_request.app.database)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert json.loads(response.body.decode("utf-8")) == {"error": "Test Error"}
