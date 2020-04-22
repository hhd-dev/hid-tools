#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2017 Red Hat, Inc.
# Copyright (c) 2020 Wacom Technology Corp.
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
# Authors:
#     Jason Gerecke <jason.gerecke@wacom.com>

"""
Tests for the Wacom driver generic codepath.

This module tests the function of the Wacom driver's generic codepath.
The generic codepath is used by devices which are not explicitly listed
in the driver's device table. It uses the device's HID descriptor to
decode reports sent by the device.
"""

import tests.base as base
import libevdev

import logging
logger = logging.getLogger('hidtools.test.wacom')


class ReportData():
    """
    Placeholder for HID report values.
    """
    pass


class BaseTablet(base.UHIDTestDevice):
    """
    Skeleton object for all kinds of tablet devices.
    """
    def __init__(self, rdesc, name=None, info=None):
        assert rdesc is not None
        super().__init__(name, 'Pen', input_info=info, rdesc=rdesc)

    def create_report(self, x, y, pressure, inrange=None, reportID=None):
        """
        Return an input report for this device.

        :param x: absolute x
        :param y: absolute y
        :param pressure: pressure
        :param inrange: a boolean indicating if the pen is in range
        :param reportID: the numeric report ID for this report, if needed
        """
        if inrange is not None:
            self.inrange = inrange
        inrange = self.inrange

        reportID = reportID or self.default_reportID

        report = ReportData()
        report.x = x
        report.y = y
        report.tippressure = pressure
        report.tipswitch = pressure > 0
        report.inrange = inrange
        return super().create_report(report, reportID=reportID)

    def event(self, x, y, pressure, inrange=None):
        """
        Send an input event on the default report ID.

        :param x: absolute x
        :param y: absolute y
        :param inrange: a boolean indicating if the pen is in range
        """
        r = self.create_report(x, y, pressure, inrange)
        self.call_input_event(r)
        return [r]


class OpaqueTablet(BaseTablet):
    """
    Bare-bones opaque tablet with a minimum of features.

    A tablet stripped down to its absolute core. It is capable of
    reporting X/Y position and if the pen is in contact. No pressure,
    no barrel switches, no eraser. Notably it *does* report an "In
    Range" flag, but this is only because the Wacom driver expects
    one to function properly. The device uses only standard HID usages,
    not any of Wacom's vendor-defined pages.
    """
    report_descriptor = [
        0x05, 0x0D,                     # . Usage Page (Digitizer),
        0x09, 0x01,                     # . Usage (Digitizer),
        0xA1, 0x01,                     # . Collection (Application),
        0x85, 0x01,                     # .     Report ID (1),
        0x09, 0x20,                     # .     Usage (Stylus),
        0xA1, 0x00,                     # .     Collection (Physical),
        0x09, 0x42,                     # .         Usage (Tip Switch),
        0x09, 0x32,                     # .         Usage (In Range),
        0x15, 0x00,                     # .         Logical Minimum (0),
        0x25, 0x01,                     # .         Logical Maximum (1),
        0x75, 0x01,                     # .         Report Size (1),
        0x95, 0x02,                     # .         Report Count (2),
        0x81, 0x02,                     # .         Input (Variable),
        0x95, 0x06,                     # .         Report Count (6),
        0x81, 0x03,                     # .         Input (Constant, Variable),
        0x05, 0x01,                     # .         Usage Page (Desktop),
        0x09, 0x30,                     # .         Usage (X),
        0x27, 0x80, 0x3E, 0x00, 0x00,   # .         Logical Maximum (16000),
        0x47, 0x80, 0x3E, 0x00, 0x00,   # .         Physical Maximum (16000),
        0x65, 0x11,                     # .         Unit (Centimeter),
        0x55, 0x0D,                     # .         Unit Exponent (13),
        0x75, 0x10,                     # .         Report Size (16),
        0x95, 0x01,                     # .         Report Count (1),
        0x81, 0x02,                     # .         Input (Variable),
        0x09, 0x31,                     # .         Usage (Y),
        0x27, 0x28, 0x23, 0x00, 0x00,   # .         Logical Maximum (9000),
        0x47, 0x28, 0x23, 0x00, 0x00,   # .         Physical Maximum (9000),
        0x81, 0x02,                     # .         Input (Variable),
        0xC0,                           # .     End Collection,
        0xC0,                           # . End Collection,
    ]

    def __init__(self,
                 rdesc=report_descriptor,
                 name=None,
                 info=(0x3, 0x056a, 0x9999)):
        super().__init__(rdesc, name, info)
        self.default_reportID = 1


class BaseTest:
    class TestTablet(base.BaseTestCase.TestUhid):
        def sync_and_assert_events(self, report, expected_events, auto_syn=True, strict=False):
            """
            Assert we see the expected events in response to a report.
            """
            uhdev = self.uhdev
            syn_event = self.syn_event
            if auto_syn:
                expected_events.append(syn_event)
            actual_events = uhdev.next_sync_events()
            self.debug_reports(report, uhdev, actual_events)
            if strict:
                self.assertInputEvents(expected_events, actual_events)
            else:
                self.assertInputEventsIn(expected_events, actual_events)

        def assertName(self, uhdev):
            """
            Assert that the name is as we expect.

            The Wacom driver applies a number of decorations to the name
            provided by the hardware. We cannot rely on the definition of
            this assertion from the base class to work properly.
            """
            evdev = uhdev.get_evdev()
            expected_name = uhdev.name + " Pen"
            if "wacom" not in expected_name.lower():
                expected_name = "Wacom " + expected_name
            assert evdev.name == expected_name

        def test_prop_direct(self):
            """
            Todo: Verify that INPUT_PROP_DIRECT is set on display devices.
            """
            pass

        def test_prop_pointer(self):
            """
            Todo: Verify that INPUT_PROP_POINTER is set on opaque devices.
            """
            pass


class TestOpaqueTablet(BaseTest.TestTablet):
    def create_device(self):
        return OpaqueTablet()

    def test_sanity(self):
        """
        Bring a pen into contact with the tablet, then remove it.

        Ensure that we get the basic tool/touch/motion events that should
        be sent by the driver.
        """
        uhdev = self.uhdev

        self.sync_and_assert_events(
            uhdev.event(100, 200, pressure=300, inrange=True),
            [
                libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN, 1),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_X, 100),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_Y, 200),
                libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH, 1),
            ]
        )

        self.sync_and_assert_events(
            uhdev.event(110, 220, pressure=0),
            [
                libevdev.InputEvent(libevdev.EV_ABS.ABS_X, 110),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_Y, 220),
                libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH, 0),
            ]
        )

        self.sync_and_assert_events(
            uhdev.event(120, 230, pressure=0, inrange=False),
            [
                libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN, 0),
            ]
        )

        self.sync_and_assert_events(uhdev.event(130, 240, pressure=0), [], auto_syn=False, strict=True)
