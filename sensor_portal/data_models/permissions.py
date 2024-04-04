from bridgekeeper import perms
from bridgekeeper.rules import is_staff, is_active, is_authenticated
from bridgekeeper.rules import R
from .rules import *

# PROJECT
perms ['data_models.add_project'] = is_authenticated & is_active
perms['data_models.change_project'] = is_authenticated & (is_staff
                                                          | IsProjectOwner()
                                                          | IsProjectManager()) & is_active  # must be project owner OR manager
perms['data_models.delete_project'] = is_authenticated & (is_staff | IsProjectOwner()) & is_active  # must be project owner
perms['data_models.view_project'] = is_authenticated & (is_staff
                                                        | IsProjectOwner()
                                                        | IsProjectManager()  # project owner OR project manager
                                                        | InProjectViewerGroup()  # OR in project group
                                                        ) & is_active  # deployment/device viewers don't need to see project objects?

# DEVICE
perms ['data_models.add_device'] = is_authenticated & is_active
perms['data_models.change_device'] = is_authenticated & (is_staff
                                                         | IsDeviceOwner()
                                                         | IsDeviceManager()) & is_active # must be deployment owner OR manager
perms['data_models.delete_device'] = is_authenticated & (is_staff
                                                         | IsDeviceOwner()) & is_active # must be deployment owner
perms['data_models.view_device'] = is_authenticated & (is_staff
                                                       | IsDeviceOwner()
                                                       | IsDeviceManager()
                                                       | InDeviceViewerGroup()
                                                       | CanViewProjectContainingDevice()
                                                       ) & is_active  # deployment viewers don't need to see device?

# DEPLOYMENT
perms ['data_models.add_deployment'] = is_authenticated & is_active
perms['data_models.change_deployment'] = is_authenticated & (is_staff
                                                             | IsDeploymentOwner()
                                                             | IsDeploymentManager()
                                                             | CanManageProjectContainingDeployment()) & is_active  # must be device owner OR manager
perms['data_models.delete_deployment'] = is_authenticated & (is_staff
                                                             | IsDeploymentOwner()
                                                             | CanManageProjectContainingDeployment()) & is_active  # must be device owner OR manager
perms['data_models.view_deployment'] = is_authenticated & (is_staff
                                                           | IsDeploymentOwner()
                                                           | IsDeploymentManager()
                                                           | InDeploymentViewerGroup()
                                                           | CanManageProjectContainingDeployment()
                                                           | CanViewProjectContainingDeployment()
                                                           | CanViewDeployedDevice()) & is_active

# DATAFILES
perms['data_models.add_datafile'] = is_authenticated & is_active
perms['data_models.change_datafile'] = is_authenticated & (is_staff
                                                           | CanManageProjectContainingDataFile()
                                                           | CanManageDeploymentContainingDataFile()
                                                           | CanManageDeviceContainingDataFile()) & is_active
perms['data_models.delete_datafile'] = is_authenticated & (is_staff
                                                           | CanManageProjectContainingDataFile()
                                                           | CanManageDeploymentContainingDataFile()
                                                           | CanManageDeviceContainingDataFile()) & is_active
perms['data_models.view_datafile'] = is_authenticated & (is_staff
                                                         | CanManageProjectContainingDataFile()
                                                         | CanManageDeploymentContainingDataFile()
                                                         | CanManageDeviceContainingDataFile()
                                                         | CanViewProjectContainingDataFile()
                                                         | CanViewDeploymentContainingDataFile()
                                                         | CanViewDeviceContainingDataFile()) & is_active
