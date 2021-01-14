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

import pytest
import resource
from .base import HIDTestUdevRule


# Set up a udev rule to prevent devices added by tests from interfering with
# the running session. This should only be done once per session but not all
# tests need it. So we we just plod on if we failed to set up the udev rule,
# hoping that the tests themselves will fail or skip correctly.
@pytest.fixture(autouse=True, scope="session")
def udev_rules_setup():
    try:
        with HIDTestUdevRule():
            yield
    except PermissionError:
        yield


@pytest.fixture(autouse=True, scope='session')
def setup_rlimit():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "skip_if_uhdev(condition, message): mark test to skip if the condition on the uhdev device is met"
    )
