from bridgekeeper import perms
from bridgekeeper.rules import is_staff, is_active
from bridgekeeper.rules import R
from .rules import *

# PROJECT
perms ['data_models.add_project'] = is_active
perms['data_models.change_project'] = (is_staff
                                       | is_project_owner()
                                       | is_project_manager()) & is_active  # must be project owner OR manager
perms['data_models.delete_project'] = (is_staff | is_project_owner()) & is_active  # must be project owner
perms['data_models.view_project'] = (is_staff
                                     | is_project_owner()
                                     | is_project_manager()  # project owner OR project manager
                                     | in_project_viewer_group()  # OR in project group
                                     ) & is_active  # deployment/device viewers don't need to see project objects?

# DEVICE
perms ['data_models.add_device'] = is_active
perms['data_models.change_device'] = (is_staff
                                          | is_device_owner()
                                          | is_device_manager()) & is_active # must be deployment owner OR manager
perms['data_models.delete_device'] = (is_staff
                                          | is_device_owner()) & is_active # must be deployment owner
perms['data_models.view_device'] = (is_staff
                                     | is_device_owner()
                                     | is_device_manager()
                                     | in_device_viewer_group()
                                     | can_view_project_containing_device()
                                    ) & is_active  # deployment viewers don't need to see device?

# DEPLOYMENT
perms ['data_models.add_deployment'] = is_active
perms['data_models.change_deployment'] = (is_staff
                                          | is_deployment_owner()
                                          | is_deployment_manager()
                                          | can_manage_project_containing_deployment()) & is_active  # must be device owner OR manager
perms['data_models.delete_deployment'] = (is_staff
                                          | is_deployment_owner()
                                          | can_manage_project_containing_deployment()) & is_active  # must be device owner OR manager
perms['data_models.view_deployment'] = (is_staff
                                          | is_deployment_owner()
                                          | is_deployment_manager()
                                          | in_deployment_viewer_group()
                                          | can_manage_project_containing_deployment()
                                          | can_view_project_containing_deployment()
                                          | can_view_deployed_device()) & is_active

# DATAFILES
perms['data_models.add_datafile'] = is_active
perms['data_models.change_datafile'] = (is_staff
                                       | can_manage_project_containing_datafile()
                                       | can_manage_deployment_containing_datafile()
                                       | can_manage_device_containing_datafile()) & is_active
perms['data_models.delete_datafile'] = (is_staff
                                       | can_manage_project_containing_datafile()
                                       | can_manage_deployment_containing_datafile()
                                       | can_manage_device_containing_datafile()) & is_active
perms['data_models.view_datafile'] = (is_staff
                                       | can_manage_project_containing_datafile()
                                       | can_manage_deployment_containing_datafile()
                                       | can_manage_device_containing_datafile()
                                       | can_view_project_containing_datafile()
                                       | can_view_deployment_containing_datafile()
                                       | can_view_device_containing_datafile()) & is_active
