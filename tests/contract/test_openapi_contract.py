import schemathesis
from schemathesis import from_uri

schema = from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
def test_api_contract(case):
    response = case.call()
    case.validate_response(response)
