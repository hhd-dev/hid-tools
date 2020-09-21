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

import libevdev
import os
import pytest
import sys
import time

import logging

# FIXME: this is really wrong :)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/..')  # noqa

from hidtools.util import twos_comp, to_twos_comp # noqa
from hidtools.device.base_device import BaseDevice, SysfsFile # noqa

logger = logging.getLogger('hidtools.test.base')


class UHIDTestDevice(BaseDevice):
    def __init__(self, name, application, rdesc_str=None, rdesc=None, input_info=None):
        super().__init__(name, application, rdesc_str, rdesc, input_info)
        if name is None:
            name = f'uhid test {self.__class__.__name__}'
        if not name.startswith('uhid test '):
            name = 'uhid test ' + self.name
        self.name = name


class BaseTestCase:
    class TestUhid(object):
        syn_event = libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT)
        key_event = libevdev.InputEvent(libevdev.EV_KEY)
        abs_event = libevdev.InputEvent(libevdev.EV_ABS)
        rel_event = libevdev.InputEvent(libevdev.EV_REL)
        msc_event = libevdev.InputEvent(libevdev.EV_MSC.MSC_SCAN)

        def assertInputEventsIn(self, expected_events, effective_events):
            effective_events = effective_events.copy()
            for ev in expected_events:
                assert ev in effective_events
                effective_events.remove(ev)
            return effective_events

        def assertInputEvents(self, expected_events, effective_events):
            remaining = self.assertInputEventsIn(expected_events, effective_events)
            assert remaining == []

        @classmethod
        def debug_reports(cls, reports, uhdev=None, events=None):
            data = [' '.join([f'{v:02x}' for v in r]) for r in reports]

            if uhdev is not None:
                human_data = [uhdev.parsed_rdesc.format_report(r, split_lines=True) for r in reports]
                try:
                    human_data = [f'\n\t       {" " * h.index("/")}'.join(h.split('\n')) for h in human_data]
                except ValueError:
                    # '/' not found: not a numbered report
                    human_data = ['\n\t      '.join(h.split('\n')) for h in human_data]
                data = [f'{d}\n\t ====> {h}' for d, h in zip(data, human_data)]

            reports = data

            if len(reports) == 1:
                print('sending 1 report:')
            else:
                print(f'sending {len(reports)} reports:')
            for report in reports:
                print('\t', report)

            if events is not None:
                print('events received:', events)

        def create_device(self):
            raise Exception('please reimplement me in subclasses')

        def assertName(self, uhdev):
            evdev = uhdev.get_evdev()
            assert evdev.name == uhdev.name

        @pytest.fixture(autouse=True)
        def context(self, request):
            with self.create_device() as self.uhdev:
                skip_cond = request.node.get_closest_marker('skip_if_uhdev')
                if skip_cond:
                    test, message, *rest = skip_cond.args

                    if test(self.uhdev):
                        pytest.skip(message)

                self.uhdev.create_kernel_device()
                now = time.time()
                while not self.uhdev.is_ready() and time.time() - now < 5:
                    self.uhdev.dispatch(10)
                assert self.uhdev.get_evdev() is not None
                yield
                self.uhdev = None

        @pytest.fixture(autouse=True)
        def check_taint(self):
            # we are abusing SysfsFile here, it's in /proc, but meh
            taint_file = SysfsFile('/proc/sys/kernel/tainted')
            taint = taint_file.int_value

            yield

            assert taint_file.int_value == taint

        def test_creation(self):
            """Make sure the device gets processed by the kernel and creates
            the expected application input node.

            If this fail, there is something wrong in the device report
            descriptors."""
            uhdev = self.uhdev
            self.assertName(uhdev)
            assert len(uhdev.next_sync_events()) == 0
            assert uhdev.get_evdev() is not None


def reload_udev_rules():
    import subprocess
    subprocess.run("udevadm control --reload-rules".split())
    subprocess.run("udevadm hwdb --update".split())


def create_udev_rule(uuid):
    os.makedirs('/run/udev/rules.d', exist_ok=True)
    with open(f'/run/udev/rules.d/91-uhid-test-device-REMOVEME-{uuid}.rules', 'w') as f:
        f.write('KERNELS=="*input*", ATTRS{name}=="uhid test *", ENV{LIBINPUT_IGNORE_DEVICE}="1"\n')
        f.write('KERNELS=="*input*", ATTRS{name}=="uhid test * System Multi Axis", ENV{ID_INPUT_TOUCHSCREEN}="", ENV{ID_INPUT_SYSTEM_MULTIAXIS}="1"\n')
    reload_udev_rules()


def teardown_udev_rule(uuid):
    os.remove(f'/run/udev/rules.d/91-uhid-test-device-REMOVEME-{uuid}.rules')
    reload_udev_rules()
