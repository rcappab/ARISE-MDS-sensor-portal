from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   OpenApiTypes, extend_schema,
                                   extend_schema_field,
                                   extend_schema_serializer)
from rest_framework import serializers
from utils.serializers import (CheckFormMixIn, CreatedModifiedMixIn,
                               DummyJSONField, OwnerMixIn,
                               SlugRelatedGetOrCreateField)
from utils.validators import check_two_keys

from .models import Observation, Taxon


class TaxonSerializer(CreatedModifiedMixIn, serializers.ModelSerializer):
    taxonomic_level_name = serializers.CharField(
        source="get_taxonomic_level_display", read_only=True)

    class Meta:
        model = Taxon
        exclude = []


class ShortTaxonSerializer(serializers.ModelSerializer):

    taxonomic_level_name = serializers.CharField(
        source="get_taxonomic_level_display", read_only=True)

    class Meta:
        model = Taxon
        exclude = ["id", "created_on", "modified_on", "parents"]

    def to_representation(self, instance):
        initial_rep = super(ShortTaxonSerializer,
                            self).to_representation(instance)
        initial_rep["taxon_extra_data"] = initial_rep.pop("extra_data")

        return initial_rep


class EvenShorterTaxonSerialier(serializers.ModelSerializer):

    class Meta:
        model = Taxon
        fields = ["id", "species_name", "species_common_name", "taxon_source"]

    def to_representation(self, instance):
        initial_rep = super(EvenShorterTaxonSerialier,
                            self).to_representation(instance)
        initial_rep["full_string"] = f"{initial_rep.get('species_name')} - {initial_rep.get('species_common_name')}"
        return initial_rep


@extend_schema_field({"type": ["object"],
                      "readOnly": False,
                      "default": {},
                      "description": "Bounding box of this observation",
                      'examples': [{"x1": 0, "y1": 0, "x2": 1, "y2": 1}],
                      "properties": {"x1": {"type": "number",
                                            "description": "Left coordinate",
                                            "required": True, },
                                     "y1": {"type": "number",
                                            "description": "Bottom coordinate",
                                            "required": True},
                                     "x2": {"type": "number",
                                            "description": "Right coordinate",
                                            "required": True},
                                     "y2": {"type": "number",
                                            "description": "Top coordinate",
                                            "required": True}},
                      "required": False,
                      })
class BBoxField(DummyJSONField):
    pass


@extend_schema_serializer(component_name="ObservationSerializer",
                          )
class DummyObservationSerializer(OwnerMixIn, CreatedModifiedMixIn, serializers.ModelSerializer):
    """
    For use in the API schema.
    """
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all(),
        required=False)
    species_name = SlugRelatedGetOrCreateField(many=False,
                                               source="taxon",
                                               slug_field="species_name",
                                               queryset=Taxon.objects.all(),
                                               allow_null=True,
                                               required=False,
                                               read_only=False)
    user_is_owner = serializers.BooleanField(
        read_only=True, default=False, required=False)
    taxonomic_level_name = serializers.CharField(
        read_only=True, default="species", required=False)
    species_common_name = serializers.CharField(read_only=True, required=False)
    taxon_code = serializers.CharField(read_only=True, required=False)
    taxon_source = serializers.IntegerField(
        read_only=True, default=0, required=False)
    taxonomic_level = serializers.IntegerField(
        read_only=True, default=0, required=False)
    taxon_extra_data = serializers.SerializerMethodField(
        read_only=True,  required=False)

    @extend_schema_field({"type": ["object"],
                          "description": "Extra taxon data that the standard fields do not cover.",
                          "additionalProperties": True,
                          "default": {},
                          'examples': [{"comment": "This is a large bird"}]
                          })
    def get_taxon_extra_data(self, object):
        return {}

    annotated_by = serializers.CharField(
        read_only=True, default=None, required=False)

    bounding_box = BBoxField(required=False)

    extra_data = DummyJSONField(
        required=False, help_text="Extra taxon data that the standard fields do not cover.")

    class Meta:
        model = Observation
        exclude = []


class ObservationSerializer(OwnerMixIn, CreatedModifiedMixIn, serializers.ModelSerializer):
    taxon_obj = ShortTaxonSerializer(
        source='taxon', read_only=True, required=False)
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all(),
        required=False)
    species_name = SlugRelatedGetOrCreateField(many=False,
                                               source="taxon",
                                               slug_field="species_name",
                                               queryset=Taxon.objects.all(),
                                               allow_null=True,
                                               required=False,
                                               read_only=False)

    def to_representation(self, instance):
        initial_rep = super(ObservationSerializer,
                            self).to_representation(instance)
        initial_rep.pop("species_name")
        original_taxon_obj = initial_rep.pop("taxon_obj")
        if (target_taxon_level := self.context.get("target_taxon_level")) is not None:
            target_taxon_level = int(target_taxon_level)

            if original_taxon_obj["taxonomic_level"] == target_taxon_level:
                initial_rep.update(original_taxon_obj)
            else:
                try:
                    new_taxon_obj = Taxon.objects.get(
                        pk=instance.parent_taxon_pk)
                except Taxon.DoesNotExist:
                    new_taxon_obj = None

                if new_taxon_obj is not None:
                    new_taxon_dict = ShortTaxonSerializer(new_taxon_obj).data
                    initial_rep.update(new_taxon_dict)
                else:
                    return None

        else:
            initial_rep.update(original_taxon_obj)

        if instance.owner:
            initial_rep["annotated_by"] = f"{instance.owner.first_name} {instance.owner.last_name}"
        else:
            initial_rep["annotated_by"] = None

        return initial_rep

    def validate(self, data):
        data = super().validate(data)
        if not self.partial:
            result, message, data = check_two_keys(
                'taxon',
                'species_name',
                data,
                Taxon,
                self.form_submission
            )
            if not result:
                raise serializers.ValidationError(message)
        return data

    class Meta:

        model = Observation
        exclude = []
