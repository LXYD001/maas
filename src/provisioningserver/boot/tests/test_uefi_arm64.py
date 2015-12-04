# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for `provisioningserver.boot.uefi_arm64`."""

__all__ = []

from contextlib import contextmanager
import os

from maastesting.factory import factory
from maastesting.matchers import MockCalledOnceWith
from maastesting.testcase import MAASTestCase
from provisioningserver.boot import (
    BootMethodInstallError,
    uefi_arm64 as uefi_arm64_module,
    utils,
)
from provisioningserver.boot.uefi_arm64 import (
    CONFIG_FILE_ARM64,
    UEFIARM64BootMethod,
)
from provisioningserver.tests.test_kernel_opts import make_kernel_parameters


class TestUEFIARM64BootMethod(MAASTestCase):
    """Tests `provisioningserver.boot.uefi_arm64.UEFIARM64BootMethod`."""

    def test_match_path_returns_None(self):
        method = UEFIARM64BootMethod()
        paths = [factory.make_string() for _ in range(3)]
        for path in paths:
            self.assertEqual(None, method.match_path(None, path))

    def test_get_reader_returns_None(self):
        method = UEFIARM64BootMethod()
        params = [make_kernel_parameters() for _ in range(3)]
        for param in params:
            self.assertEqual(None, method.get_reader(None, params))

    def test_install_bootloader_get_package_raises_error(self):
        method = UEFIARM64BootMethod()
        gpau = self.patch(uefi_arm64_module, 'get_ports_archive_url')
        gpau.return_value = factory.make_simple_http_url()
        self.patch(utils, 'get_updates_package').return_value = (None, None)
        self.assertRaises(
            BootMethodInstallError, method.install_bootloader, "bogus")

    def test_install_bootloader(self):
        method = UEFIARM64BootMethod()
        filename = factory.make_name('dpkg')
        data = factory.make_bytes()
        tmp = self.make_dir()
        dest = self.make_dir()

        @contextmanager
        def tempdir():
            try:
                yield tmp
            finally:
                pass

        mock_get_ports_archive_url = self.patch(
            uefi_arm64_module, 'get_ports_archive_url')
        mock_get_ports_archive_url.return_value = 'http://ports.ubuntu.com'
        mock_get_updates_package = self.patch(utils, 'get_updates_package')
        mock_get_updates_package.return_value = (data, filename)
        self.patch(uefi_arm64_module, 'call_and_check')
        self.patch(uefi_arm64_module, 'tempdir').side_effect = tempdir

        mock_install_bootloader = self.patch(
            uefi_arm64_module, 'install_bootloader')

        method.install_bootloader(dest)

        with open(os.path.join(tmp, filename), 'rb') as stream:
            saved_data = stream.read()
        self.assertEqual(data, saved_data)

        with open(os.path.join(tmp, 'grub.cfg'), 'rb') as stream:
            saved_config = stream.read().decode('utf-8')
        self.assertEqual(CONFIG_FILE_ARM64, saved_config)

        mkimage_expected = os.path.join(tmp, method.bootloader_path)
        dest_expected = os.path.join(dest, method.bootloader_path)
        self.assertThat(
            mock_install_bootloader,
            MockCalledOnceWith(mkimage_expected, dest_expected))
