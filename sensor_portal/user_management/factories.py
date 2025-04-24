import factory
from django.db.models.signals import post_save, pre_save

from .models import User


@factory.django.mute_signals(post_save, pre_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username", )

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("email")
    is_staff = False
    is_active = True
