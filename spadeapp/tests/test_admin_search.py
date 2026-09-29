import pytest
from rest_framework import status


@pytest.mark.parametrize(
    "model_url",
    ["processes/processrun", "files/fileupload"],
)
def test_changelist_search(admin_client, model_url):
    resp = admin_client.get(f"/admin/{model_url}/", {"q": "anything"})

    assert resp.status_code == status.HTTP_200_OK
