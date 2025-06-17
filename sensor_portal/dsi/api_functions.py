import datetime
import os

import openapi_client
from data_models.models import DataFile, Deployment, Device
from openapi_client import ApiV1DeploymentsPostRequest, ApiV1SensorsPostRequest
from openapi_client.rest import ApiException

from .api_client import ARISEDSIClient


def DSI_client(func):
    def wrapper(*args, **kwargs):
        DSIclient = ARISEDSIClient()
        DSIclient.initialise_authentication()
        with openapi_client.ApiClient(DSIclient.openapi_client_configuration) as api_client:
            func(api_client, *args, **kwargs)
    return wrapper


@DSI_client
def post_data(api_client, media_pks, dsi_project_id):

    # get DataFile
    datafile_objs = DataFile.objects.filter(
        pk__in=media_pks, local_storage=True)

    # get Deployments
    deployment_pks = datafile_objs.values_list(
        'deployment', flat=True).distinct()
    deployment_objs = Deployment.objects.filter(pk__in=deployment_pks)

    # Get Device objs
    device_pks = deployment_objs.values_list('device', flat=True).distinct()
    device_objs = Device.objects.filter(pk__in=device_pks)

    sensors_api = openapi_client.SensorsApi(api_client)
    deployments_api = openapi_client.DeploymentsApi(api_client)
    media_api = openapi_client.MediaApi(api_client)

    for device_obj in device_objs:
        # Check if sensor already exists on DSI (when this filter is available)

        # If not, create it

        create_sensor_response = sensors_api.api_v1_sensors_post(ApiV1SensorsPostRequest(
            name=device_obj.device_id,
            sensor_model_id=1)
        )
        print(f"Create sensor response: {create_sensor_response}.")

        if not create_sensor_response:
            print("Unable to create sensor object")
            continue

        device_dsi_id = create_sensor_response.id
        device_obj.extra_data["dsi_upload"] = datetime.datetime.now()
        device_obj.extra_data["dsi_id"] = device_dsi_id
        device_obj.save()

        # For each deployment of this sensor
        device_deployment_objs = device_obj.deployments.all().filter(pk__in=deployment_pks)

        for deployment_obj in device_deployment_objs:
            # Check if deployment already exists

            # If not create it
            new_deployment = ApiV1DeploymentsPostRequest(
                name=deployment_obj.deployment_device_ID,
                latitude=deployment_obj.latitude,
                longitude=deployment_obj.longitude,
                start_time=deployment_obj.deployment_start,
                end_time=deployment_obj.deployment_end,
                site_id=1,
                sensor_id=device_dsi_id,
                project_id=dsi_project_id,
            )

            create_deployment_response = deployments_api.api_v1_deployments_post(
                new_deployment)
            print(
                f"Create deployment response: {create_deployment_response}.")

            if not create_deployment_response:
                print("Unable to create deployment object")
                continue
            deloyment_dsi_id = create_deployment_response.deployment_id
            deployment_obj.extra_data["dsi_upload"] = datetime.datetime.now()
            deployment_obj.extra_data["dsi_id"] = deloyment_dsi_id
            deployment_obj.save()

            deployment_datafiles = datafile_objs.filter(
                deployment=deployment_obj)

            objects_to_update = []
            # For each media item of this deployment
            for datafile_obj in deployment_datafiles:
                # Create media item
                media_file_path = datafile_obj.full_path()
                with open(media_file_path, "rb") as media_file:
                    file_bytes = media_file.read()
                    files = [(datafile_obj.original_name, file_bytes)]

                    media_api.api_v1_media_upload_post(
                        deployment_id=create_deployment_response.deployment_id, file=files)

                datafile_obj.extra_data["dsi_upload"] = datetime.datetime.now()
                objects_to_update.append(datafile_obj)
