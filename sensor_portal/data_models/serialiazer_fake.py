from rest_framework import serializers
from utils.serializers import DummyJSONField

from .serializers import DeploymentSerializer


class DummyDeploymentSerializer(DeploymentSerializer):
    """

    """

    user_is_owner = serializers.BooleanField(
        read_only=True, default=False, required=False)

    user_is_manager = serializers.BooleanField(
        read_only=True, default=False, required=False)

    colour = serializers.CharField(
        read_only=True, default="blue", required=False)
    symbol = serializers.CharField(
        read_only=True, default="camera", required=False)

    extra_data = DummyJSONField(
        required=False, help_text="Extra taxon data that the standard fields do not cover.")
