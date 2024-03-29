from unittest import TestCase

import requests
from ccbonitaclient.ccbonitaclient import (
    complete_task,
    connect,
    launch_process,
    _set_session,
)

# Discover BONITA server running port
# See BONITA STUDIO engine logs: Help -> Bonita Engine log
# Example:
# 2024-03-14T10:24:15,022+0100 | buda | INFO  | [main|1] o.a.c.h.Http11NioProtocol - Initializing ProtocolHandler ["http-nio-63471"]
BONITA_ENGINE_PORT = 63471

GIVEN_BONITA_CREDENTIALS = {
    "BPM_BASE_URL": f"http://localhost:{BONITA_ENGINE_PORT}/bonita",
    "BPM_USER": "test.user",
    "BPM_PASS": "bpm",
}
GIVEN_REQUIRED_TEST_PROCESS = "TEST_PROCESS"


class TestCCBonitaClient(TestCase):

    def setUp(self):
        try:
            connect(
                GIVEN_BONITA_CREDENTIALS["BPM_BASE_URL"],
                GIVEN_BONITA_CREDENTIALS["BPM_USER"],
                GIVEN_BONITA_CREDENTIALS["BPM_PASS"],
            )
        except requests.HTTPError:
            self.fail("Fail to connect to Bonita engine!!:" + GIVEN_BONITA_CREDENTIALS)

    def test_connect_fail(self):
        GIVEN_WRONG_PASSWORD = "wrong password"
        self.assertRaises(
            requests.exceptions.HTTPError,
            lambda: connect(
                GIVEN_BONITA_CREDENTIALS["BPM_BASE_URL"],
                GIVEN_BONITA_CREDENTIALS["BPM_USER"],
                GIVEN_WRONG_PASSWORD,
            ),
        )

    def test_check_deployed_process(self):
        GIVEN_MANDATORY_PROCESSES = [GIVEN_REQUIRED_TEST_PROCESS]
        try:
            connect(
                GIVEN_BONITA_CREDENTIALS["BPM_BASE_URL"],
                GIVEN_BONITA_CREDENTIALS["BPM_USER"],
                GIVEN_BONITA_CREDENTIALS["BPM_PASS"],
                GIVEN_MANDATORY_PROCESSES,
            )
        except requests.HTTPError:
            self.fail(
                "Fail to check process:"
                + GIVEN_REQUIRED_TEST_PROCESS
                + "\nIs it deployed?"
                + "\nSee 'fixtures' folder to get a deployable process."
            )

    def test_launch_process(self):
        process_name = GIVEN_REQUIRED_TEST_PROCESS
        entity_id = 1
        process_params = {"user_id": entity_id}

        try:
            case_id = launch_process(process_name, entity_id, process_params)
            self.assertIsNotNone(case_id)
        except requests.HTTPError:
            self.fail(
                "Fail to launch process:"
                + GIVEN_REQUIRED_TEST_PROCESS
                + "\nIs it deployed?"
                + "\nSee 'fixtures' folder to get a deployable process."
            )

    def test_launch_process_reconnecting(self):
        GIVEN_INVALID_SESSION = {
            "JSESSIONID": "JSESSIONID",
            "X-Bonita-API-Token": "X-Bonita-API-Token",
            "BOS_Locale": "en",
        }
        _set_session(GIVEN_INVALID_SESSION)

        process_name = GIVEN_REQUIRED_TEST_PROCESS

        entity_id = 1
        process_params = {"user_id": entity_id}

        try:
            case_id = launch_process(process_name, entity_id, process_params)
            self.assertIsNotNone(case_id)
        except requests.HTTPError:
            self.fail(
                "Fail to launch process:"
                + GIVEN_REQUIRED_TEST_PROCESS
                + "\nIs it deployed?"
                + "\nSee 'fixtures' folder to get a deployable process."
            )

    def test_complete_task(self):
        GIVEN_TASK_NAME = "manual_step2"

        process_name = GIVEN_REQUIRED_TEST_PROCESS
        task_name = GIVEN_TASK_NAME
        entity_id = 1
        process_params = {"user_id": entity_id}

        case_id = launch_process(process_name, entity_id, process_params)
        self.assertIsNotNone(case_id)

        try:
            complete_task(process_name, entity_id, task_name)
        except requests.HTTPError:
            self.fail(
                "Fail to complete task: "
                + GIVEN_TASK_NAME
                + "\on process: "
                + GIVEN_REQUIRED_TEST_PROCESS
                + "\nIs it deployed?"
                + "\nSee 'fixtures' folder to get a deployable process."
            )
