# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for interface link form."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

str = None

__metaclass__ = type
__all__ = []

import random

from maasserver.enum import (
    INTERFACE_LINK_TYPE,
    INTERFACE_TYPE,
    IPADDRESS_TYPE,
    NODEGROUP_STATUS,
    NODEGROUPINTERFACE_MANAGEMENT,
)
from maasserver.forms_interface_link import (
    InterfaceLinkForm,
    InterfaceSetDefaultGatwayForm,
    InterfaceUnlinkForm,
)
from maasserver.models import interface as interface_module
from maasserver.testing.factory import factory
from maasserver.testing.orm import reload_object
from maasserver.testing.testcase import MAASServerTestCase
from maasserver.utils.orm import get_one
from netaddr import IPAddress


class TestInterfaceLinkForm(MAASServerTestCase):

    def test__requires_mode(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={})
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "mode": ["This field is required."],
            }, form.errors)

    def test__mode_is_case_insensitive(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP.upper(),
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test__sets_subnet_queryset_to_subnets_on_interface_vlan(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnets = [
            factory.make_Subnet(vlan=interface.vlan)
            for _ in range(3)
        ]
        form = InterfaceLinkForm(instance=interface, data={})
        self.assertItemsEqual(subnets, form.fields["subnet"].queryset)

    def test__AUTO_requires_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
        })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "subnet": ["This field is required."],
            }, form.errors)

    def test__AUTO_creates_link_to_AUTO_with_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        auto_subnet = factory.make_Subnet(vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
            "subnet": auto_subnet.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        auto_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.AUTO)
        self.assertEquals(auto_subnet, auto_ip.subnet)

    def test__AUTO_sets_node_gateway_link_v4(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        network = factory.make_ipv4_network()
        auto_subnet = factory.make_Subnet(
            cidr=unicode(network.cidr), vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
            "subnet": auto_subnet.id,
            "default_gateway": True,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        auto_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.AUTO)
        node = interface.get_node()
        self.assertEquals(auto_ip, node.gateway_link_ipv4)

    def test__AUTO_sets_node_gateway_link_v6(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        network = factory.make_ipv6_network()
        auto_subnet = factory.make_Subnet(
            cidr=unicode(network.cidr), vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
            "subnet": auto_subnet.id,
            "default_gateway": True,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        auto_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.AUTO)
        node = interface.get_node()
        self.assertEquals(auto_ip, node.gateway_link_ipv6)

    def test__AUTO_default_gateway_requires_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
            "default_gateway": True,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "default_gateway": [
                "Subnet is required when default_gateway is True."],
            "subnet": ["This field is required."],
            }, form.errors)

    def test__AUTO_default_gateway_requires_subnet_with_gateway_ip(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        auto_subnet = factory.make_Subnet(vlan=interface.vlan)
        auto_subnet.gateway_ip = None
        auto_subnet.save()
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.AUTO,
            "subnet": auto_subnet.id,
            "default_gateway": True,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "default_gateway": [
                "Cannot set as default gateway because subnet "
                "%s doesn't provide a gateway IP address." % auto_subnet],
            }, form.errors)

    def test__DHCP_not_allowed_if_already_DHCP_with_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        dhcp_subnet = factory.make_Subnet()
        factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.DHCP, ip="",
            subnet=dhcp_subnet, interface=interface)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "mode": [
                "Interface is already set to DHCP from '%s'." % (
                    dhcp_subnet)]
            }, form.errors)

    def test__DHCP_not_allowed_if_already_DHCP_without_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        static_ip = factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.DHCP, ip="", interface=interface)
        static_ip.subnet = None
        static_ip.save()
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "mode": [
                "Interface is already set to DHCP."]
            }, form.errors)

    def test__DHCP_not_allowed_default_gateway(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP,
            "default_gateway": True,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "default_gateway": [
                "Cannot use in mode '%s'." % (INTERFACE_LINK_TYPE.DHCP)]
            }, form.errors)

    def test__DHCP_creates_link_to_DHCP_with_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        dhcp_subnet = factory.make_Subnet(vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP,
            "subnet": dhcp_subnet.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        dhcp_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.DHCP)
        self.assertEquals(dhcp_subnet, dhcp_ip.subnet)

    def test__DHCP_creates_link_to_DHCP_without_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.DHCP,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        self.assertIsNotNone(
            get_one(
                interface.ip_addresses.filter(alloc_type=IPADDRESS_TYPE.DHCP)))

    def test__STATIC_requires_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
        })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "subnet": ["This field is required."],
            }, form.errors)

    def test__STATIC_not_allowed_if_ip_address_not_in_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        network = factory.make_ipv4_network()
        subnet = factory.make_Subnet(
            vlan=interface.vlan, cidr=unicode(network.cidr))
        ip_not_in_subnet = factory.make_ipv6_address()
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "ip_address": ip_not_in_subnet,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "ip_address": [
                "IP address is not in the given subnet '%s'." % subnet]
            }, form.errors)

    def test__STATIC_not_allowed_if_ip_address_in_dynamic_range(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        ngi = factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        ip_in_dynamic = IPAddress(ngi.get_dynamic_ip_range().first)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "ip_address": "%s" % ip_in_dynamic,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "ip_address": [
                "IP address is inside a managed dynamic range %s to %s." % (
                    ngi.ip_range_low, ngi.ip_range_high)]
            }, form.errors)

    def test__STATIC_sets_ip_in_unmanaged_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        ip = factory.pick_ip_in_network(subnet.get_ipnetwork())
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "ip_address": ip,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        self.assertIsNotNone(
            get_one(
                interface.ip_addresses.filter(
                    alloc_type=IPADDRESS_TYPE.STICKY, ip=ip, subnet=subnet)))

    def test__STATIC_sets_ip_in_managed_subnet(self):
        # Silence update_host_maps.
        self.patch_autospec(interface_module, "update_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        ngi = factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        ip_in_static = IPAddress(ngi.get_static_ip_range().first)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "ip_address": "%s" % ip_in_static,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        self.assertIsNotNone(
            get_one(
                interface.ip_addresses.filter(
                    alloc_type=IPADDRESS_TYPE.STICKY, ip="%s" % ip_in_static,
                    subnet=subnet)))

    def test__STATIC_picks_ip_in_unmanaged_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        ip_address = get_one(
            interface.ip_addresses.filter(
                alloc_type=IPADDRESS_TYPE.STICKY, subnet=subnet))
        self.assertIsNotNone(ip_address)
        self.assertIn(IPAddress(ip_address.ip), subnet.get_ipnetwork())

    def test__STATIC_picks_ip_in_managed_subnet(self):
        # Silence update_host_maps.
        self.patch_autospec(interface_module, "update_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        ngi = factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        ip_address = get_one(
            interface.ip_addresses.filter(
                alloc_type=IPADDRESS_TYPE.STICKY, subnet=subnet))
        self.assertIsNotNone(ip_address)
        self.assertIn(IPAddress(ip_address.ip), ngi.get_static_ip_range())

    def test__STATIC_sets_node_gateway_link_ipv4(self):
        # Silence update_host_maps.
        self.patch_autospec(interface_module, "update_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        network = factory.make_ipv4_network()
        subnet = factory.make_Subnet(
            cidr=unicode(network.cidr), vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "default_gateway": True,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        ip_address = get_one(
            interface.ip_addresses.filter(
                alloc_type=IPADDRESS_TYPE.STICKY, subnet=subnet))
        node = interface.get_node()
        self.assertEquals(ip_address, node.gateway_link_ipv4)

    def test__STATIC_sets_node_gateway_link_ipv6(self):
        # Silence update_host_maps.
        self.patch_autospec(interface_module, "update_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        network = factory.make_ipv6_network()
        subnet = factory.make_Subnet(
            cidr=unicode(network.cidr), vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "default_gateway": True,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        ip_address = get_one(
            interface.ip_addresses.filter(
                alloc_type=IPADDRESS_TYPE.STICKY, subnet=subnet))
        node = interface.get_node()
        self.assertEquals(ip_address, node.gateway_link_ipv6)

    def test__LINK_UP_not_allowed_with_other_ip_addresses(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.DHCP, ip="", interface=interface)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.LINK_UP,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "mode": [
                "Cannot configure interface to link up (with no IP address) "
                "while other links are already configured."]
            }, form.errors)

    def test__LINK_UP_creates_link_STICKY_with_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        link_subnet = factory.make_Subnet(vlan=interface.vlan)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.LINK_UP,
            "subnet": link_subnet.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        link_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.STICKY)
        self.assertIsNone(link_ip.ip)
        self.assertEquals(link_subnet, link_ip.subnet)

    def test__LINK_UP_creates_link_STICKY_without_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.LINK_UP,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        link_ip = get_one(
            interface.ip_addresses.filter(alloc_type=IPADDRESS_TYPE.STICKY))
        self.assertIsNotNone(link_ip)
        self.assertIsNone(link_ip.ip)

    def test__LINK_UP_not_allowed_default_gateway(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceLinkForm(instance=interface, data={
            "mode": INTERFACE_LINK_TYPE.LINK_UP,
            "default_gateway": True,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "default_gateway": [
                "Cannot use in mode '%s'." % (INTERFACE_LINK_TYPE.LINK_UP)]
            }, form.errors)

    def test_linking_when_no_bond_not_allowed(self):
        node = factory.make_Node()
        eth0 = factory.make_Interface(INTERFACE_TYPE.PHYSICAL, node=node)
        eth1 = factory.make_Interface(INTERFACE_TYPE.PHYSICAL, node=node)
        bond0 = factory.make_Interface(
            INTERFACE_TYPE.BOND, parents=[eth0, eth1], node=node)
        subnet = factory.make_Subnet(vlan=eth0.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        ngi = factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        ip_in_static = IPAddress(ngi.get_static_ip_range().first)
        form = InterfaceLinkForm(instance=eth0, data={
            "mode": INTERFACE_LINK_TYPE.STATIC,
            "subnet": subnet.id,
            "ip_address": "%s" % ip_in_static,
            })
        self.assertFalse(form.is_valid())
        self.assertEquals({
            "bond": [("Cannot link interface(%s) when interface is in a "
                      "bond(%s)." % (eth0.name, bond0.name))]},
            form.errors)


class TestInterfaceUnlinkForm(MAASServerTestCase):

    def test__requires_id(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceUnlinkForm(instance=interface, data={})
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "id": ["This field is required."],
            }, form.errors)

    def test__must_be_valid_id(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        link_id = random.randint(100, 1000)
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": link_id,
            })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "id": ["'%s' is not a valid id.  It should be one of: ." % (
                link_id)],
            }, form.errors)

    def test__DHCP_deletes_link_with_unmanaged_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        dhcp_subnet = factory.make_Subnet(vlan=interface.vlan)
        interface.link_subnet(INTERFACE_LINK_TYPE.DHCP, dhcp_subnet)
        interface = reload_object(interface)
        dhcp_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.DHCP)
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": dhcp_ip.id,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIsNone(reload_object(dhcp_ip))

    def test__DHCP_deletes_link_with_managed_subnet(self):
        self.patch_autospec(interface_module, "remove_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        dhcp_subnet = factory.make_Subnet(vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=dhcp_subnet)
        interface.link_subnet(INTERFACE_LINK_TYPE.DHCP, dhcp_subnet)
        interface = reload_object(interface)
        dhcp_ip = interface.ip_addresses.get(alloc_type=IPADDRESS_TYPE.DHCP)
        assigned_ip = factory.pick_ip_in_network(dhcp_subnet.get_ipnetwork())
        factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.DISCOVERED, ip=assigned_ip,
            subnet=dhcp_subnet, interface=interface)
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": dhcp_ip.id,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIsNone(reload_object(dhcp_ip))

    def test__STATIC_deletes_link_in_unmanaged_subnet(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        ip = factory.pick_ip_in_network(subnet.get_ipnetwork())
        interface.link_subnet(
            INTERFACE_LINK_TYPE.STATIC, subnet, ip_address=ip)
        interface = reload_object(interface)
        static_ip = get_one(
            interface.ip_addresses.filter(
                alloc_type=IPADDRESS_TYPE.STICKY, ip=ip, subnet=subnet))
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": static_ip.id,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIsNone(reload_object(static_ip))

    def test__STATIC_deletes_link_in_managed_subnet(self):
        self.patch_autospec(interface_module, "remove_host_maps")
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        nodegroup = factory.make_NodeGroup(status=NODEGROUP_STATUS.ENABLED)
        factory.make_NodeGroupInterface(
            nodegroup, management=NODEGROUPINTERFACE_MANAGEMENT.DHCP,
            subnet=subnet)
        ip = factory.pick_ip_in_network(subnet.get_ipnetwork())
        static_ip = factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.STICKY, ip=ip,
            subnet=subnet, interface=interface)
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": static_ip.id,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIsNone(reload_object(static_ip))

    def test__LINK_UP_deletes_link(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        subnet = factory.make_Subnet(vlan=interface.vlan)
        link_ip = factory.make_StaticIPAddress(
            alloc_type=IPADDRESS_TYPE.STICKY, ip="",
            subnet=subnet, interface=interface)
        form = InterfaceUnlinkForm(instance=interface, data={
            "id": link_ip.id,
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIsNone(reload_object(link_ip))


class TestInterfaceSetDefaultGatwayForm(MAASServerTestCase):

    def make_ip_family_link(
            self, interface, network, alloc_type=IPADDRESS_TYPE.STICKY):
        subnet = factory.make_Subnet(
            cidr=unicode(network.cidr), vlan=interface.vlan)
        if alloc_type == IPADDRESS_TYPE.STICKY:
            ip = factory.pick_ip_in_network(network)
        else:
            ip = ""
        return factory.make_StaticIPAddress(
            alloc_type=alloc_type, ip=ip, subnet=subnet, interface=interface)

    def test__interface_needs_gateways(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={})
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "__all__": ["This interface has no usable gateways."],
            }, form.errors)

    def test__doesnt_require_link_id_if_only_one_gateway_per_family(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        self.make_ip_family_link(interface, factory.make_ipv4_network())
        self.make_ip_family_link(interface, factory.make_ipv6_network())
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={})
        self.assertTrue(form.is_valid(), form.errors)

    def test__requires_link_id_if_more_than_one_gateway_per_family(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        self.make_ip_family_link(interface, factory.make_ipv4_network())
        self.make_ip_family_link(interface, factory.make_ipv6_network())
        self.make_ip_family_link(interface, factory.make_ipv4_network())
        self.make_ip_family_link(interface, factory.make_ipv6_network())
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={})
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEquals({
            "link_id": [
                "This field is required; Interface has more than one "
                "usable IPv4 and IPv6 gateways."],
            }, form.errors)

    def test__link_id_fields_setup_correctly(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        links = []
        for _ in range(2):
            links.append(
                self.make_ip_family_link(
                    interface, factory.make_ipv4_network()))
        for _ in range(2):
            links.append(
                self.make_ip_family_link(
                    interface, factory.make_ipv6_network()))
        link_ids = [
            link.id
            for link in links
        ]
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={})
        choice_ids = [
            choice[0]
            for choice in form.fields["link_id"].choices
        ]
        self.assertItemsEqual(link_ids, choice_ids)

    def test__sets_gateway_links_on_node_when_no_link_id(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        ipv4_link = self.make_ip_family_link(
            interface, factory.make_ipv4_network())
        ipv6_link = self.make_ip_family_link(
            interface, factory.make_ipv6_network())
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={})
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        node = interface.get_node()
        self.assertEquals(ipv4_link, node.gateway_link_ipv4)
        self.assertEquals(ipv6_link, node.gateway_link_ipv6)

    def test__sets_gateway_link_v4_on_node_when_link_id(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        ipv4_link = self.make_ip_family_link(
            interface, factory.make_ipv4_network())
        self.make_ip_family_link(interface, factory.make_ipv4_network())
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={
            "link_id": ipv4_link.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        node = interface.get_node()
        self.assertEquals(ipv4_link, node.gateway_link_ipv4)

    def test__sets_gateway_link_v6_on_node_when_link_id(self):
        interface = factory.make_Interface(INTERFACE_TYPE.PHYSICAL)
        ipv6_link = self.make_ip_family_link(
            interface, factory.make_ipv6_network())
        self.make_ip_family_link(interface, factory.make_ipv6_network())
        form = InterfaceSetDefaultGatwayForm(instance=interface, data={
            "link_id": ipv6_link.id,
            })
        self.assertTrue(form.is_valid(), form.errors)
        interface = form.save()
        node = interface.get_node()
        self.assertEquals(ipv6_link, node.gateway_link_ipv6)
