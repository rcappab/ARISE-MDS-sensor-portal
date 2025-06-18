from bridgekeeper.rules import R
from django.conf import settings
from django.db.models import Q
from utils.rules import check_super, final_query, query_super


# PROJECT RULES
class IsManager(R):
    """
    A rule class to check if a user is a manager of a given instance.
    Methods:
        check(user, instance=None):
            Determines if the given user is in the list of managers for the specified instance.
            Args:
                user: The user to check.
                instance: The instance to check against. Defaults to None.
            Returns:
                bool: True if the user is a manager of the instance, False otherwise.
        query(user):
            Constructs a query to filter instances where the given user is a manager.
            Args:
                user: The user to filter by.
            Returns:
                Q: A query object representing the filter criteria.
    """

    def check(self, user, instance=None):
        return user in instance.managers.all()

    def query(self, user):
        accumulated_q = Q(
            managers=user)
        return final_query(accumulated_q)


class IsAnnotator(R):
    """
    A rule class to check if a user is an annotator for a given instance.
    Methods:
        check(user, instance=None):
            Determines if the given user is listed as an annotator for the specified instance.
            Args:
                user: The user to check.
                instance: The instance to check against. Defaults to None.
            Returns:
                bool: True if the user is an annotator for the instance, False otherwise.
        query(user):
            Constructs a query to filter instances where the given user is an annotator.
            Args:
                user: The user to filter by.
            Returns:
                Q: A query object representing the filter condition.
    """

    def check(self, user, instance=None):

        return user in instance.annotators.all()

    def query(self, user):

        accumulated_q = Q(
            annotators=user)
        return final_query(accumulated_q)


class IsViewer(R):
    """
    Rule class to check if a user is a viewer of a specific instance.
    Methods:
        check(user, instance=None):
            Determines if the given user is in the list of viewers for the specified instance.
            Args:
                user: The user to check.
                instance: The instance to check against. Defaults to None.
            Returns:
                bool: True if the user is a viewer of the instance, False otherwise.
        query(user):
            Constructs a query to filter instances where the given user is a viewer.
            Args:
                user: The user to filter by.
            Returns:
                Q: A query object representing the filter condition.
    """

    def check(self, user, instance=None):

        return user in instance.viewers.all()

    def query(self, user):

        accumulated_q = Q(viewers=user)

        return final_query(accumulated_q)


class CanViewDeploymentInProject(R):
    """
    Rule class to determine if a user can view a deployment within a project.
    This class provides methods to check permissions for a user based on their
    relationship to the project (viewer, annotator, manager, or owner) and to
    construct a query for filtering deployments that the user has access to.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the specified deployment
            instance. A user can view the deployment if they are listed as a viewer,
            annotator, manager, or owner of the associated project.
        query(user):
            Constructs a query object to filter deployments within projects that the
            user has access to. The user can access deployments if they are a viewer,
            annotator, manager, or owner of the associated project.
    """

    def check(self, user, instance=None):

        return user.pk in instance.project.viewers.values_list(
            'pk', flat=True) or \
            user.pk in instance.project.annotators.values_list(
            'pk', flat=True) or \
            user.pk in instance.project.managers.values_list(
            'pk', flat=True) or \
            user.pk == instance.project.owner.pk

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(project__viewers=user)
        accumulated_q = accumulated_q | Q(project__annotators=user)
        # manage
        accumulated_q = accumulated_q | Q(project__managers=user)
        # owner
        accumulated_q = accumulated_q | Q(project__owner=user)

        return final_query(accumulated_q)


class CanViewDeviceInProject(R):
    """
    Rule class to determine if a user can view a device within a project.
    This class provides methods to check permissions for a user based on their
    association with a project (as a viewer, annotator, manager, or owner) and
    to construct a query for filtering devices based on the user's permissions.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the specified instance.
            The user must be associated with the project as a viewer, annotator, 
            manager, or owner.
        query(user):
            Constructs a query to filter devices that the user has permission to view.
            The query accumulates conditions based on the user's roles in the project.
    """

    def check(self, user, instance=None):

        return user.pk in instance.values_list(
            'deployments__project__viewers__pk', flat=True) or\
            user.pk in instance.values_list(
            'deployments__project__annotators__pk', flat=True) or \
            user.pk in instance.values_list(
            'deployments__project__managers__pk', flat=True) or \
            user.pk in instance.values_list(
            'deployments__project__owner__pk', flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(deployments__project__viewers=user)
        # annotate
        accumulated_q = accumulated_q | Q(
            deployments__project__annotators=user)
        # manage
        accumulated_q = accumulated_q | Q(
            deployments__project__managers=user)
        # own
        accumulated_q = accumulated_q | Q(
            deployments__project__owner=user)

        return final_query(accumulated_q)


class CanViewProjectContainingDevice(R):
    """
    A rule class that determines whether a user has permission to view a project 
    containing a specific device. The rule checks the user's association with 
    the project through various roles such as viewer, annotator, manager, or owner.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the project containing 
            the device. The user must be associated with the project through one 
            of the roles: viewer, annotator, manager, or owner.
            Args:
                user: The user object to check permissions for.
                instance: The device instance to check against. Defaults to None.
            Returns:
                bool: True if the user has permission, False otherwise.
        query(user):
            Constructs a query to retrieve all devices that the user has permission 
            to view based on their association with the project through roles such 
            as viewer, annotator, manager, or owner.
            Args:
                user: The user object to construct the query for.
            Returns:
                Q: A Django Q object representing the accumulated query for filtering 
                devices based on the user's permissions.
    """

    def check(self, user, instance=None):

        return user.pk in instance.values_list(
            "deployments__project__viewers__pk", flat=True) or\
            user.pk in instance.values_list(
            "deployments__project__annotator__pk", flat=True) or\
            user.pk in instance.values_list(
            "deployments__project__managers__pk", flat=True) or\
            user.pk in instance.values_list(
            "deployments__project__owner__pk", flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(deployments__project__viewers=user)
        # annotate
        accumulated_q = accumulated_q | Q(
            deployments__project__annotators=user)
        # manage
        accumulated_q = accumulated_q | Q(
            deployments__project__managers=user)
        # own
        accumulated_q = accumulated_q | Q(deployments__project__owner=user)

        return final_query(accumulated_q)


class CanManageProjectContainingDeployment(R):
    """
    A rule class to determine if a user can manage or own a project containing a deployment.
    Methods:
        check(user, instance=None):
            Checks if the given user is either a manager or owner of the project 
            associated with the given instance. Returns True if the user is authorized, 
            otherwise False.
        query(user):
            Constructs a query to filter deployments where the user is either a manager 
            or owner of the associated project. Returns the final query object.
    """

    def check(self, user, instance=None):

        return user.pk in instance.project.all().values_list('managers__pk', flat=True) or\
            user.pk in instance.project.all().values_list('owner__pk', flat=True)

    def query(self, user):

        # can manage/own a deployment within project
        # manage
        accumulated_q = Q(project__managers=user)
        # own
        accumulated_q = accumulated_q | Q(project__owner=user)

        return final_query(accumulated_q)


class CanViewProjectContainingDeployment(R):
    """
    Rule to determine if a user can view a project containing a deployment.
    This rule checks whether a user has permission to view a project that 
    contains a specific deployment. It provides methods to verify access 
    based on user permissions and to construct query filters for database 
    operations.
    Methods:
        check(user, instance=None):
            Determines if the given user has permission to view the specified 
            instance. The instance is expected to have a related project with 
            a list of viewers.
        query(user):
            Constructs a query filter to retrieve deployments within projects 
            that the user can view or annotate.
    Attributes:
        None
    """

    def check(self, user, instance=None):

        return user.pk in instance.project.all().values_list("viewers__pk", flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(project__viewers=user) | Q(
            project__annotators=user)

        return final_query(accumulated_q)


class CanManageDeployedDevice(R):
    """
    Rule to determine if a user can manage a deployed device.
    This rule checks whether the user is either a manager of the device or the owner of the device.
    Methods:
        check(user, instance=None):
            Determines if the user has management permissions for the given device instance.
            Returns True if the user is in the device's managers list or is the owner of the device.
        query(user):
            Constructs a query to filter devices that the user can manage.
            Returns a query object that includes devices where the user is either a manager or the owner.
    """

    def check(self, user, instance=None):

        return user in instance.device.managers.all() or \
            user.pk == instance.device.owner

    def query(self, user):

        # manage
        accumulated_q = Q(device__managers=user)
        # own
        accumulated_q = accumulated_q | Q(device__owner=user)
        return final_query(accumulated_q)


class CanViewDeployedDevice(R):
    """
    Rule class to determine if a user has permission to view a deployed device.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the specified instance.
            A user can view the instance if they are listed as a viewer or annotator
            of the device associated with the instance.
        query(user):
            Constructs a query to filter instances where the given user has permission
            to view the associated device. A user can view the device if they are listed
            as a viewer or annotator of the device.
    """

    def check(self, user, instance=None):

        return user in instance.device.viewers.all() or \
            user in instance.device.annotators.all()

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(device__viewers=user) | Q(
            device__annotators=user)

        return final_query(accumulated_q)


class CanManageProjectContainingDataFile(R):
    """
    Rule class to determine if a user can manage a project containing a specific data file.
    Methods:
        check(user, instance=None):
            Checks if the given user is either a manager or owner of the project associated 
            with the given instance's deployment.
            Args:
                user (User): The user to check permissions for.
                instance (Optional[Instance]): The instance containing the deployment and project information.
            Returns:
                bool: True if the user is a manager or owner of the project, False otherwise.
        query(user):
            Constructs a query to filter deployments within projects that the user can manage or own.
            Args:
                user (User): The user to construct the query for.
            Returns:
                Q: A Django Q object representing the query for filtering deployments within projects 
                managed or owned by the user.
    """

    def check(self, user, instance=None):

        return user.pk in instance.deployment.project.all().values_list("managers__pk", flat=True) or\
            instance.deployment.project.all().values_list("owner__pk", flat=True)

    def query(self, user):
        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(deployment__project__managers=user)
        # own
        accumulated_q = accumulated_q | Q(deployment__project__owner=user)

        return final_query(accumulated_q)


class CanAnnotateProjectContainingDataFile(R):
    """
    Rule to determine if a user can annotate a project containing a specific data file.
    This class provides methods to check permissions for a user based on their association 
    with a project's annotators and to construct a query for filtering relevant data.
    Methods:
        check(user, instance=None):
            Checks if the given user is an annotator for the project associated with the instance's deployment.
        query(user):
            Constructs a query to filter deployments within projects where the user is an annotator.
    """

    def check(self, user, instance=None):

        return user.pk in instance.deployment.project.all().values_list(
            "annotators__pk", flat=True)

    def query(self, user):
        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(
            deployment__project__annotators=user)

        return final_query(accumulated_q)


class CanViewProjectContainingDataFile(R):
    """
    A rule class to determine if a user has permission to view a project 
    containing a specific data file.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the project 
            associated with the given instance. The user must be listed 
            as a viewer in the project's deployment.
        query(user):
            Constructs a query object to filter projects where the user 
            has permission to view, manage, or own a deployment within the project.
    """

    def check(self, user, instance=None):

        return user.pk in instance.deployment.project.all().values_list(
            "viewers__pk", flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(deployment__project__viewers=user)

        return final_query(accumulated_q)


class CanManageDeviceContainingDataFile(R):
    """
    A rule class to determine if a user can manage a device containing a data file.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to manage the device containing the data file.
            A user can manage the device if they are the owner of the device or if they are listed
            as a manager of the device.
            Args:
                user: The user object to check permissions for.
                instance: The instance containing the deployment and device information.
            Returns:
                bool: True if the user can manage the device, False otherwise.
        query(user):
            Constructs a query to filter deployments where the user can manage or own the device.
            Args:
                user: The user object to construct the query for.
            Returns:
                Q: A Django Q object representing the query for deployments the user can manage or own.
    """

    def check(self, user, instance=None):

        return user == instance.deployment.device.owner or\
            user in instance.deployment.device.managers.all().values_list("pk", flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # manage
        accumulated_q = Q(deployment__device__managers=user)
        # own
        accumulated_q = accumulated_q | Q(deployment__device__owner=user)

        return final_query(accumulated_q)


class CanAnnotateDeviceContainingDataFile(R):
    """
    Rule to determine if a user can annotate a device containing a data file.
    This rule checks whether the user is listed as an annotator for the device
    associated with the deployment containing the data file.
    Methods:
        check(user, instance=None):
            Determines if the user is allowed to annotate the device containing
            the data file. Returns True if the user's primary key (pk) is in the
            list of annotators for the device, otherwise False.
        query(user):
            Constructs a query to filter deployments where the user is an annotator
            for the associated device. Returns the final query object.
    """

    def check(self, user, instance=None):
        return user.pk in instance.deployment.device.annotators.all().values_list(
            "pk", flat=True)

    def query(self, user):

        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(
            deployment__device__annotators=user)

        return final_query(accumulated_q)


class CanViewDeviceContainingDataFile(R):
    """
    Rule to determine if a user can view a device containing a specific data file.
    Methods:
        check(user, instance=None):
            Checks if the given user has permission to view the device associated 
            with the provided instance. Returns True if the user's primary key 
            is in the list of viewers for the device, otherwise False.
        query(user):
            Constructs a query to filter deployments where the user is a viewer 
            of the associated device. Returns the final query object.
    """

    def check(self, user, instance=None):
        return user.pk in instance.deployment.device.viewers.all().values_list(
            "pk", flat=True)

    def query(self, user):
        # can view/manage/own a deployment within project
        # view
        accumulated_q = Q(deployment__device__viewers=user)

        return final_query(accumulated_q)


class DataFileHasNoHuman(R):
    """
    A rule class that checks whether a data file does not contain human-related data.
    Methods:
        check(user, instance=None):
            Determines if the given instance does not have human-related data.
            Returns True if `instance.has_human` is False, otherwise False.
        query(user):
            Constructs a query to filter data files that do not contain human-related data.
            Returns a query object with the condition `has_human=False`.
    """

    def check(self, user, instance=None):
        return not instance.has_human

    def query(self, user):

        accumulated_q = Q(has_human=False)

        return final_query(accumulated_q)
