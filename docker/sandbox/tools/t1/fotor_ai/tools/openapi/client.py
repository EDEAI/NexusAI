import http
import uuid

import requests
from loguru import logger
from retry import retry

from tools.openapi import error_code
from tools.openapi.exceptions import TaskException
from tools.openapi.task import Task, TaskType
from tools.openapi.task import TaskStatus


class OpenAPIClient:
    """
    OpenAPI Client class.
    """

    _client_id: str = str(uuid.uuid4())
    _api_key = None
    _validate_api_key_url = None
    _create_task_url = None
    _get_task_status_url = None

    def __init__(self,
                 api_key: str,
                 create_task_url: str = None,
                 get_task_status_url: str = None,
                 validate_api_key_url: str = None,
                 ):
        self._api_key = api_key
        self._create_task_url = create_task_url
        self._get_task_status_url = get_task_status_url
        self._validate_api_key_url = validate_api_key_url

        logger.info(
            f"client_id={self._client_id}, create_task_url={self._create_task_url}, get_task_status_url={self._get_task_status_url}")

    def _build_headers(self):
        """
        Build headers for the request.
        :return: headers.
        """

        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

    @retry(tries=3, delay=5, logger=logger)
    def validate_api_key(self) -> bool:
        """
        Validate API key by making a simple request.
        :return: True if valid, False otherwise.
        """

        response = requests.get(
            url=self._validate_api_key_url,
            headers=self._build_headers(),
        )

        if response.status_code == http.HTTPStatus.OK:
            return True

        return False

    def create_task(self, payload, task_type=TaskType.GENERAL) -> Task:
        """
        Create a new task.
        :param payload: Request payload.
        :param task_type: Task type.
        :return: Task object.
        """

        logger.debug(f"Creating task... URL={self._create_task_url}, Request payload={payload}")
        response = requests.post(
            url=self._create_task_url,
            headers=self._build_headers(),
            json=payload,
        )
        if response.status_code != http.HTTPStatus.OK:
            response.raise_for_status()

        rsp = response.json()
        logger.trace(f"Response={rsp}")

        # Check if the code in response is not "000"
        if rsp["code"] != error_code.OK:
            raise Exception(f"Error: {rsp['msg']}")

        # Check if the response contains the expected data
        if "data" not in rsp or "taskId" not in rsp["data"]:
            raise Exception("Invalid response from the API")

        # Get the taskId from the response
        task_id = rsp["data"]["taskId"]
        logger.debug(f"task_id={task_id}")

        # Create a new task object
        task = Task(
            task_id=task_id,
            task_type=task_type,
            task_input={
                "url": self._create_task_url,
                "payload": payload,
            },
            status=TaskStatus.IN_PROGRESS,
        )

        return task

    @retry(exceptions=TaskException, tries=180, delay=3, logger=logger)
    def polling_task_status(self, task: Task) -> Task:
        """
        Polling task status.
        :param task: Task object.
        :return: Task object.
        """

        task = self.get_task(task)

        if task.status == TaskStatus.COMPLETED:
            logger.info(f"Task completed, task={task.print()}")
        elif task.status == TaskStatus.FAILED:
            logger.info(f"Task failed, task={task.print()}")
        elif task.status == TaskStatus.IN_PROGRESS:
            logger.debug(f"Task in progress, task={task.print()}")
            raise TaskException(f"Task in progress, task={task.print()}")
        else:
            raise TaskException(f"Task not completed, task={task.print()}")

        return task

    def get_task(self, task: Task) -> Task:
        """
        Get task info.
        :param task: Task object.
        :return: Task object.
        """

        logger.debug(f"Checking the task status... URL=f'{self._get_task_status_url}/{task.id}'")
        response = requests.get(
            url=f"{self._get_task_status_url}/{task.id}",
            headers=self._build_headers(),
        )
        if response.status_code != http.HTTPStatus.OK:
            logger.error(f"response={response}")
            task.status = TaskStatus.FAILED
            return task

        rsp = response.json()
        logger.debug(f"Response={rsp}")

        # Check if the code in response is not "000"
        if rsp["code"] != error_code.OK:
            task.status = TaskStatus.FAILED
            return task

        # Check if the response contains the expected data
        if "data" not in rsp or "taskId" not in rsp["data"]:
            task.status = TaskStatus.FAILED
            return task

        # Check if the task is completed
        if rsp["data"]["status"] == TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            if task.type == TaskType.GENERAL:
                task.output = rsp["data"].get("resultUrl")
            elif task.type == TaskType.HEADSHOT:
                task.output = rsp["data"].get("avatarResult", [{}])[0].get("images", [{}])[0].get("url")

                # Replace "s3://img-pub-fotor" with "https://pub-static.fotor.com" in task.output
                task.output = task.output.replace("s3://img-pub-fotor", "https://pub-static.fotor.com")
            return task

        # Task is still processing
        elif rsp["data"]["status"] == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.IN_PROGRESS
            return task

        # Task failed
        elif rsp["data"]["status"] == TaskStatus.FAILED:
            # TODO: add error message to task
            task.status = TaskStatus.FAILED
            return task

        return task
