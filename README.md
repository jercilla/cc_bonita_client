# CodeContract Bonita client
Python client for CodeContract Bonita integration through REST API

## Run tests
```
python3 -m unittest tests.unit.test_ccbonitaclient.TestCCBonitaClient
python3 -m unittest tests.integration.test_ccbonitaclient.TestCCBonitaClient 
```
Note: Integration test will require local Bonita server running (`http://localhost:24038/bonita`) and properly configured (see `/fixtures` folder).

## Documentation

See (1st) tests and (2nd) source comments.

