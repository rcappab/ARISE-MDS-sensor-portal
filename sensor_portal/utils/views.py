from pytz import all_timezones, common_timezones
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view()
@permission_classes([IsAuthenticated])
def AllTimezoneView(request):
    """
    Return all timezones.
    """

    combined_timezones = common_timezones + \
        [x for x in all_timezones if "Etc" in x and x not in common_timezones]
    return Response(combined_timezones)
