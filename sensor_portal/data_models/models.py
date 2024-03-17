from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_delete, m2m_changed, post_delete
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Sum, F, Q, BooleanField, ExpressionWrapper, Case, When, DateTimeField
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_projects",
                              on_delete=models.SET_NULL, null=True)
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
        groupname = f"{instance.projectID}_project_group"
        try:
            usergroup = Group.objects.get(name=groupname)
        except ObjectDoesNotExist:
            usergroup = Group(name=groupname)
            usergroup.save()
        usergroup_profile = usergroup.profile
        usergroup_profile.project.add(instance)
        usergroup_profile.save()


class Device(Basemodel):
    deviceID = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    make = models.CharField(max_length=200, blank=True)
    type = models.ForeignKey(DataType, models.PROTECT, related_name="devices")

    # User ownership
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_devices",
                              on_delete=models.SET_NULL, null=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="managed_devices")


    autoupdate = models.BooleanField(default=False)
    update_time = models.IntegerField(default=48)

    username = models.CharField(max_length=100, unique=True, null=True, blank=True, default=None)
    authentication = models.CharField(max_length=100, blank=True, null=True)
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

        # For deployments that have not ended - end date is shifted 100 years

        all_deploys = all_deploys.annotate(deploymentEnd_indefinite=
        Case(
            When(deploymentEnd__isnull=True,
                 then=ExpressionWrapper(
                     F('deploymentStart') + timedelta(days=365 * 100),
                     output_field=DateTimeField()
                 )
                 ),
            default=F('deploymentEnd')
        )
        )

        # Annotate by whether the datetime lies in the deployment range

        all_deploys = all_deploys.annotate(in_deployment=
        ExpressionWrapper(
            Q(Q(deploymentStart__lte=dt) & Q(deploymentEnd_indefinite__gte=dt)),
            output_field=BooleanField()
        )
        )

        try:
            correct_deployment = all_deploys.get(in_deployment=True)
            return correct_deployment
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            # Check for complete failure or ambiguity
            all_true_deployments = all_deploys.filter(in_deployment=True)
            print(f"Error: found {all_true_deployments.count()} deployments")
            return None



@receiver(post_save, sender=Device)
def post_save_device(sender, instance, created, **kwargs):
    if created:
        groupname = f"{instance.deviceID}_device_group"
        try:
            usergroup = Group.objects.get(name=groupname)
        except ObjectDoesNotExist:
            usergroup = Group(name=groupname)
            usergroup.save()
        usergroup_profile = usergroup.profile
        usergroup_profile.device.add(instance)
        usergroup_profile.save()



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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_deployments",
                              on_delete=models.SET_NULL, null=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="managed_deployments")

    combo_project = models.CharField(max_length=100, blank=True, null=True, editable=False)
    last_image = models.ForeignKey("DataFile", blank=True, on_delete=models.SET_NULL, null=True, editable=False,
                                   related_name="deployment_last_image")
    last_file = models.ForeignKey("DataFile", blank=True, on_delete=models.SET_NULL, null=True, editable=False,
                                  related_name="deployment_last_file")
    last_imageURL = models.CharField(max_length=500, null=True, blank=True, editable=False)

    def get_absolute_url(self):
        return reverse('deployment-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.deployment_deviceID

    def save(self, *args, **kwargs):
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

    def get_combo_project(self):
        if self.project.all().exists:
            all_proj_id = list(self.project.all().values_list("projectID", flat=True))
            all_proj_id.sort()
            return " ".join(all_proj_id)
        else:
            return ""

    def check_active(self):
        if self.id:
            if self.deploymentStart <= djtimezone.now():
                if self.deploymentEnd is None or self.deploymentEnd >= djtimezone.now():
                    return True

        return False

    def set_last_file(self,newfile=None):
        try:
            if self.files.exists():
                file_object = self.files.all().latest('recording_dt')
            elif newfile is not None:
                if self.last_file is None:
                    file_object = newfile
            if file_object is not None:
                self.last_file = file_object
                self.set_last_image()
                self.save()

        except:
            print(traceback.format_exc())
            pass

    def set_last_image(self):
        if self.last_file:
            #check for thumbnail first
            if self.last_file.file_format.lower() in [".jpg",".jpeg"]:
                self.last_image = self.last_file
                self.last_imageURL = self.last_file.file_url
@receiver(post_save, sender=Deployment)
def post_save_deploy(sender, instance, created, **kwargs):
    if created:
        groupname = f"{instance.deployment_deviceID}_deployment_group"
        try:
            usergroup = Group.objects.get(name=groupname)
        except ObjectDoesNotExist:
            usergroup = Group(name=groupname)
            usergroup.save()
        usergroup_profile = usergroup.profile
        usergroup_profile.deployment.add(instance)
        usergroup_profile.save()

    global_project = get_global_project()
    if global_project not in instance.project.all():
        instance.project.add(global_project)
        # RefreshDeploymentCache()
        # print("Clear deployment cache")
        # cache.delete_many(["allowed_deployments_{0}".format(x) for x in User.objects.all().values_list("username",flat=True)])


@receiver(m2m_changed, sender=Deployment.project.through)
def update_project(sender, instance, action, reverse, *args, **kwargs):
    if (action == 'post_add' or action == 'post_remove') and not reverse:
        combo_project = instance.get_combo_project()
        Deployment.objects.filter(pk=instance.pk).update(combo_project=combo_project)

@receiver(post_delete, sender=Device)
@receiver(post_delete, sender=Deployment)
@receiver(post_delete, sender=Project)
def clear_user_groups(sender, instance, **kwargs):
    all_groups = Group.objects.all()
    all_groups = all_groups.annotate(
        all_is_null=ExpressionWrapper(
            (Q(Q(profile__project=None) & Q(profile__device=None) & Q(profile__deployment=None))),
            output_field=BooleanField()
        )
    )
    all_groups.filter(all_is_null=True).delete()

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

    do_not_remove = models.BooleanField(default=False)
    original_name = models.CharField(max_length=100, blank=True, null=True)

    file_url = models.CharField(max_length=500, null=True, blank=True)
    tag = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.file_name}{self.file_format}"

    def get_absolute_url(self):
        return reverse('file-detail', kwargs={'pk': self.pk})

    def add_favourite(self, user):
        self.favourite_of.add(user)
        self.save()

    def remove_favourite(self, user):
        self.favourite_of.remove(user)
        self.save()

    def set_file_url(self):
        if self.localstorage:

            self.file_url = os.path.normpath(
                os.path.join(settings.FILE_STORAGE_URL,
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

    def clean_file(self, delete_obj=False):
        if (self.do_not_remove or self.deployment_last_image.exists or self.deployment_last_file.exists) and not delete_obj:
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

        if not delete_obj:
            self.localstorage = False
            self.local_path = ""
            self.extra_reps = {}
            self.thumb_path = None
            self.save()
        else:
            self.deployment.set_last_file()

    def save(self, *args, **kwargs):
        self.set_file_url()
        super().save(*args, **kwargs)


@receiver(post_save,sender=DataFile)
def post_save_file(sender,instance,created, **kwargs):
    # if created:
    # print("Refresh file cache")
    # RefreshFileCache()

    # cache.delete_many(["allowed_files_{0}".format(x) for x in User.objects.all().values_list("username",flat=True)])
    instance.deployment.set_last_file(instance)
    # if instance.format.lower() in [".jpg",".jpeg",".png",".dat"]:
    #    instance.deployment.SetLastImage(instance)


@receiver(pre_delete, sender=DataFile)
def remove_file(sender, instance, **kwargs):
    # deletes the attached file form data storage
    instance.clean_file(True)
