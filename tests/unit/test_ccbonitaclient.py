from unittest import TestCase

from ccbonitaclient import ccbonitaclient


class TestCCBonitaClient(TestCase):
    def test__find_process_id_from_name(self):
        EXPECTED_PROCESS_ID = "902891387048802672"
        GIVEN_PROCESS_NAME = "RegisterUser"
        GIVEN_DEPLOYED_PROCESSES = [
            {
                "displayDescription": "",
                "deploymentDate": "2023-11-19 23:59:56.594",
                "displayName": "RegisterUser",
                "name": GIVEN_PROCESS_NAME,
                "description": "",
                "deployedBy": "204",
                "id": EXPECTED_PROCESS_ID,
                "activationState": "ENABLED",
                "version": "1.0",
                "configurationState": "RESOLVED",
                "last_update_date": "2023-11-19 23:59:56.832",
                "actorinitiatorid": "301",
            }
        ]

        self.assertEqual(
            EXPECTED_PROCESS_ID,
            ccbonitaclient._find_process_id_from_name(
                GIVEN_PROCESS_NAME, GIVEN_DEPLOYED_PROCESSES
            ),
        )

    def test__find_task_id_from_name(self):
        EXPECTED_TASK_ID = "100063"
        GIVEN_TASK_NAME = "Step2-Manual"
        GIVEN_AVAILABLE_TASKS = [
            {
                "displayDescription": "",
                "executedBy": "0",
                "rootContainerId": "5014",
                "assigned_date": "",
                "displayName": GIVEN_TASK_NAME,
                "executedBySubstitute": "0",
                "dueDate": "",
                "description": "",
                "type": "USER_TASK",
                "priority": "normal",
                "actorId": "505",
                "processId": "5522989229928495767",
                "caseId": "5014",
                "name": "Step2-Manual",
                "reached_state_date": "2023-12-20 23:48:43.612",
                "rootCaseId": "5014",
                "id": EXPECTED_TASK_ID,
                "state": "ready",
                "parentCaseId": "5014",
                "last_update_date": "2023-12-20 23:48:43.612",
                "assigned_id": "",
            }
        ]

        self.assertEqual(
            EXPECTED_TASK_ID,
            ccbonitaclient._find_task_id_from_name(
                GIVEN_TASK_NAME, GIVEN_AVAILABLE_TASKS
            ),
        )

        pass
