# Copyright 2012-2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""System user representing node-group workers.

Workers access the MAAS API under this user identity.
"""

__all__ = [
    'get_worker_user',
    'user_name',
    ]

from django.contrib.auth.models import User


user_name = 'maas-nodegroup-worker'


def get_worker_user():
    """Get the system user representing the node-group workers."""
    worker_user, created = User.objects.get_or_create(
        username=user_name, defaults=dict(
            first_name="Node-group worker", last_name="Special user",
            email="maas-nodegroup-worker@localhost", is_staff=False,
            is_superuser=False))
    return worker_user
