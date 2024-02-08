import json
import time
import requests

SYSTEM_PROCESS_REGISTER = "SYSTEM_RegisterProcess"
SYSTEM_PROCESS_REGISTRY = "io.codecontract.core.ProcessRegistry"

_connection_settings = {}
_session = {}


def connect(url, user, passwd, check_processes=[]):
    """
    Connect to the specified bonita server using the provided credentials.

    Args:
        url (str): The URL of the server to connect to.
        user (str): The username for authentication.
        passwd (str): The password for authentication.
        check_processes (list, optional): A list of processes to check on the startup, 
        to ensure they exist and fail fast. Defaults to an empty list.

    Raises:
        ValueError: If the URL, user, or password is missing.
        Exception: If a mandatory processes are not deployed in the server.
    """

    global _connection_settings

    if not url:
        raise ValueError("Missing BPM_BASE_URL")
    if not user:
        raise ValueError("Missing BPM_USER")
    if not passwd:
        raise ValueError("Missing BPM_PASS")

    _connection_settings["url"] = url
    _connection_settings["user"] = user
    _connection_settings["passwd"] = passwd

    _refresh_session()
    check_processes.insert(0, SYSTEM_PROCESS_REGISTER)
    for p in check_processes:
        if not _get_process_id(p):
            raise Exception(
                "Missing mandatory process:" + p + "\nPlease deploy it before continue."
            )


def launch_process(process_name, entity_id, params=None):
    """
    Launches a process.

    Args:
        process_name (str): The name of the process to launch.
        entity_id (int): The ID of the entity associated with the process (i.e.: user_id).
        params (dict, optional): Additional parameters for the process. Defaults to None.

    Returns:
        str: The ID of the launched case/process instance.
    """

    process_id = _get_process_id(process_name)
    payload = json.dumps(params) if params else None

    def doRequest():
        session = _get_session()
        return requests.post(
            _connection_settings["url"]
            + "/API/bpm/process/{}/instantiation".format(process_id),
            cookies=session,
            data=payload,
            headers={
                "X-Bonita-API-Token": session["X-Bonita-API-Token"],
                "Content-Type": "application/json",
            },
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()

    case_id = r.json()["caseId"]
    _save_case(process_name, str(entity_id), case_id)

    return case_id


def complete_task(process_name, entity_id, task_name, params=None):
    """
    Completes a task. 
    Args:
        process_name (str): The name of the process.
        entity_id (int): The ID of the entity (i.e.: user_id).
        task_name (str): The name of the task.
        params (dict, optional): Additional parameters for the task. Defaults to None.
    Returns:
        None
    """
    case_id = _get_case(process_name, str(entity_id))

    task_id = _get_task_id(task_name, case_id)
    payload = json.dumps(params) if params else None

    def doRequest():
        session = _get_session()
        return requests.post(
            _connection_settings["url"]
            + "/API/bpm/userTask/{}/execution?assign=true".format(task_id),
            cookies=session,
            data=payload,
            headers={
                "X-Bonita-API-Token": session["X-Bonita-API-Token"],
                "Content-Type": "application/json",
            },
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()


def _get_session():
    global _session
    if not _session:
        _session = _login()

    return _session


def _refresh_session():
    _session = _login()
    return _session


def _login(user=None, passwd=None):
    if not user:
        user = _connection_settings["user"]
    if not passwd:
        passwd = _connection_settings["passwd"]

    data = {"username": user, "password": passwd}
    payload = "&".join([f"{k}={v}" for k, v in data.items()])
    r = requests.post(
        _connection_settings["url"] + "/loginservice",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    r.raise_for_status()
    session = {
        "JSESSIONID": r.cookies["JSESSIONID"],
        "X-Bonita-API-Token": r.cookies["X-Bonita-API-Token"],
        "BOS_Locale": r.cookies["BOS_Locale"],
    }
    return session


def _find_process_id_from_name(process_name, processes):
    for process in processes:
        if process["name"] == process_name:
            return process["id"]
    return None


def _find_task_id_from_name(task_name, tasks):
    for task in tasks:
        if task["name"] == task_name:
            return task["id"]
    return None


def _get_process_id(process_name, process_version=None, retry_countdown=3):
    url_params = [
        ("f", "name=" + process_name),
        ("f", "version=" + process_version if process_version else None),
    ]

    def doRequest():
        session = _get_session()
        return requests.get(
            _connection_settings["url"] + "/API/bpm/process",
            params=url_params,
            cookies=session,
            headers={"X-Bonita-API-Token": session["X-Bonita-API-Token"]},
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()
    processes = r.json()

    # retry if process is not instantiated
    if processes == [] and retry_countdown > 0:
        time.sleep(1)
        return _get_process_id(process_name, process_version, retry_countdown - 1)

    process_id = _find_process_id_from_name(process_name, processes)

    return process_id


def _get_task_id(task_name, case_id, retry_countdown=3):
    url_params = [
        ("f", "caseId=" + str(case_id)),
        ("f", "name=" + task_name),
    ]

    def doRequest():
        session = _get_session()
        return requests.get(
            _connection_settings["url"] + "/API/bpm/task",
            params=url_params,
            cookies=session,
            headers={"X-Bonita-API-Token": session["X-Bonita-API-Token"]},
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()
    tasks = r.json()

    # retry if task is not instantiated
    if tasks == [] and retry_countdown > 0:
        time.sleep(1)
        return _get_task_id(task_name, case_id, retry_countdown - 1)

    task_id = _find_task_id_from_name(task_name, tasks)

    return task_id


def _get_case(process_name, entity_id):
    url_params = [
        ("q", "findByProcessNameAndEntityId"),
        ("p", 0),
        ("c", 1),
        ("f", "processName=" + str(process_name)),
        ("f", "entityId=" + entity_id),
    ]

    def doRequest():
        session = _get_session()
        return requests.get(
            _connection_settings["url"]
            + "/API/bdm/businessData/"
            + SYSTEM_PROCESS_REGISTRY,
            params=url_params,
            cookies=session,
            headers={"X-Bonita-API-Token": session["X-Bonita-API-Token"]},
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()
    try:
        result = r.json()

        case_id = result[0]["caseId"]
    except:
        raise Exception(
            "Failed to get data for processName: '"
            + process_name
            + "' entityId: "
            + str(entity_id)
            + "\n Possible cause: Missing mandatory BDM class in Bonita setup: "
            + SYSTEM_PROCESS_REGISTRY
        )

    return case_id


def _save_case(process_name, entity_id, case_id):
    process_id = _get_process_id(SYSTEM_PROCESS_REGISTER)
    payload = json.dumps(
        {
            "processRegisterInput": {
                "processName": process_name,
                "entityId": entity_id,
                "caseId": case_id,
            }
        }
    )

    def doRequest():
        session = _get_session()
        return requests.post(
            _connection_settings["url"]
            + "/API/bpm/process/{}/instantiation".format(process_id),
            cookies=session,
            data=payload,
            headers={
                "X-Bonita-API-Token": session["X-Bonita-API-Token"],
                "Content-Type": "application/json",
            },
        )

    r = doRequest()
    # Retry login if unauthorized
    if r.status_code == 401:
        _refresh_session()
        r = doRequest()

    r.raise_for_status()
