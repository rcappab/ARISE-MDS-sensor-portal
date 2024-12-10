from bridgekeeper.rules import R
from django.db.models import Q


def final_query(accumulated_q):
    if len(accumulated_q) == 0:
        return Q(id=-1)
    else:
        return Q(accumulated_q)


def query_super(user):
    accumulated_q = Q()

    if user.is_superuser:
        return accumulated_q

    return None


def check_super(user):
    if user.is_superuser:
        return True

    return None


# PROJECT RULES
class IsOwner(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user == instance.owner

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(owner=user)
            return final_query(accumulated_q)


class IsManager(R):

    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user in instance.managers.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            accumulated_q = Q(
                managers=user)
            return final_query(accumulated_q)


class IsViewer(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user in instance.viewers.all()

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # in project group
            accumulated_q = Q(viewers=user)

            return final_query(accumulated_q)


class CanViewDeploymentInProject(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_viewer = user.pk in instance.values_list(
                'project__viewers__pk', flat=True)
            is_manager = user.pk in instance.values_list(
                'project__managers__pk', flat=True)
            is_owner = user.pk in instance.values_list(
                'project__owner__pk', flat=True)

            return any([is_viewer, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(project__viewers=user)
            # manage
            accumulated_q = accumulated_q | Q(
                project__managers=user)
            # owner
            accumulated_q = accumulated_q | Q(project__owner=user)

        return final_query(accumulated_q)


class CanViewDeviceInProject(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_viewer = user.pk in instance.values_list(
                'deployments__project__viewers__pk', flat=True)
            is_manager = user.pk in instance.values_list(
                'deployments__project__managers__pk', flat=True)
            is_owner = user.pk in instance.values_list(
                'deployments__project__owner__pk', flat=True)

            return any([is_viewer, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployments__project__viewers=user)
            # manage
            accumulated_q = accumulated_q | Q(
                deployments__project__managers=user)
            # own
            accumulated_q = accumulated_q | Q(
                deployments__project__owner=user)

        return final_query(accumulated_q)


class CanViewProjectContainingDevice(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_viewer = user.pk in instance.values_list(
                "deployments__project__viewers__pk", flat=True)
            is_manager = user.pk in instance.values_list(
                "deployments__project__managers__pk", flat=True)
            is_owner = user.pk in instance.values_list(
                "deployments__project__owner__pk", flat=True)

            return any([is_viewer, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployments__project__viewers=user)
            # manage
            accumulated_q = accumulated_q | Q(
                deployments__project__managers=user)
            # own
            accumulated_q = accumulated_q | Q(deployments__project__owner=user)

        return final_query(accumulated_q)


class CanManageProjectContainingDeployment(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = user.pk in instance.values_list(
                "project__managers__pk")
            is_owner = user.pk in instance.values_list("project__owner__pk")
            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            print(self)
            # can manage/own a deployment within project
            # manage
            accumulated_q = Q(project__managers=user)
            print(accumulated_q)
            # own
            accumulated_q = accumulated_q | Q(project__owner=user)
            print(accumulated_q)

        return final_query(accumulated_q)


class CanViewProjectContainingDeployment(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user.pk in instance.values_list("project__viewers__pk")

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(project__viewers=user)

        return final_query(accumulated_q)


class CanViewDeployedDevice(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_viewer = user.pk in instance.values_list("device__viewers__pk")
            is_manager = user.pk in instance.values_list(
                "device__managers__pk")
            is_owner = user.pk in instance.values_list("device__owner__pk")

            return any([is_viewer, is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(device__viewers=user)
            # manage
            accumulated_q = accumulated_q | Q(device__managers=user)
            # own
            accumulated_q = accumulated_q | Q(device__owner=user)

        return final_query(accumulated_q)


class CanManageProjectContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = user.pk in instance.values_list(
                "deployment__project__managers__pk", flat=True)
            is_owner = user.pk in instance.values_list(
                "deployment__project__owner__pk", flat=True)

            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__project__managers=user)
            # own
            accumulated_q = accumulated_q | Q(deployment__project__owner=user)

        return final_query(accumulated_q)


class CanViewProjectContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user.pk in instance.values_list(
                "deployment__project__viewers__pk", flat=True)

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__project__viewers=user)

        return final_query(accumulated_q)


class CanManageDeploymentContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = user.pk in instance.values_list(
                "deployment__managers__pk", flat=True)
            is_owner = user.pk in instance.values_list(
                "deployment__owner__pk", flat=True)

            return any([is_manager, is_owner])

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__managers=user)
            # own
            accumulated_q = accumulated_q | Q(deployment__owner=user)

        return final_query(accumulated_q)


class CanViewDeploymentContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user.pk in instance.values_list(
                "deployment__viewers__pk", flat=True)

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__viewers=user)

        return final_query(accumulated_q)


class CanManageDeviceContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            is_manager = user.pk in user.values_list(
                "deployment__device__managers__pk", flat=True)
            is_owner = user.pk in user.values_list(
                "deployment__device__owner__pk", flat=True)

            return any(is_manager, is_owner)

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__device__managers=user)
            # own
            accumulated_q = accumulated_q | Q(deployment__device__owner=user)

        return final_query(accumulated_q)


class CanViewDeviceContainingDataFile(R):
    def check(self, user, instance=None):
        initial_bool = check_super(user)

        if initial_bool is not None:
            return initial_bool
        else:
            return user.pk in user.values_list(
                "deployment__device__viewers__pk", flat=True)

    def query(self, user):
        accumulated_q = query_super(user)

        if accumulated_q is not None:
            return accumulated_q
        else:
            # can view/manage/own a deployment within project
            # view
            accumulated_q = Q(deployment__device__viewers=user)

        return final_query(accumulated_q)
