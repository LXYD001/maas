# Copyright 2012-2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Adapting `testscenarios` to work with MAAS."""

__all__ = [
    "WithScenarios",
    ]

import testscenarios


class WithScenarios(testscenarios.WithScenarios):
    """Variant of testscenarios_' that provides ``__call__``.

    Some sadistic `TestCase` implementations (cough, Django, cough) treat
    ``__call__`` as something other than a synonym for ``run``. This means
    that testscenarios_' ``WithScenarios``, which customises ``run`` only,
    does not work correctly.

    .. testscenarios_: https://launchpad.net/testscenarios
    """

    def __call__(self, result=None):
        if self._get_scenarios():
            for test in testscenarios.generate_scenarios(self):
                test.__call__(result)
        else:
            super(WithScenarios, self).__call__(result)
