from django.conf import settings
from django.db.models.signals import (m2m_changed, post_delete, post_save,
                                      pre_delete)
from django.dispatch import receiver

from .models import DataFile, Deployment, Project

# Deployment signals


@receiver(post_save, sender=Deployment)
def post_save_deploy(sender, instance: Deployment, created, **kwargs):
    """
    Post save signal for Deployment model to ensure that the global project
    is always associated with the deployment instance.

    """

    global_project, added = Project.objects.get_or_create(
        name=settings.GLOBAL_PROJECT_ID)

    if global_project.pk not in instance.project.all().values_list('pk', flat=True):
        instance.project.add(global_project)


@receiver(m2m_changed, sender=Deployment.project.through)
def update_project(sender, instance, action, reverse, *args, **kwargs):
    """
    Signal to update the deployment's project when the many-to-many
    relationship changes. This ensures that the combination project field is updated.

    """
    if (action == 'post_add' or action == 'post_remove') and not reverse:
        instance.save()


# DataFile signals

@receiver(post_save, sender=DataFile)
def post_save_file(sender, instance: DataFile, created, **kwargs):
    """
    Post save signal for DataFile model to update the deployment's thumbnail URL.
    """
    instance.deployment.set_thumb_url()
    instance.deployment.save()


@receiver(pre_delete, sender=DataFile)
def pre_remove_file(sender, instance: DataFile, **kwargs):
    """
    Pre delete signal for DataFile model to clean up the attached file before deletion.

    """
    # deletes the attached file from data storage
    success = instance.clean_file(True)
    if not success:
        raise (
            Exception(f'Unable to delete datafile object {instance.file_name}'))


@receiver(post_delete, sender=DataFile)
def post_remove_file(sender, instance: DataFile, **kwargs):
    """
    Post delete signal for DataFile model to update the deployment's thumbnail URL after a file is deleted.
    """
    instance.deployment.set_thumb_url()
    instance.deployment.save()
