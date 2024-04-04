from user_management.models import User, GroupProfile
from django.contrib.auth.models import Group
from bridgekeeper.rules import R
from django.db.models import Q


# Some utility functions
def final_query(accumulated_q):
    if len(accumulated_q) == 0:
        return Q(id=-1)
    else:
        return accumulated_q


def query_super(user):
    accumulated_q = Q()

    if user.is_superuser:
        return accumulated_q

    return None


def check_super(user):

    if user.is_superuser:
        return True

    return None


## PROJECT RULES
class IsProjectOwner(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.owned_projects.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.owned_projects.values_list('pk', flat=True))
            return final_query(accumulated_q)


class IsProjectManager(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.managed_projects.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.managed_projects.values_list('pk', flat=True))
            return final_query(accumulated_q)


class InProjectViewerGroup(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__project__isnull=False). \
                values_list('profile__project__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # in project group
            accumulated_q = Q(pk__in=user.groups.filter(profile__project__isnull=False).
                              values_list('profile__project__pk', flat=True).
                              distinct())

            return final_query(accumulated_q)


class CanViewDeploymentInProject(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_groupmember = instance.pk in user.groups.filter(profile__deployment__isnull=False). \
                values_list('profile__deployment__project__pk', flat=True). \
                distinct()
            is_manager = instance.pk in user.managed_deployments.all()
            is_owner = instance.pk in user.owned_deployments.all()

            return any([is_groupmember, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployments__pk__in=user.groups.filter(profile__deployment__isnull=False).
                              values_list('profile__deployment__pk', flat=True).
                              distinct())
            # manage
            accumulated_q = accumulated_q | Q(deployments__pk__in=user.managed_deployments)
            # own
            accumulated_q = accumulated_q | Q(deployments__pk__in=user.owned_deployments)

        return final_query(accumulated_q)

class CanViewDeviceInProject(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_groupmember = instance.pk in user.groups.filter(profile__device__isnull=False). \
                values_list('profile__device__deployments__project__pk', flat=True). \
                distinct()
            is_manager = instance.pk in user.managed_deployments.all()
            is_owner = instance.pk in user.owned_deployments.all()

            return any([is_groupmember, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__device__isnull=False).
                              values_list('profile__device__deployments__project__pk', flat=True).
                              distinct())
            # manage
            accumulated_q = accumulated_q | Q(pk__in=user.managed_devices.values_list('deployments__project__pk'))
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_devices.values_list('deployments__project__pk'))

        return final_query(accumulated_q)


## DEVICE RULES
class IsDeviceOwner(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.owned_devices.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.owned_devices.values_list('pk', flat=True))
            return final_query(accumulated_q)


class IsDeviceManager(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.managed_devices.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.managed_devices.values_list('pk', flat=True))
            return final_query(accumulated_q)


class InDeviceViewerGroup(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__device__isnull=False). \
                values_list('profile__device__pk', flat=True). \
                distinct()

    def query(self, user):
        print('QUERY IN DEVICE VIEWER GROUP')
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # in device group

            accumulated_q = Q(pk__in=user.groups.filter(profile__device__isnull=False).
                              values_list('profile__device__pk', flat=True).
                              distinct())

            return final_query(accumulated_q)


class CanViewProjectContainingDevice(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_groupmember = instance.pk in user.groups.filter(profile__project__isnull=False). \
                values_list('profile__project__deployments__device__pk', flat=True). \
                distinct()
            is_manager = instance.pk in user.managed_projects.values_list('deployments__device__pk').distinct()
            is_owner = instance in user.owned_projects.values_list('deployments__device__pk').distinct()

            return any([is_groupmember, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__project__isnull=False).
                              values_list('profile__project__deployments__device__pk', flat=True).
                              distinct())
            # manage
            accumulated_q = accumulated_q | Q(pk__in=user.managed_projects.
                                              values_list('deployments__device__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_projects.
                                              values_list('deployments__device__pk', flat=True).distinct())

        return final_query(accumulated_q)


class IsDeploymentOwner(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.owned_deployments.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.owned_deployments.values_list('pk', flat=True))
            return final_query(accumulated_q)


class IsDeploymentManager(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance in user.managed_deployments.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(pk__in=user.managed_deployments.values_list('pk', flat=True))
            return final_query(accumulated_q)


class InDeploymentViewerGroup(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__deployment__isnull=False). \
                values_list('profile__deployment__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # in project group
            accumulated_q = Q(pk__in=user.groups.filter(profile__deployment__isnull=False).
                              values_list('profile__deployment__pk', flat=True).
                              distinct())

            return final_query(accumulated_q)


class CanManageProjectContainingDeployment(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = instance.pk in user.managed_projects.values_list('deployments__pk').distinct()
            is_owner = instance in user.owned_projects.values_list('deployments__pk').distinct()

            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can manage/own a deployment within project
            # manage
            accumulated_q = Q(pk__in=user.managed_projects.
                                              values_list('deployments__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_projects.
                                              values_list('deployments__pk', flat=True).distinct())

        return final_query(accumulated_q)


class CanViewProjectContainingDeployment(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__project__isnull=False). \
                values_list('profile__project__deployments__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__project__isnull=False).
                              values_list('profile__project__deployments__pk', flat=True).
                              distinct())

        return final_query(accumulated_q)


class CanViewDeployedDevice(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_groupmember = instance.pk in user.groups.filter(profile__device__isnull=False). \
                values_list('profile__device__deployments__pk', flat=True). \
                distinct()
            is_manager = instance.pk in user.managed_devices.values_list('deployments__pk').distinct()
            is_owner = instance in user.owned_devices.values_list('deployments__pk').distinct()

            return any([is_groupmember, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__device__isnull=False).
                              values_list('profile__device__deployments__pk', flat=True).
                              distinct())
            # manage
            accumulated_q = accumulated_q | Q(pk__in=user.managed_devices.
                                              values_list('deployments__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_devices.
                                              values_list('deployments__pk', flat=True).distinct())

        return final_query(accumulated_q)

class CanManageProjectContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = instance.pk in user.managed_projects.values_list('deployments__datafiles__pk').distinct()
            is_owner = instance in user.owned_projects.values_list('deployments__datafiles__pk').distinct()

            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.managed_projects.
                                              values_list('deployments__datafiles__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_projects.
                                              values_list('deployments__datafiles__pk', flat=True).distinct())

        return final_query(accumulated_q)

class CanViewProjectContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__project__isnull=False). \
                values_list('profile__project__deployments__datafiles__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__project__isnull=False).
                              values_list('profile__project__deployments__datafiles__pk', flat=True).
                              distinct())

        return final_query(accumulated_q)

class CanManageDeploymentContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = instance.pk in user.managed_deployments.values_list('datafiles__pk').distinct()
            is_owner = instance in user.owned_deployments.values_list('datafiles__pk').distinct()

            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.managed_projects.
                                              values_list('datafiles__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_projects.
                                              values_list('datafiles__pk', flat=True).distinct())

        return final_query(accumulated_q)

class CanViewDeploymentContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__deployment__isnull=False). \
                values_list('profile__deployments__datafiles__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__deployment__isnull=False).
                              values_list('profile__deployment__datafiles__pk', flat=True).
                              distinct())

        return final_query(accumulated_q)

class CanManageDeviceContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = instance.pk in user.managed_devices.values_list('deployments__datafiles__pk').distinct()
            is_owner = instance in user.owned_devices.values_list('deployments__datafiles__pk').distinct()

            return any(is_manager, is_owner)

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.managed_devices.
                                              values_list('deployments__datafiles__pk', flat=True).distinct())
            # own
            accumulated_q = accumulated_q | Q(pk__in=user.owned_devices.
                                              values_list('deployments__datafiles__pk', flat=True).distinct())

        return final_query(accumulated_q)

class CanViewDeviceContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return instance.pk in user.groups.filter(profile__device__isnull=False). \
                values_list('profile__device__deployments__datafiles__pk', flat=True). \
                distinct()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(pk__in=user.groups.filter(profile__device__isnull=False).
                              values_list('profile__device__deployments__datafiles__pk', flat=True).
                              distinct())

        return final_query(accumulated_q)
