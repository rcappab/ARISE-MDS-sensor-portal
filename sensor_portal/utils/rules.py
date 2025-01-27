from bridgekeeper.rules import R
from django.db.models import Q


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
