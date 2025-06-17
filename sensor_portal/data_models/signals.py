from django.conf import settings
from django.db.models.signals import (m2m_changed, post_delete, post_save,
                                      pre_delete)
from django.dispatch import receiver

from .models import DataFile, Deployment, Project

# Deployment signals


@receiver(post_save, sender=Deployment)
def post_save_deploy(sender, instance, created, **kwargs):

    global_project, added = Project.objects.get_or_create(
        name=settings.GLOBAL_PROJECT_ID)

    if global_project not in instance.project.all():
        instance.project.add(global_project)


@receiver(m2m_changed, sender=Deployment.project.through)
def update_project(sender, instance, action, reverse, *args, **kwargs):

    if (action == 'post_add' or action == 'post_remove') and not reverse:
        instance.save()


# DataFile signals

@receiver(post_save, sender=DataFile)
def post_save_file(sender, instance, created, **kwargs):
    instance.deployment.set_thumb_url()
    instance.deployment.save()


@receiver(pre_delete, sender=DataFile)
def pre_remove_file(sender, instance: DataFile, **kwargs):
    # deletes the attached file from data storage
    success = instance.clean_file(True)
    if not success:
        raise (Exception(f'Unable to delete file {instance.file_name}'))


@receiver(post_delete, sender=DataFile)
def post_remove_file(sender, instance: DataFile, **kwargs):
    instance.deployment.set_thumb_url()
    instance.deployment.save()
