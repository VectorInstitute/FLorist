"""FastAPI routes for the job."""
from json import JSONDecodeError
from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder

from florist.api.db.entities import JOB_DATABASE_NAME, Job


router = APIRouter()


@router.post(
    path="/",
    response_description="Create a new job",
    status_code=status.HTTP_201_CREATED,
    response_model=Job,
)
def new_job(request: Request, job: Job = Body(...)) -> Dict[str, Any]:  # noqa: B008
    """
    Create a new training job.

    If calling from the REST API, it will receive the job attributes as the Request Body in raw/JSON format.
    See `florist.api.db.entities.Job` to check the list of attributes and their requirements.

    :param request: (fastapi.Request) the FastAPI request object.
    :param job: (Job) The Job instance to be saved in the database.
    :return: (Dict[str, Any]) A dictionary with the attributes of the new Job instance as saved in the database.
    :raises: (HTTPException) a 400 if job.server_info is not None and cannot be parsed into JSON.
    """
    try:
        is_valid = Job.is_valid_server_info(job.server_info)
        if not is_valid:
            msg = f"job.server_info is not valid. job.server_info: {job.server_info}."
            raise HTTPException(status_code=400, detail=msg)
    except JSONDecodeError as e:
        msg = f"job.server_info could not be parsed into JSON. job.server_info: {job.server_info}. Error: {e}"
        raise HTTPException(status_code=400, detail=msg) from e

    json_job = jsonable_encoder(job)
    result = request.app.database[JOB_DATABASE_NAME].insert_one(json_job)

    created_job = request.app.database[JOB_DATABASE_NAME].find_one({"_id": result.inserted_id})
    assert isinstance(created_job, dict)

    return created_job
