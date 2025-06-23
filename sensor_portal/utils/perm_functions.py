from data_models.models import Deployment, Device, Project
from user_management.models import User


def cascade_permissions(instance: Project | Deployment | Device):
    """
    Cascade permissions from owner through to viewer. This allows simpler queries.

    Args:
        instance (Project | Deployment | Device): Object on which to cascade permissions
    """
    # OWNER SHOULD BE MANAGER
    if instance.owner is not None:
        instance.managers.add(instance.owner)

    # MANAGERS SHOULD BE ANNOTATORS
    instance.annotators.add(*instance.managers.all())

    # ANNOTATORS SHOULD BE VIEWERS
    instance.viewers.add(*instance.annotators.all())


def remove_user_permissions(user: User, instance: Project | Deployment | Device):
    if instance.owner is not None:
        if user == instance.owner:
            return
    instance.managers.remove(user)
    instance.annotators.remove(user)
    instance.viewers.remove(user)
