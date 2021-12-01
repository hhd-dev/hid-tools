#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2017 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import platform
import pytest
import re
import resource
import subprocess
from .base import HIDTestUdevRule
from pathlib import Path


# See the comment in HIDTestUdevRule, this doesn't set up but it will clean
# up once the last test exited.
@pytest.fixture(autouse=True, scope="session")
def udev_rules_session_setup():
    with HIDTestUdevRule.instance():
        yield


@pytest.fixture(autouse=True, scope='session')
def setup_rlimit():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "skip_if_uhdev(condition, message): mark test to skip if the condition on the uhdev device is met"
    )


# Generate the list of modules and modaliases
# for the tests that need to be parametrized with those
def pytest_generate_tests(metafunc):
    if 'usbVidPid' in metafunc.fixturenames:
        modules = Path('/lib/modules/') / platform.uname().release / 'kernel' / 'drivers' / 'hid'

        modalias_re = re.compile(r'alias:\s+hid:b0003g.*v([0-9a-fA-F]+)p([0-9a-fA-F]+)')

        params = []
        ids = []
        for module in modules.glob('*.ko'):
            p = subprocess.run(["modinfo", module], capture_output=True, check=True, encoding="utf-8")
            for line in p.stdout.split('\n'):
                m = modalias_re.match(line)
                if m is not None:
                    vid, pid = m.groups()
                    vid = int(vid, 16)
                    pid = int(pid, 16)
                    params.append([module, vid, pid])
                    ids.append(f'{module.name} {vid:04x}:{pid:04x}')
        metafunc.parametrize('usbVidPid', params, ids=ids)
