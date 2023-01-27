#!/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0
#
# Copyright (c) 2017 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2017 Red Hat, Inc.

import libevdev
import os
import pytest
import time

import logging

from hidtools.device.base_device import BaseDevice, SysfsFile

logger = logging.getLogger("hidtools.test.base")


class UHIDTestDevice(BaseDevice):
    def __init__(self, name, application, rdesc_str=None, rdesc=None, input_info=None):
        super().__init__(name, application, rdesc_str, rdesc, input_info)
        if name is None:
            name = f"uhid test {self.__class__.__name__}"
        if not name.startswith("uhid test "):
            name = "uhid test " + self.name
        self.name = name


class BaseTestCase:
    class TestUhid(object):
        syn_event = libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT)  # type: ignore
        key_event = libevdev.InputEvent(libevdev.EV_KEY)  # type: ignore
        abs_event = libevdev.InputEvent(libevdev.EV_ABS)  # type: ignore
        rel_event = libevdev.InputEvent(libevdev.EV_REL)  # type: ignore
        msc_event = libevdev.InputEvent(libevdev.EV_MSC.MSC_SCAN)  # type: ignore

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
            data = [" ".join([f"{v:02x}" for v in r]) for r in reports]

            if uhdev is not None:
                human_data = [
                    uhdev.parsed_rdesc.format_report(r, split_lines=True)
                    for r in reports
                ]
                try:
                    human_data = [
                        f'\n\t       {" " * h.index("/")}'.join(h.split("\n"))
                        for h in human_data
                    ]
                except ValueError:
                    # '/' not found: not a numbered report
                    human_data = ["\n\t      ".join(h.split("\n")) for h in human_data]
                data = [f"{d}\n\t ====> {h}" for d, h in zip(data, human_data)]

            reports = data

            if len(reports) == 1:
                print("sending 1 report:")
            else:
                print(f"sending {len(reports)} reports:")
            for report in reports:
                print("\t", report)

            if events is not None:
                print("events received:", events)

        def create_device(self):
            raise Exception("please reimplement me in subclasses")

        @pytest.fixture()
        def new_uhdev(self):
            return self.create_device()

        def assertName(self, uhdev):
            evdev = uhdev.get_evdev()
            assert uhdev.name in evdev.name

        @pytest.fixture(autouse=True)
        def context(self, new_uhdev, request):
            try:
                with HIDTestUdevRule.instance():
                    with new_uhdev as self.uhdev:
                        skip_cond = request.node.get_closest_marker("skip_if_uhdev")
                        if skip_cond:
                            test, message, *rest = skip_cond.args

                            if test(self.uhdev):
                                pytest.skip(message)

                        self.uhdev.create_kernel_device()
                        now = time.time()
                        while not self.uhdev.is_ready() and time.time() - now < 5:
                            self.uhdev.dispatch(10)
                        if self.uhdev.get_evdev() is None:
                            logger.warning(
                                f"available list of input nodes: (default application is '{self.uhdev.application}')"
                            )
                            logger.warning(self.uhdev.input_nodes)
                        yield
                        self.uhdev = None
            except PermissionError:
                pytest.skip("Insufficient permissions, run me as root")

        @pytest.fixture(autouse=True)
        def check_taint(self):
            # we are abusing SysfsFile here, it's in /proc, but meh
            taint_file = SysfsFile("/proc/sys/kernel/tainted")
            taint = taint_file.int_value

            yield

            assert taint_file.int_value == taint

        def test_creation(self):
            """Make sure the device gets processed by the kernel and creates
            the expected application input node.

            If this fail, there is something wrong in the device report
            descriptors."""
            uhdev = self.uhdev
            assert uhdev is not None
            assert uhdev.get_evdev() is not None
            self.assertName(uhdev)
            assert len(uhdev.next_sync_events()) == 0
            assert uhdev.get_evdev() is not None


class HIDTestUdevRule(object):
    _instance = None
    """
    A context-manager compatible class that sets up our udev rules file and
    deletes it on context exit.

    This class is tailored to our test setup: it only sets up the udev rule
    on the **second** context and it cleans it up again on the last context
    removed. This matches the expected pytest setup: we enter a context for
    the session once, then once for each test (the first of which will
    trigger the udev rule) and once the last test exited and the session
    exited, we clean up after ourselves.
    """

    def __init__(self):
        self.refs = 0
        self.rulesfile = None

    def __enter__(self):
        self.refs += 1
        if self.refs == 2 and self.rulesfile is None:
            self.create_udev_rule()
            self.reload_udev_rules()

    def __exit__(self, exc_type, exc_value, traceback):
        self.refs -= 1
        if self.refs == 0 and self.rulesfile:
            os.remove(self.rulesfile.name)
            self.reload_udev_rules()

    def reload_udev_rules(self):
        import subprocess

        subprocess.run("udevadm control --reload-rules".split())
        subprocess.run("systemd-hwdb update".split())

    def create_udev_rule(self):
        import tempfile

        os.makedirs("/run/udev/rules.d", exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix="91-uhid-test-device-REMOVEME-",
            suffix=".rules",
            mode="w+",
            dir="/run/udev/rules.d",
            delete=False,
        ) as f:
            f.write(
                'KERNELS=="*input*", ATTRS{name}=="*uhid test *", ENV{LIBINPUT_IGNORE_DEVICE}="1"\n'
            )
            f.write(
                'KERNELS=="*input*", ATTRS{name}=="*uhid test * System Multi Axis", ENV{ID_INPUT_TOUCHSCREEN}="", ENV{ID_INPUT_SYSTEM_MULTIAXIS}="1"\n'
            )
            self.rulesfile = f

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = HIDTestUdevRule()
        return cls._instance
