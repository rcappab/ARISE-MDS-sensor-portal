from bridgekeeper import perms
from bridgekeeper.rules import (is_active, is_authenticated, is_staff,
                                is_superuser)
from utils.rules import IsOwner

from .rules import (CanAnnotateDeviceContainingDataFile,
                    CanAnnotateProjectContainingDataFile,
                    CanManageDeployedDevice, CanManageDeviceContainingDataFile,
                    CanManageProjectContainingDataFile,
                    CanManageProjectContainingDeployment,
                    CanViewDeployedDevice, CanViewDeviceContainingDataFile,
                    CanViewProjectContainingDataFile,
                    CanViewProjectContainingDeployment,
                    CanViewProjectContainingDevice, DataFileHasNoHuman,
                    IsAnnotator, IsManager, IsViewer)

# PROJECT
# Permissions for adding a project: User must be authenticated and active
perms['data_models.add_project'] = is_authenticated & is_active

# Permissions for changing a project: User must be authenticated, active, and either a superuser, project owner, or manager
perms['data_models.change_project'] = is_authenticated & (is_superuser
                                                          | IsOwner()
                                                          | IsManager()) & is_active

# Permissions for deleting a project: User must be authenticated, active, and either a staff member or project owner
perms['data_models.delete_project'] = is_authenticated & (
    is_staff | IsOwner()) & is_active

# Permissions for viewing a project: User must be authenticated, active, and either a superuser, project owner, manager, annotator, or viewer
perms['data_models.view_project'] = is_authenticated & (is_superuser
                                                        | IsOwner()
                                                        | IsManager()  # project owner OR project manager
                                                        | IsAnnotator()
                                                        | IsViewer()  # OR in project group
                                                        ) & is_active

# DEVICE
# Permissions for adding a device: User must be authenticated and active
perms['data_models.add_device'] = is_authenticated & is_active

# Permissions for changing a device: User must be authenticated, active, and either a superuser, device owner, or manager
perms['data_models.change_device'] = is_authenticated & (is_superuser
                                                         | IsOwner()
                                                         | IsManager()) & is_active

# Permissions for deleting a device: User must be authenticated, active, and either a superuser or device owner
perms['data_models.delete_device'] = is_authenticated & (is_superuser
                                                         | IsOwner()) & is_active

# Permissions for viewing a device: User must be authenticated, active, and either a superuser, device owner, manager, annotator, viewer, or have access to the project containing the device
perms['data_models.view_device'] = is_authenticated & (is_superuser
                                                       | IsOwner()
                                                       | IsManager()
                                                       | IsAnnotator()
                                                       | IsViewer()
                                                       | CanViewProjectContainingDevice()
                                                       ) & is_active

# DEPLOYMENT
# Permissions for adding a deployment: User must be authenticated and active
perms['data_models.add_deployment'] = is_authenticated & is_active

# Permissions for changing a deployment: User must be authenticated, active, and either a superuser, deployment owner, or have management permissions for the deployed device or project containing the deployment
perms['data_models.change_deployment'] = is_authenticated & (is_superuser
                                                             | IsOwner()
                                                             | CanManageDeployedDevice()
                                                             | CanManageProjectContainingDeployment()
                                                             ) & is_active

# Permissions for deleting a deployment: User must be authenticated, active, and either a superuser, deployment owner, or have management permissions for the project or deployed device
perms['data_models.delete_deployment'] = is_authenticated & (is_superuser
                                                             | IsOwner()
                                                             | CanManageProjectContainingDeployment()
                                                             | CanManageDeployedDevice()
                                                             ) & is_active

# Permissions for viewing a deployment: User must be authenticated, active, and either a superuser, deployment owner, or have view or management permissions for the project or deployed device
perms['data_models.view_deployment'] = is_authenticated & (is_superuser
                                                           | IsOwner()
                                                           | CanManageProjectContainingDeployment()
                                                           | CanViewProjectContainingDeployment()
                                                           | CanManageDeployedDevice()
                                                           | CanViewDeployedDevice()
                                                           ) & is_active

# DATAFILES
# Permissions for adding a datafile: User must be authenticated and active
perms['data_models.add_datafile'] = is_authenticated & is_active

# Permissions for changing a datafile: User must be authenticated, active, and either a superuser or have management permissions for the project or device containing the datafile
perms['data_models.change_datafile'] = is_authenticated & (is_superuser
                                                           | CanManageProjectContainingDataFile()
                                                           | CanManageDeviceContainingDataFile()) & is_active

# Permissions for deleting a datafile: User must be authenticated, active, and either a superuser or have management permissions for the project or device containing the datafile
perms['data_models.delete_datafile'] = is_authenticated & (is_superuser
                                                           | CanManageProjectContainingDataFile()
                                                           | CanManageDeviceContainingDataFile()) & is_active

# Permissions for viewing a datafile: User must be authenticated, active, and either a superuser, have management permissions, or specific annotation/view permissions for the project or device containing the datafile
perms['data_models.view_datafile'] = is_authenticated & (is_superuser |
                                                         ((CanManageProjectContainingDataFile()
                                                           | CanManageDeviceContainingDataFile())
                                                          | (CanAnnotateProjectContainingDataFile()
                                                              | CanViewProjectContainingDataFile()
                                                              | CanAnnotateDeviceContainingDataFile()
                                                              | CanViewDeviceContainingDataFile()
                                                             ) & DataFileHasNoHuman())) & is_active

# Permissions for annotating a datafile: User must be authenticated, active, and either a superuser or have annotation/management permissions for the project or device containing the datafile
perms['data_models.annotate_datafile'] = is_authenticated & (is_superuser
                                                             | CanManageProjectContainingDataFile()
                                                             | CanAnnotateProjectContainingDataFile()
                                                             | CanManageDeviceContainingDataFile()
                                                             | CanAnnotateDeviceContainingDataFile()
                                                             ) & is_active

# SITE
# Permissions for viewing a site: User must be authenticated and active
perms['data_models.view_site'] = is_authenticated & is_active

# Permissions for adding a site: User must be authenticated and active
perms['data_models.add_site'] = is_authenticated & is_active

# Permissions for changing a site: User must be authenticated and a superuser
perms['data_models.change_site'] = is_authenticated & is_superuser

# Permissions for deleting a site: User must be authenticated and a superuser
perms['data_models.delete_site'] = is_authenticated & is_superuser

# DATATYPE
# Permissions for viewing a datatype: User must be authenticated and active
perms['data_models.view_datatype'] = is_authenticated & is_active

# Permissions for adding a datatype: User must be authenticated and active
perms['data_models.add_datatype'] = is_authenticated & is_active

# Permissions for changing a datatype: User must be authenticated and a superuser
perms['data_models.change_datatype'] = is_authenticated & is_superuser

# Permissions for deleting a datatype: User must be authenticated and a superuser
perms['data_models.delete_datatype'] = is_authenticated & is_superuser

# DEVICE MODEL
# Permissions for viewing a device model: User must be authenticated and active
perms['data_models.view_devicemodel'] = is_authenticated & is_active

# Permissions for adding a device model: User must be authenticated and a superuser
perms['data_models.add_devicemodel'] = is_authenticated & is_superuser

# Permissions for changing a device model: User must be authenticated and a superuser
perms['data_models.change_devicemodel'] = is_authenticated & is_superuser

# Permissions for deleting a device model: User must be authenticated and a superuser
perms['data_models.delete_devicemodel'] = is_authenticated & is_superuser

# PROJECT JOB
# Permissions for viewing a project job: User must be authenticated and active
perms['data_models.view_projectjob'] = is_authenticated & is_active

# Permissions for adding a project job: User must be authenticated and a superuser
perms['data_models.add_projectjob'] = is_authenticated & is_superuser

# Permissions for changing a project job: User must be authenticated and a superuser
perms['data_models.change_projectjob'] = is_authenticated & is_superuser

# Permissions for deleting a project job: User must be authenticated and a superuser
perms['data_models.delete_projectjob'] = is_authenticated & is_superuser
