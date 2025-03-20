from bridgekeeper import perms
from bridgekeeper.rules import is_active, is_authenticated, is_superuser
from utils.rules import IsOwner

from .rules import CanViewObservationDataFile

perms['observation_editor.add_observation'] = is_authenticated & is_active
perms['observation_editor.change_observation'] = is_authenticated & (is_superuser
                                                                     | IsOwner()) & is_active
perms['observation_editor.delete_observation'] = is_authenticated & (
    is_superuser | IsOwner())

perms['observation_editor.view_observation'] = is_authenticated & (is_superuser
                                                                   | IsOwner() |
                                                                   CanViewObservationDataFile()
                                                                   ) & is_active

perms['observation_editor.view_taxon'] = is_authenticated & is_active
perms['observation_editor.add_taxon'] = is_authenticated & is_active
