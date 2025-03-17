from observation_editor.filtersets import ObservationFilter
from observation_editor.models import Observation
from utils.viewsets import OptionalPaginationViewSetMixIn

from .querysets import get_ctdp_seq_qs
from .serializers import SequenceSerializer


class SequenceViewsetCTDP(OptionalPaginationViewSetMixIn):
    queryset = get_ctdp_seq_qs(Observation.objects.all().distinct())
    serializer_class = SequenceSerializer
