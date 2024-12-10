import pytest
from data_models.factories import DeploymentFactory, DeviceFactory, ProjectFactory
from data_models.serializers import (
    DeploymentSerializer,
    DeviceSerializer,
    ProjectSerializer,
)


def api_check_post(api_client, api_url, payload, check_key):
    """
    Function to test if object can be created and read through the API.

    Args:
        api_client (rest_framework.tests.APIclient): API client with a forced log in.
        api_url (string): URL to which the api_client will POST.
        payload (dict): data to POST.
        check_key (string): key to check in returned data.
    """
    response_create = api_client.post(
        api_url, data=payload, format="json")
    print(f"{response_create.data}")

    assert response_create.status_code == 201
    assert response_create.data[check_key] == payload[check_key]
    response_id = response_create.data["id"]

    response_read = api_client.get(
        f"{api_url}{response_id}/", format="json")
    print(f"Response: {response_read.data}")
    assert response_read.status_code == 200
    assert response_read.data[check_key] == payload[check_key]
    if "owner" in response_read.data.keys():
        assert response_read.data["owner"] == api_client.handler._force_user.username


def api_check_update(api_client, api_url, new_value, check_key):
    """
    Function to test if object can be updated and read through the API.

    Args:
        api_client (rest_framework.tests.APIclient): API client with a forced log in.
        api_url (string): URL which the api_client will PATCH.
        new_value (any): New value in the PATCH.
        check_key (string): Key which will be PATCHed and checked in the returned data.
    """
    response_update = api_client.patch(
        api_url, data={check_key: new_value}, format="json")
    print(f"Response: {response_update.data}")
    assert response_update.status_code == 200
    assert response_update.data[check_key] == new_value

    response_read = api_client.get(
        api_url, format="json")
    print(f"Response: {response_read.data}")
    assert response_read.status_code == 200
    assert response_read.data[check_key] == new_value


def api_check_delete(api_client, api_url):
    """
    Function to test if object can be deleted through the API.

    Args:
        api_client (rest_framework.tests.APIclient): API client with a forced log in.
        api_url (string): URL which the api_client will DELETE.
    """

    response_delete = api_client.delete(
        api_url, format="json")
    print(f"Response: {response_delete.data}")
    assert response_delete.status_code == 204

    response_read = api_client.get(
        api_url, format="json")
    print(f"Response: {response_read.data}")
    assert response_read.status_code == 404


@pytest.mark.django_db
def test_create_project(api_client_with_credentials):
    """
    Test: Can project be created and retrieved through the API.
    """
    check_key = 'name'
    serializer = ProjectSerializer
    new_item = ProjectFactory.build(
        name='test_project',
        project_ID='test_pr_ID')
    api_url = '/api/project/'
    payload = serializer(instance=new_item).data
    api_check_post(api_client_with_credentials, api_url,
                   payload, check_key)


@pytest.mark.django_db
def test_update_project(api_client_with_credentials):
    """
    Test: Can project be updated and retrieved through the API.
    """
    user = api_client_with_credentials.handler._force_user
    check_key = 'project_ID'
    new_item = ProjectFactory(
        name='test_project',
        project_ID='test_pr_ID',
        owner=user)

    api_url = f'/api/project/{new_item.pk}/'
    new_value = 'pr_ID_test'
    api_check_update(api_client_with_credentials,
                     api_url, new_value, check_key)


@pytest.mark.django_db
def test_delete_project(api_client_with_credentials):
    """
    Test: Can project be deleted through the API.
    """
    user = api_client_with_credentials.handler._force_user
    new_item = ProjectFactory(
        name='test_project',
        project_ID='test_pr_ID',
        owner=user)

    api_url = f'/api/project/{new_item.pk}/'

    api_check_delete(api_client_with_credentials,
                     api_url)


@pytest.mark.django_db
def test_create_deployment(api_client_with_credentials):
    """
    Test: Can deployment be created and retrieved through the API.
    """
    user = api_client_with_credentials.handler._force_user
    check_key = 'deployment_ID'
    serializer = DeploymentSerializer
    new_item = DeploymentFactory(
        deployment_ID='test_ID',
        project=[]
    )
    new_item.device.owner = user
    new_item.device.save()
    api_url = '/api/deployment/'
    payload = serializer(instance=new_item).data
    new_item.delete()
    api_check_post(api_client_with_credentials, api_url,
                   payload, check_key)


@pytest.mark.django_db
def test_update_deployment(api_client_with_credentials):
    """
    Test: Can deployment be updated and retrieved through the API.
    """
    user = api_client_with_credentials.handler._force_user
    check_key = 'deployment_ID'
    new_item = DeploymentFactory(
        deployment_ID='test_ID',
        project=[],
        owner=user
    )

    api_url = f'/api/deployment/{new_item.pk}/'
    new_value = 'new_deployment'
    api_check_update(api_client_with_credentials,
                     api_url, new_value, check_key)


@pytest.mark.django_db
def test_delete_deployment(api_client_with_credentials):
    """
    Test: Can deployment be deleted through the API.
    """
    user = api_client_with_credentials.handler._force_user
    new_item = DeploymentFactory(
        deployment_ID='test_ID',
        project=[],
        owner=user
    )

    api_url = f'/api/deployment/{new_item.pk}/'

    api_check_delete(api_client_with_credentials,
                     api_url)


# device tests
@pytest.mark.django_db
def test_create_device(api_client_with_credentials):
    """
    Test: Can device be created and retrieved through the API.
    """
    check_key = 'name'
    serializer = DeviceSerializer
    new_item = DeviceFactory()
    api_url = '/api/device/'
    payload = serializer(instance=new_item).data
    payload["managers_ID"] = []
    print(payload)
    new_item.delete()
    api_check_post(api_client_with_credentials, api_url,
                   payload, check_key)


@pytest.mark.django_db
def test_update_device(api_client_with_credentials):
    """
    Test: Can device be updated and retrieved through the API.
    """
    user = api_client_with_credentials.handler._force_user
    check_key = 'name'
    new_item = DeviceFactory(owner=user)
    api_url = f'/api/device/{new_item.pk}/'
    new_value = 'new_device_name'

    api_check_update(api_client_with_credentials,
                     api_url, new_value, check_key)


@pytest.mark.django_db
def test_delete_device(api_client_with_credentials):
    """
    Test: Can device be udeleted through the API.
    """
    user = api_client_with_credentials.handler._force_user
    new_item = DeviceFactory(owner=user)
    api_url = f'/api/device/{new_item.pk}/'
    api_check_delete(api_client_with_credentials,
                     api_url)

    # file tests at some point
