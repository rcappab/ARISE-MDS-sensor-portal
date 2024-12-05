from datetime import datetime, timedelta, tzinfo
from random import sample

import factory
import pytz
from django.utils import timezone as djtimezone
from user_management.factories import UserFactory

from .models import DataType, Deployment, Device, DeviceModel, Project, Site


class DataTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DataType
        django_get_or_create = ("name",)

    name = factory.Faker('random_element',
                         elements=["test_type_1", "test_type_2", "test_type_3"])


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site
        django_get_or_create = ("name",)

    name = factory.Faker('word')


class DeviceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeviceModel
        django_get_or_create = ("name",)

    name = factory.Faker('word')
    type = factory.SubFactory(DataTypeFactory)


class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device
        django_get_or_create = ("device_ID",)

    device_ID = factory.Faker('word')
    name = factory.Faker('word')
    model = factory.SubFactory(DeviceModelFactory)
    type = None


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        django_get_or_create = ("name",)

    name = factory.Faker('word')


class DeploymentFactory(factory.django.DjangoModelFactory):
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
        if not create:
            # Simple build do nothing.
            return
        if extracted is None:
            for i in range(sample(range(3), 1)[0]):
                self.project.add(ProjectFactory())
