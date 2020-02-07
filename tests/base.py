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

import fcntl
import libevdev
import os
import pathlib
import pytest
import sys
import time

# FIXME: this is really wrong :)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/..')  # noqa

import logging

import hidtools.hid as hid # noqa
from hidtools.util import twos_comp, to_twos_comp # noqa
from hidtools.uhid import UHIDDevice  # noqa

logger = logging.getLogger('hidtools.test.base')


class SysfsFile(object):
    def __init__(self, path):
        self.path = path

    def __set_value(self, value):
        with open(self.path, 'w') as f:
            return f.write(f'{value}\n')

    def __get_value(self):
        with open(self.path) as f:
            return f.read().strip()

    @property
    def int_value(self):
        return int(self.__get_value())

    @int_value.setter
    def int_value(self, v):
        self.__set_value(v)

    @property
    def str_value(self):
        return self.__get_value()

    @str_value.setter
    def str_value(self, v):
        self.__set_value(v)


class LED(object):
    def __init__(self, udev_object):
        self.sys_path = pathlib.Path(udev_object.sys_path)
        self.max_brightness = SysfsFile(self.sys_path / 'max_brightness').int_value
        self.__brightness = SysfsFile(self.sys_path / 'brightness')

    @property
    def brightness(self):
        return self.__brightness.int_value

    @brightness.setter
    def brightness(self, value):
        self.__brightness.int_value = value


class UHIDTestDevice(UHIDDevice):
    input_type_mapping = {
        'ID_INPUT_TOUCHSCREEN': 'Touch Screen',
        'ID_INPUT_TOUCHPAD': 'Touch Pad',
        'ID_INPUT_TABLET': 'Pen',
        'ID_INPUT_MOUSE': 'Mouse',
        'ID_INPUT_KEY': 'Key',
        'ID_INPUT_JOYSTICK': 'Joystick',
        'ID_INPUT_ACCELEROMETER': 'Accelerometer',
    }

    def __init__(self, name, application, rdesc_str=None, rdesc=None, input_info=None):
        if rdesc_str is None and rdesc is None:
            raise Exception('Please provide at least a rdesc or rdesc_str')
        super().__init__()
        if name is None:
            name = f'uhid test {self.__class__.__name__}'
        if input_info is None:
            input_info = (3, 1, 2)
        self.name = name
        self.info = input_info
        self.default_reportID = None
        if not name.startswith('uhid test '):
            self.name = 'uhid test ' + self.name
        self.opened = False
        self.application = application
        self.input_nodes = {}
        self.led_classes = {}
        self._opened_files = []
        if rdesc is None:
            self.rdesc = hid.ReportDescriptor.from_human_descr(rdesc_str)
        else:
            self.rdesc = rdesc

    def match_evdev_rule(self, application, evdev):
        '''Replace this in subclasses if the device has multiple reports
        of the same type and we need to filter based on the actual evdev
        node.

        returning True will append the corresponding report to
        `self.input_nodes[type]`
        returning False  will ignore this report for the device.
        '''
        return True

    def udev_input_event(self, device):
        if 'DEVNAME' not in device.properties:
            return

        devname = device.properties['DEVNAME']
        if not devname.startswith('/dev/input/event'):
            return

        # associate the Input type to the matching HID application
        # we reuse the guess work from udev
        types = []
        for name, type in UHIDTestDevice.input_type_mapping.items():
            if name in device.properties:
                types.append(type)

        if not types:
            # abort, the device has not been processed by udev
            print('abort', devname, list(device.properties.items()))
            return

        event_node = open(devname, 'rb')
        self._opened_files.append(event_node)
        evdev = libevdev.Device(event_node)

        fd = evdev.fd.fileno()
        flag = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

        for type in types:
            # check for custom defined matching
            if not self.match_evdev_rule(type, evdev):
                evdev.fd.close()
                continue
            self.input_nodes[type] = evdev

    def udev_led_event(self, device):
        led = LED(device)
        self.led_classes[led.sys_path.name] = led

    def udev_event(self, event):
        if event.action != 'add':
            return

        device = event

        subsystem = device.properties['SUBSYSTEM']

        if subsystem == 'input':
            return self.udev_input_event(device)
        elif subsystem == 'leds':
            return self.udev_led_event(device)

        logger.debug(f'{subsystem}: {device}')

    def open(self):
        self.opened = True

    def __del__(self):
        for evdev in self._opened_files:
            evdev.close()

    def close(self):
        self.opened = False

    def start(self, flags):
        pass

    def stop(self):
        to_remove = []
        for name, evdev in self.input_nodes.items():
            evdev.fd.close()
            to_remove.append(name)

        for name in to_remove:
            del(self.input_nodes[name])

    def next_sync_events(self):
        return list(self.evdev.events())

    @property
    def evdev(self):
        if self.application not in self.input_nodes:
            return None

        return self.input_nodes[self.application]


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
                    human_data = [f'\n\t      '.join(h.split('\n')) for h in human_data]
                data = [f'{d}\n\t ====> {h}' for d, h in zip(data, human_data)]

            reports = data

            if len(reports) == 1:
                print(f'sending 1 report:')
            else:
                print(f'sending {len(reports)} reports:')
            for report in reports:
                print('\t', report)

            if events is not None:
                print('events received:', events)

        def create_device(self):
            raise Exception('please reimplement me in subclasses')

        def assertName(self, uhdev):
            assert uhdev.evdev.name == uhdev.name

        def uhdev_is_ready(self):
            '''Can be overwritten in subclasses to add extra conditions
            on when to consider a UHID device ready. This can be:
            - we need to wait on different types of input devices to be ready
              (Touch Screen and Pen for example)
            - we need to have at least 4 LEDs present
              (len(self.uhdev.leds_classes) == 4)
            - or any other combinations'''
            return self.uhdev.application in self.uhdev.input_nodes

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
                while not self.uhdev_is_ready() and time.time() - now < 5:
                    self.uhdev.dispatch(10)
                assert self.uhdev.evdev is not None
                yield

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
            assert uhdev.evdev is not None


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
