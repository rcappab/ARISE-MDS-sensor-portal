from bridgekeeper import perms
from bridgekeeper.rules import is_active, is_authenticated
from utils.rules import IsOwner

perms['data_packages.add_datapackage'] = is_authenticated & is_active
perms['data_packages.view_datapackage'] = is_authenticated & IsOwner()
perms['data_packages.delete_datapackage'] = is_authenticated & IsOwner()
perms['data_packages.change_datapackage'] = is_authenticated & IsOwner()
