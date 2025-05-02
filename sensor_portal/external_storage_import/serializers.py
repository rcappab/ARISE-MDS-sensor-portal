from rest_framework import serializers
from utils.serializers import CreatedModifiedMixIn, OwnerMixIn

from .models import DataStorageInput


class DataStorageInputSerializer(OwnerMixIn, CreatedModifiedMixIn, serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = DataStorageInput
        exclude = []

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_datastorageinput'
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        initial_rep = super().to_representation(instance)
        fields_to_pop = [
            "username",
            "address"
        ]

        if self.context.get('request'):
            user_is_manager = self.context['request'].user.has_perm(
                self.management_perm, obj=instance)
        else:
            user_is_manager = False
        if not user_is_manager:
            [initial_rep.pop(field, '') for field in fields_to_pop]

        return initial_rep
