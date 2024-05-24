"""FastAPI routes for the job."""

from typing import List

from fastapi import APIRouter, Body, Request, status

from florist.api.db.entities import MAX_RECORDS_TO_FETCH, Job, JobStatus


router = APIRouter()


@router.post(
    path="",
    response_description="Create a new job",
    status_code=status.HTTP_201_CREATED,
    response_model=Job,
)
async def new_job(request: Request, job: Job = Body(...)) -> Job:  # noqa: B008
    """
    Create a new training job.

    If calling from the REST API, it will receive the job attributes as the Request Body in raw/JSON format.
    See `florist.api.db.entities.Job` to check the list of attributes and their requirements.

    :param request: (fastapi.Request) the FastAPI request object.
    :param job: (Job) The Job instance to be saved in the database.
    :return: (Job) The job that has been saved in the database.
    :raises: (HTTPException) status 400 if job.server_info is not None and cannot be parsed into JSON.
    """
    job_id = await job.create(request.app.database)
    job_in_db = await Job.find_by_id(job_id, request.app.database)

    assert job_in_db is not None
    return job_in_db


@router.get(path="/{status}", response_description="List jobs with the specified status", response_model=List[Job])
async def list_jobs_with_status(status: JobStatus, request: Request) -> List[Job]:
    """
    List jobs with specified status.

    Fetches list of Job with max length MAX_RECORDS_TO_FETCH.

    :param status: (JobStatus) The status of jobs to query the Job DB for.
    :param request: (fastapi.Request) the FastAPI request object.
    :return: (List[Dict[str, Any]]) A list where each entry is a dictionary with the attributes
        of a Job instance with the specified status.
    """
    return await Job.find_by_status(status, MAX_RECORDS_TO_FETCH, request.app.database)
