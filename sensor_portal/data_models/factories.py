import os
from datetime import datetime, timedelta, tzinfo
from random import sample

import factory
import pytz
from django.conf import settings
from django.utils import timezone as djtimezone
from user_management.factories import UserFactory

from .general_functions import create_image
from .models import (DataFile, DataType, Deployment, Device, DeviceModel,
                     Project, Site)


class DataTypeFactory(factory.django.DjangoModelFactory):
    """
    DataTypeFactory is a factory class for creating instances of the DataType model
    using the Factory Boy library. It is configured to use Django's ORM for model
    creation and ensures that instances are uniquely identified by the "name" field.
    Attributes:
        Meta:
            model (DataType): Specifies the model class to be used for instance creation.
            django_get_or_create (tuple): Ensures that instances are retrieved or created
                based on the "name" field.
        name (str): A randomly generated name for the DataType instance, chosen from
            the predefined list ["test_type_1", "test_type_2", "test_type_3"].
    """

    class Meta:
        model = DataType
        django_get_or_create = ("name",)

    name = factory.Faker('random_element',
                         elements=["test_type_1", "test_type_2", "test_type_3"])


class SiteFactory(factory.django.DjangoModelFactory):
    """
    SiteFactory is a factory class for creating instances of the Site model 
    using the factory_boy library. It is configured to use Django's ORM 
    and ensures that instances are uniquely identified by the "name" field.
    Attributes:
        Meta:
            model (Site): Specifies the Django model associated with this factory.
            django_get_or_create (tuple): Ensures that the factory retrieves or 
                creates a Site instance based on the "name" field.
        name (str): A randomly generated word used as the name of the Site instance.
    """

    class Meta:
        model = Site
        django_get_or_create = ("name",)

    name = factory.Faker('word')


class DeviceModelFactory(factory.django.DjangoModelFactory):
    """
    DeviceModelFactory is a factory class for creating instances of the DeviceModel Django model.
    It uses the factory_boy library to simplify the creation of test data for the DeviceModel model.
    Attributes:
        Meta:
            model (DeviceModel): Specifies the Django model associated with this factory.
            django_get_or_create (tuple): Ensures that objects are retrieved or created based on the "name" field.
        name (str): A randomly generated word representing the name of the device model.
        type (DataTypeFactory): A subfactory that generates instances of the DataType model associated with the device model.
    """

    class Meta:
        model = DeviceModel
        django_get_or_create = ("name",)

    name = factory.Faker('word')
    type = factory.SubFactory(DataTypeFactory)


class DeviceFactory(factory.django.DjangoModelFactory):
    """
    DeviceFactory is a factory class for creating instances of the Device model 
    using the Factory Boy library. It is designed to simplify the creation of 
    test data for the Device model in Django applications.
    Attributes:
        device_ID (str): A randomly generated word representing the unique identifier of the device.
        name (str): A randomly generated word representing the name of the device.
        model (DeviceModelFactory): A subfactory that generates instances of the DeviceModel associated with the device.
        type (None): Placeholder for the type attribute, which is not currently set.
    Meta:
        model (Device): Specifies the Django model that this factory is associated with.
        django_get_or_create (tuple): Ensures that the factory will attempt to retrieve an existing Device instance 
                                      based on the "device_ID" field before creating a new one.
    """

    class Meta:
        model = Device
        django_get_or_create = ("device_ID",)

    device_ID = factory.Faker('word')
    name = factory.Faker('word')
    model = factory.SubFactory(DeviceModelFactory)
    type = None


class ProjectFactory(factory.django.DjangoModelFactory):
    """
    ProjectFactory is a factory class for creating instances of the Project model
    using the Factory Boy library. It is designed to simplify the creation of
    test data for the Project model in Django applications.
    Attributes:
        Meta:
            model (Project): Specifies the Django model that this factory generates.
            django_get_or_create (tuple): Ensures that objects are retrieved or created
                based on the specified fields ('name').
        name (str): A randomly generated word used as the name of the Project instance.
    """

    class Meta:
        model = Project
        django_get_or_create = ("name",)

    name = factory.Faker('word')


class DeploymentFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating Deployment model instances using Factory Boy.
    Attributes:
        deployment_ID (str): A randomly generated word representing the deployment ID.
        device_type (str): The type of device associated with the deployment. Defaults to None.
        device_n (int): A randomly generated integer between 0 and 100 representing the device number.
        deployment_start (datetime): A randomly generated datetime between January 1, 2020, and the current date.
        deployment_end (datetime or None): A conditional datetime generated based on deployment_start, or None.
        device (DeviceFactory): A sub-factory for creating associated Device instances.
        site (SiteFactory): A sub-factory for creating associated Site instances.
    Methods:
        project(create, extracted, **kwargs):
            Handles post-generation logic for the 'project' attribute. If 'extracted' is provided, it adds the
            extracted projects to the deployment. If 'extracted' is None, it randomly generates and adds projects.
    """

    class Meta:
        model = Deployment
        django_get_or_create = (
            "deployment_ID", "device_type", "device_n")

    deployment_ID = factory.Faker('word')
    device_type = None
    device_n = factory.Faker('random_int', min=0, max=100)

    deployment_start = factory.Faker('date_time_between_dates',
                                     datetime_start=datetime(
                                         2020, 1, 1, 0, 0, 0),
                                     tzinfo=djtimezone.utc)

    deployment_end = factory.Maybe(
        factory.Faker('pybool'),

        factory.Faker('date_time_between_dates',
                      datetime_start=factory.SelfAttribute(
                          "..deployment_start"),
                      tzinfo=djtimezone.utc
                      )
    )

    device = factory.SubFactory(DeviceFactory)
    site = factory.SubFactory(SiteFactory)

    @factory.post_generation
    def project(self, create, extracted, **kwargs):
        """
        Handles the creation or addition of projects to the current instance.
        Args:
            create (bool): Determines whether to create new projects. If False, no action is taken.
            extracted (iterable or None): A collection of existing projects to add. If None, new projects are generated.
            **kwargs: Additional keyword arguments that may be passed.
        Behavior:
            - If `create` is False, the method does nothing.
            - If `extracted` is provided, it adds each project in the collection to the current instance.
            - If `extracted` is None, it generates a random number of new projects using `ProjectFactory` and adds them to the current instance.
        """

        if not create:
            # Simple build do nothing.
            return
        if extracted:
            for current_project in extracted:
                self.project.add(current_project)
        elif extracted is None:
            for i in range(sample(range(3), 1)[0]):
                self.project.add(ProjectFactory())


class DataFileFactory(factory.django.DjangoModelFactory):
    """
    DataFileFactory is a factory class for creating instances of the DataFile model 
    using the Factory Boy library. This factory is designed to generate realistic 
    test data for the DataFile model, including attributes such as file name, file 
    size, file format, upload date, deployment, recording date, and file path.
    Attributes:
        file_name (str): A randomly generated word representing the file name.
        file_size (int): A randomly generated integer between 25 and 100,000 
            representing the file size in bytes.
        file_format (str): The file format, defaulting to ".JPG".
        upload_dt (datetime): The upload date and time, set to the current timezone-aware datetime.
        deployment (DeploymentFactory): A sub-factory for creating associated Deployment instances.
        recording_dt (datetime): A randomly generated datetime between the deployment start 
            and end times, with UTC timezone.
        local_path (str): The root directory for file storage, derived from settings.FILE_STORAGE_ROOT.
        path (str): A lazy attribute that generates the relative path for the file based on 
            deployment device ID and upload date.
    Methods:
        make_image(create, extracted, **kwargs):
            A post-generation hook that creates a test image file in the specified path 
            if the instance is being created (not just built). The image is saved in JPEG format.
    """

    class Meta:
        model = DataFile
        django_get_or_create = (
            "file_name", "file_format")

    file_name = factory.Faker('word')
    file_size = factory.Faker('random_int', min=25, max=100000)
    file_format = ".JPG"  # factory.Faker('file_extension')
    upload_dt = djtimezone.now()

    deployment = factory.SubFactory(DeploymentFactory)

    recording_dt = factory.Faker('date_time_between_dates',
                                 datetime_start=factory.SelfAttribute(
                                     "..deployment.deployment_start"),
                                 datetime_end=factory.SelfAttribute(
                                     "..deployment.deployment_end"),
                                 tzinfo=djtimezone.utc
                                 )
    local_path = os.path.join(
        settings.FILE_STORAGE_ROOT)

    path = factory.LazyAttribute(lambda o: os.path.join("test",
                                                        o.deployment.deployment_device_ID, str(o.upload_dt.date())))

    @factory.post_generation
    def make_image(self, create, extracted, **kwargs):
        """
        Creates and saves an image file at the specified path.
        Args:
            create (bool): If True, the method will create and save an image. 
                   If False, the method will do nothing.
            extracted (Any): Placeholder for additional extracted data (not used in this method).
            **kwargs: Additional keyword arguments (not used in this method).
        Returns:
            None
        Notes:
            - If `create` is True, the method ensures the directory structure exists 
              by creating necessary directories.
            - A test image is generated using `create_image()` and saved in JPEG format 
              at the location specified by `self.full_path()`.
        """

        if not create:
            # Simple build do nothing.
            return
        else:
            os.makedirs(os.path.join(self.local_path,
                        self.path), exist_ok=True)
            test_image = create_image()
            test_image.save(self.full_path(), format="JPEG")
