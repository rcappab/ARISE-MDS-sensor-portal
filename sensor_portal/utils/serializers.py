from rest_framework import serializers


class SlugRelatedGetOrCreateField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail("invalid")
