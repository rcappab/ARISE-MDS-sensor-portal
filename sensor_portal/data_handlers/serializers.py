from rest_framework import serializers


class DataHandlerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    data_types = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True
    )
    device_models = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True
    )
    safe_formats = serializers.ListField(
        child=serializers.CharField(max_length=10),
        allow_empty=True
    )
    full_name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    validity_description = serializers.CharField(max_length=500)
    handling_description = serializers.CharField(max_length=500)
    post_handling_description = serializers.CharField(max_length=500)
