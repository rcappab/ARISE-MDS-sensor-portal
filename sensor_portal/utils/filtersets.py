import django_filters.rest_framework


class GenericFilterMixIn(django_filters.FilterSet):
    created_after = django_filters.DateFilter(
        field_name='created_on', lookup_expr='gt')
    created_before = django_filters.DateFilter(
        field_name='created_on', lookup_expr='lte')
    modified_after = django_filters.DateFilter(
        field_name='modified_on', lookup_expr='gt')
    modified_before = django_filters.DateFilter(
        field_name='modified_on', lookup_expr='lte')

    class Meta:
        fields = {
            'id': ['exact', 'in']
        }


class ExtraDataFilterMixIn(django_filters.FilterSet):
    extra_data = django_filters.CharFilter(method='extra_data_filter')

    def extra_data_filter(self, queryset, name, value):
        # unpack value
        newvalue = value.split("__")[-1]
        newname = "__".join(value.split("__")[:-1])
        newname = name + "__" + newname
        return queryset.filter(**{
            newname: newvalue,
        })
