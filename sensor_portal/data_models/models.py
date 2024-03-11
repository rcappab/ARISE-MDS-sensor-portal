from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_delete, m2m_changed, pre_save
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, ExpressionWrapper, F, Q
from django.utils import timezone as djtimezone
from sizefield.models import FileSizeField
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gis_models

import pytz
import dateutil.parser
import traceback
from datetime import datetime, timedelta, timezone, time
import os


class Basemodel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def model_name(self):
        return self._meta.model_name


class Site(Basemodel):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class DataType(Basemodel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Project(Basemodel):
    # Metadata
    projectID = models.CharField(max_length=10, unique=True)
    projectName = models.CharField(max_length=50)
    projectObjectives = models.CharField(max_length=500, blank=True)
    countryCode = models.CharField(max_length=10, blank=True)
    principalInvestigator = models.CharField(max_length=50, blank=True)
    principalInvestigatorEmail = models.CharField(max_length=100, blank=True)
    projectContact = models.CharField(max_length=50, blank=True)
    projectContactEmail = models.CharField(max_length=100, blank=True)
    organizationName = models.CharField(max_length=100, blank=True)

    # User ownership
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_projects", on_delete=models.SET_NULL , null=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="managed_projects")

    # Archiving
    archive_files = models.BooleanField(default=True)
    clean_time = models.IntegerField(default=90)

    def __str__(self):
        return self.projectID

    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'pk': self.pk})


def get_global_project():
    try:
        global_project = Project.objects.get(projectID=settings.GLOBAL_PROJECT_ID)
        return global_project
    except ObjectDoesNotExist:
        global_project = Project(projectID=settings.GLOBAL_PROJECT_ID,
                                 projectName=settings.GLOBAL_PROJECT_ID,
                                 projectObjectives="Global project for all deployments")
        global_project.save()
        return global_project
    except:
        print(" Error: " + traceback.format_exc())
        pass


@receiver(post_save, sender=Project)
def post_save_project(sender, instance, created, **kwargs):
    if created:
        project_group = Group(name=f"{instance.projectID}_project_group")
        project_group.save()
        project_group_profile = project_group.profile
        project_group_profile.project.add(instance)
        project_group_profile.save()

class Device(Basemodel):
    deviceID = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    make = models.CharField(max_length=200, blank=True)
    type = models.ForeignKey(DataType, models.PROTECT, related_name="devices")

    # User ownership
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_devices", on_delete=models.SET_NULL, null=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="managed_devices")

    autoupdate = models.BooleanField(default=False)
    update_time = models.IntegerField(default=48)

    username = models.CharField(max_length=100, unique=True, null=True, blank=True, default=None)
    authentication = models.CharField(max_length=100, blank=True)
    extra_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.deviceID

    def get_absolute_url(self):
        return reverse('device-detail', kwargs={'pk': self.pk})

    def deployment_from_date(self, dt, user=None):
        if type(dt) is str:
            dt = dateutil.parser.parse(dt)

        if dt.tzinfo is None:
            mytz = pytz.timezone(settings.TIME_ZONE)
            dt = mytz.localize(dt)

        if user is None:
            all_deploys = self.deployments.all()

        # else:
        #    all_deploys, count = GetAllowedDeployments(user)
        #    all_deploys = alldeploys.filter(device=self)

        # annotate list of deployments with booleans

        # ranges = [x.getdt() for x in alldeploys]
        # deploybool = [gf.in_range_tuple(x, dt) for x in ranges]
        # if (sum(deploybool) == 0) | (sum(deploybool) > 1):
        #     return None
        # currdeploy_obj = [alldeploys[i] for i in range(alldeploys.count()) if deploybool[i]][0]
        # return currdeploy_obj


class Deployment(Basemodel):
    deployment_deviceID = models.CharField(max_length=100, blank=True, editable=False, unique=True)
    deploymentID = models.CharField(max_length=50)
    device_type = models.ForeignKey(DataType, models.PROTECT, related_name="deployments")
    device_n = models.IntegerField(default=1)

    deploymentStart = models.DateTimeField(default=djtimezone.now)
    deploymentEnd = models.DateTimeField(blank=True, null=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="deployments")
    project = models.ManyToManyField(Project, related_name="deployments", blank=True)

    Latitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True)
    Longitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True)
    point = gis_models.PointField(
        blank=True,
        null=True,
        spatial_index=True
    )

    site = models.ForeignKey(Site, models.PROTECT, related_name="deployments")
    extra_info = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    # User ownership
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_deployments", on_delete=models.SET_NULL, null=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="managed_deployments")

    combo_project = models.CharField(max_length=100, blank=True, null=True, editable=False)
    last_image = models.ForeignKey("DataFile", blank=True, on_delete=models.SET_NULL, null=True, editable=False,
                                   related_name="last_image_of_deployment")
    last_file = models.ForeignKey("DataFile", blank=True, on_delete=models.SET_NULL, null=True, editable=False,
                                  related_name="last_file_of_deployment")
    last_imageURL = models.CharField(max_length=500, null=True, blank=True, editable=False)

    def get_absolute_url(self):
        return reverse('deployment-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.deployment_deviceID

    def save(self, *args, **kwargs):
        print("save")
        self.deployment_deviceID = f"{self.deploymentID}_{self.device_type.name}_{self.device_n}"
        self.is_active = self.check_active()

        if self.Longitude and self.Latitude:
            self.point = Point(
                float(self.Longitude),
                float(self.Latitude),
                srid=4326
            )
        elif (not self.Longitude and not self.Latitude) and self.point:
            self.Longitude, self.Latitude = self.point.coords
        else:
            self.point = None

        super().save(*args, **kwargs)
        global_project = get_global_project()
        if global_project not in self.project.all():
            self.project.add(global_project)


    def get_combo_project(self):
        if self.project.all().exists:
            allprojids = list(self.project.all().values_list("projectID", flat=True))
            allprojids.sort()
            return " ".join(allprojids)
        else:
            return ""

    def check_active(self):
        if self.id:
            if self.deploymentStart <= djtimezone.now():
                if self.deploymentEnd is None or self.deploymentEnd >= djtimezone.now():
                    return True

        return False


# @receiver(post_save, sender=Deployment)
# def post_save_deploy(sender, instance, created, **kwargs):
#     print(f"post_save_deploy {sender} {instance} {instance.project.all()} {kwargs}")
#     if created:
#         print("post_save_deploy created")
#         active = instance.check_active()
#         Deployment.objects.filter(pk=instance.pk).update(is_active=active)
#     global_project = get_global_project()
#     if global_project not in instance.project.all():
#         instance.project.add(global_project)
#         # RefreshDeploymentCache()
#         # print("Clear deployment cache")
#         # cache.delete_many(["allowed_deployments_{0}".format(x) for x in User.objects.all().values_list("username",flat=True)])
#         #instance.get_combo_project()


@receiver(m2m_changed, sender=Deployment.project.through)
def update_project(sender, instance, action, reverse, *args, **kwargs):
    print(f"update_project {instance.project.all()} {sender} {instance} {action} {args} {kwargs}")
    print(instance.project.all())
    if (action == 'post_add' or action == 'post_remove') and not reverse:
        combo_project = instance.get_combo_project()
        Deployment.objects.filter(pk=instance.pk).update(combo_project=combo_project)
        print(f"{action} {instance.project.all()}")


class DataFile(Basemodel):
    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE, related_name="files")

    file_type = models.ForeignKey(DataType, models.PROTECT, related_name="files")
    file_name = models.CharField(max_length=100)
    file_size = FileSizeField()
    file_format = models.CharField(max_length=100)

    download_date = models.DateField(auto_now_add=True)
    recording_dt = models.DateTimeField(null=True, db_index=True)
    path = models.CharField(max_length=500)
    local_path = models.CharField(max_length=500, blank=True)

    extra_info = models.JSONField(default=dict, blank=True)
    extra_reps = models.JSONField(default=dict, blank=True)
    thumb_path = models.JSONField(default=None, blank=True, null=True)

    localstorage = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    # tarfile = models.ForeignKey(TarFile, on_delete=models.SET_NULL, blank=True, null=True, related_name="Files")
    favourite_of = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="favourites")

    do_not_delete = models.BooleanField(default=False)
    original_name = models.CharField(max_length=100, blank=True, null=True)

    file_url = models.CharField(max_length=500, null=True, blank=True)
    tag = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.file_name + self.file_file_format

    def get_absolute_url(self):
        return reverse('file-detail', kwargs={'pk': self.pk})

    def add_favourite(self, user):
        self.favourite_of.add(user)
        self.save()

    def set_file_url(self):
        if self.localstorage:
            self.file_url = os.path.normpath(
                    os.path.join(settings.EXPORT_URL,
                                  os.path.join(*[x for x in
                                                 os.path.normpath(self.local_path).split(os.sep)
                                                 if x not in ['media', 'file_storage']
                                                 ]),
                                  self.path,
                                  (self.file_name + self.file_format))
                    ).replace("\\", "/")
            # if not self.thumbpath:
            # last_images = self.DeployLastIm.all()
            # if lastim.exists() and self.deployment:
            #    self.deployment.GetLastImageURL()
            #    self.deployment.save()
        else:
            self.file_url = None

    def clean_file(self, remove_obj=False):
        if self.bundling:
            return
        if self.localstorage:
            try:
                os.remove(self.fullpath())

            except:
                pass
        try:
            os.remove(self.thumbpath["filepath"])
        except:
            pass

        for v in self.extrareps.values():
            try:
                os.remove(v["filepath"])
            except:
                pass

        if not remove_obj:
            self.localstorage = False
            self.local_path = ""
            self.extra_reps = {}
            self.thumb_path = None
            self.save()

    def save(self, *args, **kwargs):
        self.set_file_url()
        super().save(*args, **kwargs)


@receiver(post_save,sender=DataFile)
def post_save_file(sender,instance,created, **kwargs):
    if created:
        #print("Refresh file cache")
        #RefreshFileCache()

        #cache.delete_many(["allowed_files_{0}".format(x) for x in User.objects.all().values_list("username",flat=True)])
        instance.deployment.SetLastFile(instance)
        if instance.format.lower() in [".jpg",".jpeg",".png",".dat"]:
            instance.deployment.SetLastImage(instance)


@receiver(pre_delete,sender=DataFile)
def RemoveFile(sender, instance, **kwargs):
    instance.CleanFile(True)

