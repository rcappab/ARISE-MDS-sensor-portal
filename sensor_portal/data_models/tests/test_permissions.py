import pytest
from data_models.factories import (
    DeploymentFactory,
    DeviceFactory,
    ProjectFactory,
    SiteFactory,
)
from data_models.models import Deployment
from data_models.serializers import DeploymentSerializer
from user_management.factories import UserFactory

# permissions
# can't deploy a non-managed device, creation and update


@pytest.mark.django_db
def test_deploy_non_managed_device(api_client_with_credentials):
    """
    Test: Check user cannot deploy a device they do not own, both at creation and during an update.
    """
    user = api_client_with_credentials.handler._force_user
    site = SiteFactory()
    device_not_owned = DeviceFactory()
    device_owned = DeviceFactory(
        owner=user, type=device_not_owned.type, model=device_not_owned.model)
    not_allowed_deployment = DeploymentFactory.build(
        device=device_not_owned, site=site)
    not_allowed_payload = DeploymentSerializer(
        instance=not_allowed_deployment).data

    api_url = '/api/deployment/'

    response_create_not_allowed = api_client_with_credentials.post(
        api_url, data=not_allowed_payload, format="json")
    print(response_create_not_allowed.data)
    assert response_create_not_allowed.status_code == 403

    allowed_deployment = DeploymentFactory.build(
        device=device_owned, site=site)
    allowed_payload = DeploymentSerializer(
        instance=allowed_deployment).data

    response_create_allowed = api_client_with_credentials.post(
        api_url, data=allowed_payload, format="json")

    print(response_create_allowed.data)
    assert response_create_allowed.status_code == 201
    response_id = response_create_allowed.data["id"]

    response_update_not_allowed = api_client_with_credentials.patch(
        f'{api_url}{response_id}/', data={"device_ID": device_not_owned.pk}, format="json")
    print(response_update_not_allowed.data)
    assert response_update_not_allowed.status_code == 403

    device_not_owned.managers.add(user)
    response_update_allowed = api_client_with_credentials.patch(
        f'{api_url}{response_id}/', data={"device_ID": device_not_owned.pk}, format="json")
    print(response_update_allowed.data)
    assert response_update_allowed.status_code == 200


@pytest.mark.django_db
def test_deploy_to_non_managed_project(api_client_with_credentials):
    user = api_client_with_credentials.handler._force_user
    site = SiteFactory()
    device_owned = DeviceFactory(
        owner=user)
    project_not_owned = ProjectFactory()
    project_owned = ProjectFactory(owner=user)

    api_url = '/api/deployment/'

    new_deployment = DeploymentFactory.build(
        device=device_owned, site=site)
    not_allowed_payload = DeploymentSerializer(
        instance=new_deployment).data
    not_allowed_payload['project_ID'] = [project_not_owned.pk]

    print("create not allowed")
    response_create_not_allowed = api_client_with_credentials.post(
        api_url, data=not_allowed_payload, format="json")
    print(response_create_not_allowed.data)
    assert response_create_not_allowed.status_code == 403

    new_deployment = DeploymentFactory.build(
        device=device_owned, site=site)

    allowed_payload = DeploymentSerializer(
        instance=new_deployment).data
    allowed_payload['project_ID'] = [project_owned.pk]

    print("create allowed")
    response_create_allowed = api_client_with_credentials.post(
        api_url, data=allowed_payload, format="json")
    print(response_create_allowed.data)
    assert response_create_allowed.status_code == 201
    response_id = response_create_allowed.data["id"]

    print("update not allowed")
    response_update_not_allowed = api_client_with_credentials.patch(
        f'{api_url}{response_id}/', data={"project_ID": [project_not_owned.pk]}, format="json")

    print(response_update_not_allowed.data)
    assert response_update_not_allowed.status_code == 403

    response_update_allowed = api_client_with_credentials.patch(
        f'{api_url}{response_id}/', data={"project_ID": [project_owned.pk]}, format="json")

    print(response_update_allowed.data)
    assert response_update_allowed.status_code == 200
