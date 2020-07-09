import pytest


class DummyResponse:
    pass


@pytest.fixture(scope="module", autouse=True)
def get_dummy_response_with_status_200(request):
    response = DummyResponse()
    response.status_code = 200
    return response
