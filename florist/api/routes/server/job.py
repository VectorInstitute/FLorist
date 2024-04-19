"""FastAPI routes for the job."""
from json import JSONDecodeError
from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder

from florist.api.db.entities import JOB_DATABASE_NAME, MAX_RECORDS_TO_FETCH, Job, JobStatus


router = APIRouter()


@router.post(
    path="/",
    response_description="Create a new job",
    status_code=status.HTTP_201_CREATED,
    response_model=Job,
)
async def new_job(request: Request, job: Job = Body(...)) -> Dict[str, Any]:  # noqa: B008
    """
    Create a new training job.

    If calling from the REST API, it will receive the job attributes as the Request Body in raw/JSON format.
    See `florist.api.db.entities.Job` to check the list of attributes and their requirements.

    :param request: (fastapi.Request) the FastAPI request object.
    :param job: (Job) The Job instance to be saved in the database.
    :return: (Dict[str, Any]) A dictionary with the attributes of the new Job instance as saved in the database.
    :raises: (HTTPException) status 400 if job.server_info is not None and cannot be parsed into JSON.
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
    result = await request.app.database[JOB_DATABASE_NAME].insert_one(json_job)

    created_job = await request.app.database[JOB_DATABASE_NAME].find_one({"_id": result.inserted_id})
    assert isinstance(created_job, dict)

    return created_job


@router.get(path="/{status}", response_description="List jobs with the specified status", response_model=List[Job])
async def list_jobs_with_status(status: JobStatus, request: Request) -> List[Dict[str, Any]]:
    """
    List jobs with specified status.

    Fetches list of Job with max length MAX_RECORDS_TO_FETCH.

    :param status: (JobStatus) The status of jobs to query the Job DB for.
    :param request: (fastapi.Request) the FastAPI request object.
    :return: (List[Dict[str, Any]]) A list where each entry is a dictionary with the attributes
        of a Job instance with the specified status.
    """
    status = jsonable_encoder(status)

    job_db = request.app.database[JOB_DATABASE_NAME]
    result = await job_db.find({"status": status}).to_list(MAX_RECORDS_TO_FETCH)
    assert isinstance(result, list)
    return result
