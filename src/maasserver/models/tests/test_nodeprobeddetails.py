# Copyright 2013-2016 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for `maasserver.models.nodeprobeddetails`."""

__all__ = []

from unittest.mock import create_autospec

from maasserver.models import nodeprobeddetails
from maasserver.testing.factory import factory
from maasserver.testing.testcase import MAASServerTestCase
from provisioningserver.refresh.node_info_scripts import (
    LLDP_OUTPUT_NAME,
    LSHW_OUTPUT_NAME,
)


def make_lshw_result(node, data, script_result=0):
    return factory.make_NodeResult_for_commissioning(
        node=node, name=LSHW_OUTPUT_NAME,
        data=data, script_result=script_result)


def make_lldp_result(node, data, script_result=0):
    return factory.make_NodeResult_for_commissioning(
        node=node, name=LLDP_OUTPUT_NAME,
        data=data, script_result=script_result)


class TestNodeDetail(MAASServerTestCase):

    def test_calls_through_to_get_probed_details(self):
        node = factory.make_Node()
        get_probed_details = self.patch(
            nodeprobeddetails, "get_probed_details",
            create_autospec(nodeprobeddetails.get_probed_details))
        get_probed_details.return_value = {
            node.system_id: {
                "lshw": b"<lshw-data/>",
                "lldp": b"<lldp-data/>",
            },
        }
        self.assertDictEqual(
            {"lshw": b"<lshw-data/>", "lldp": b"<lldp-data/>"},
            nodeprobeddetails.get_single_probed_details(node.system_id))
        get_probed_details.assert_called_once_with((node.system_id,))


class TestNodesDetail(MAASServerTestCase):

    def get_details(self, nodes):
        return nodeprobeddetails.get_probed_details(
            node.system_id for node in nodes)

    def test_returns_null_details_when_there_are_none(self):
        nodes = [factory.make_Node(), factory.make_Node()]
        expected = {
            node.system_id: {"lshw": None, "lldp": None}
            for node in nodes
        }
        self.assertDictEqual(expected, self.get_details(nodes))

    def test_returns_all_details(self):
        nodes = [factory.make_Node(), factory.make_Node()]
        expected = {
            node.system_id: {
                "lshw": make_lshw_result(node, b"<node%d/>" % index).data,
                "lldp": make_lldp_result(node, b"<node%d/>" % index).data,
            }
            for index, node in enumerate(nodes)
        }
        self.assertDictEqual(expected, self.get_details(nodes))

    def test_returns_only_those_details_that_exist(self):
        nodes = [factory.make_Node(), factory.make_Node()]
        expected = {
            node.system_id: {
                "lshw": make_lshw_result(node, b"<node%d/>" % index).data,
                "lldp": None,
            }
            for index, node in enumerate(nodes)
        }
        self.assertDictEqual(expected, self.get_details(nodes))

    def test_returns_only_details_from_okay_commissioning_results(self):
        nodes = [factory.make_Node(), factory.make_Node()]
        expected = {}
        for index, node in enumerate(nodes):
            make_lshw_result(node, b"<node%d/>" % index)
            make_lldp_result(node, b"<node%d/>" % index, script_result=1)
            expected[node.system_id] = {
                "lshw": b"<node%d/>" % index,
                "lldp": None,
            }
        self.assertDictEqual(expected, self.get_details(nodes))
