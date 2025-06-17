from data_models.job_handling_functions import register_job

from sensor_portal.celery import app

from .api_functions import post_data


@app.task(name="push_to_dsi")
@register_job("Push to ARISE DSI", "push_to_dsi", "datafile", True,
              default_args={"dsi_project_id": 1, "dsi_site_id": 1})
def push_to_dsi_task(datafile_pks, dsi_project_id, dsi_site_id):
    post_data(media_pks=datafile_pks, dsi_project_id=dsi_project_id,
              dsi_site_id=dsi_site_id)
