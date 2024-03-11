from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, m2m_changed, pre_save
from data_models.models import Project

class User(AbstractUser):
    pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not getattr(instance, 'from_admin_site', False):
        if created:
            Token.objects.create(user=instance)


class GroupProfile(models.Model):
    usergroup = models.OneToOneField(Group, on_delete=models.CASCADE,related_name='profile')
    project = models.ManyToManyField(Project, related_name="usergroup")

    def __str__(self):
        return (self.usergroup.name + " profile")


@receiver(post_save, sender=Group)
def create_user_group_profile(sender, instance, created, **kwargs):
    if not getattr(instance, 'from_admin_site', False):
        if created:
            GroupProfile.objects.create(usergroup=instance)


@receiver(post_save, sender=Group)
def save_user_group_profile(sender, instance, **kwargs):
    if not getattr(instance, 'from_admin_site', False):
        instance.profile.save()