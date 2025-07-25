import json
from enum import Enum


class TaskStatus(int, Enum):
    """
    Task status enumeration. Status is represented as an integer.
    """

    UNKNOWN = -1
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2
    TIMEOUT = 3
    CANCELLED = 4


class TaskType(str, Enum):
    """
    Task type enumeration. Type is represented as a string.
    """

    GENERAL = "general"
    HEADSHOT = "headshot"


class Task:
    """
    Task class to represent a task.
    """

    _task_id: str = ""
    _task_status = TaskStatus.UNKNOWN
    _task_input = None
    _task_output = None
    _task_type = None
    _task_errors = None

    def __init__(self,
                 task_id: str,
                 task_input,
                 task_type: TaskType = TaskType.GENERAL,
                 status: TaskStatus = TaskStatus.UNKNOWN,
                 ):
        self._task_id = task_id
        self._task_input = task_input
        self._task_type = task_type
        self._task_status = status

    def __repr__(self):
        return f"Task(task_id={self._task_id}, task_type={self._task_type}, status={self.status}, task_input={self._task_input}, output={self.output}, errors={self.errors})"

    @property
    def id(self):
        """
        Task ID.
        :return: Task ID.
        """

        return self._task_id

    @property
    def status(self):
        """
        Status of the task.
        :return: TaskStatus.
        """

        return self._task_status

    @status.setter
    def status(self, _status: TaskStatus):
        """
        Set status of the task.
        :param _status: TaskStatus.
        :return: None.
        """

        self._task_status = _status

    @property
    def type(self):
        """
        Task type.
        :return: Task type.
        """

        return self._task_type

    @type.setter
    def type(self, _type):
        """
        Set task type.
        :param _type: Task type.
        :return: None.
        """

        self._task_type = _type

    @property
    def input(self):
        """
        Input of the task.
        :return: Task input.
        """

        return self._task_input

    @input.setter
    def input(self, _input):
        """
        Set input of the task.
        :param _input: Task input.
        :return: None.
        """

        self._task_input = _input

    @property
    def output(self):
        """
        Output of the task.
        :return: Task output.
        """

        return self._task_output

    @output.setter
    def output(self, _output):
        """
        Set output of the task.
        :param _output: Task output.
        :return: None.
        """

        self._task_output = _output

    @property
    def errors(self):
        """
        Errors of the task.
        :return: Task errors.
        """

        return self._task_errors

    @errors.setter
    def errors(self, _errors):
        """
        Set errors of the task.
        :param _errors: Task errors.
        :return: None.
        """

        self._task_errors = _errors

    def print(self):
        """
        Print task object.
        :return: Task object as dictionary.
        """

        return {
            "task_id": self._task_id,
            "task_type": self._task_type,
            "status": self._task_status,
            "input": self._task_input,
            "output": self._task_output,
            "errors": self._task_errors,
        }

    def to_json(self) -> str:
        """
        Convert task object to JSON string.
        :return: JSON string.
        """

        return json.dumps(self.print())
