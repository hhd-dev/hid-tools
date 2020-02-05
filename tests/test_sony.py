#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2020 Red Hat, Inc.
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

from test_gamepad import BaseGamepad, BaseTest

import logging
import random
import struct
logger = logging.getLogger('hidtools.test.sony')


class InvalidHIDCommunication(Exception):
    pass


class GamepadData(object):
    pass


class PS3Rumble(object):
    def __init__(self):
        self.right_duration = 0  # Right motor duration (0xff means forever)
        self.right_motor_on = 0  # Right (small) motor on/off, only supports values of 0 or 1 (off/on)
        self.left_duration = 0  # Left motor duration (0xff means forever)
        self.left_motor_force = 0  # left (large) motor, supports force values from 0 to 255
        self.offset = 1

    def parse(self, buf):
        padding, self.right_duration, self.right_motor_on, self.left_duration, self.left_motor_force = struct.unpack_from('< B B B B B', buf, self.offset)


class PS3LED(object):
    def __init__(self, idx):
        self.idx = idx
        self.offset = 11 + idx * 5
        self.time_enabled = 0  # the total time the led is active (0xff means forever)
        self.duty_length = 0  # how long a cycle is in deciseconds (0 means "really fast")
        self.enabled = 0
        self.duty_off = 0  # % of duty_length the led is off (0xff means 100%)
        self.duty_on = 0  # % of duty_length the led is on (0xff mean 100%)

    def parse(self, buf):
        self.time_enabled, self.duty_length, self.enabled, self.duty_off, self.duty_on = struct.unpack_from('< B B B B B', buf, self.offset)


class PS3LEDs(object):
    def __init__(self):
        self.offset = 10
        self.leds_bitmap = 0
        self.leds = [PS3LED(i) for i in range(4)]

    def parse(self, buf):
        (self.leds_bitmap, ) = struct.unpack_from('< B', buf, self.offset)
        for led in self.leds:
            led.parse(buf)

    def get_led(self, idx):
        return bool(self.leds_bitmap & (1 << idx + 1)), self.leds[idx]


class PS3Controller(BaseGamepad):
    buttons_map = {
        1: 'BTN_SELECT',
        2: 'BTN_THUMBL',            # L3
        3: 'BTN_THUMBR',            # R3
        4: 'BTN_START',
        5: 'BTN_DPAD_UP',
        6: 'BTN_DPAD_RIGHT',
        7: 'BTN_DPAD_DOWN',
        8: 'BTN_DPAD_LEFT',
        9: 'BTN_TL2',               # L2
        10: 'BTN_TR2',              # R2 */
        11: 'BTN_TL',               # L1 */
        12: 'BTN_TR',               # R1 */
        13: 'BTN_NORTH',            # options/triangle */
        14: 'BTN_EAST',             # back/circle */
        15: 'BTN_SOUTH',            # cross */
        16: 'BTN_WEST',             # view/square */
        17: 'BTN_MODE',             # PS button */
    }

    report_descriptor = [
        0x05, 0x01,                    # Usage Page (Generic Desktop)        0
        0x09, 0x04,                    # Usage (Joystick)                    2
        0xa1, 0x01,                    # Collection (Application)            4
        0xa1, 0x02,                    # .Collection (Logical)               6
        0x85, 0x01,                    # ..Report ID (1)                     8
        0x75, 0x08,                    # ..Report Size (8)                   10
        0x95, 0x01,                    # ..Report Count (1)                  12
        0x15, 0x00,                    # ..Logical Minimum (0)               14
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             16
        0x81, 0x03,                    # ..Input (Cnst,Var,Abs)              19
        0x75, 0x01,                    # ..Report Size (1)                   21
        0x95, 0x13,                    # ..Report Count (19)                 23
        0x15, 0x00,                    # ..Logical Minimum (0)               25
        0x25, 0x01,                    # ..Logical Maximum (1)               27
        0x35, 0x00,                    # ..Physical Minimum (0)              29
        0x45, 0x01,                    # ..Physical Maximum (1)              31
        0x05, 0x09,                    # ..Usage Page (Button)               33
        0x19, 0x01,                    # ..Usage Minimum (1)                 35
        0x29, 0x13,                    # ..Usage Maximum (19)                37
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              39
        0x75, 0x01,                    # ..Report Size (1)                   41
        0x95, 0x0d,                    # ..Report Count (13)                 43
        0x06, 0x00, 0xff,              # ..Usage Page (Vendor Defined Page 1) 45
        0x81, 0x03,                    # ..Input (Cnst,Var,Abs)              48
        0x15, 0x00,                    # ..Logical Minimum (0)               50
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             52
        0x05, 0x01,                    # ..Usage Page (Generic Desktop)      55
        0x09, 0x01,                    # ..Usage (Pointer)                   57
        0xa1, 0x00,                    # ..Collection (Physical)             59
        0x75, 0x08,                    # ...Report Size (8)                  61
        0x95, 0x04,                    # ...Report Count (4)                 63
        0x35, 0x00,                    # ...Physical Minimum (0)             65
        0x46, 0xff, 0x00,              # ...Physical Maximum (255)           67
        0x09, 0x30,                    # ...Usage (X)                        70
        0x09, 0x31,                    # ...Usage (Y)                        72
        0x09, 0x32,                    # ...Usage (Z)                        74
        0x09, 0x35,                    # ...Usage (Rz)                       76
        0x81, 0x02,                    # ...Input (Data,Var,Abs)             78
        0xc0,                          # ..End Collection                    80
        0x05, 0x01,                    # ..Usage Page (Generic Desktop)      81
        0x75, 0x08,                    # ..Report Size (8)                   83
        0x95, 0x27,                    # ..Report Count (39)                 85
        0x09, 0x01,                    # ..Usage (Pointer)                   87
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              89
        0x75, 0x08,                    # ..Report Size (8)                   91
        0x95, 0x30,                    # ..Report Count (48)                 93
        0x09, 0x01,                    # ..Usage (Pointer)                   95
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             97
        0x75, 0x08,                    # ..Report Size (8)                   99
        0x95, 0x30,                    # ..Report Count (48)                 101
        0x09, 0x01,                    # ..Usage (Pointer)                   103
        0xb1, 0x02,                    # ..Feature (Data,Var,Abs)            105
        0xc0,                          # .End Collection                     107
        0xa1, 0x02,                    # .Collection (Logical)               108
        0x85, 0x02,                    # ..Report ID (2)                     110
        0x75, 0x08,                    # ..Report Size (8)                   112
        0x95, 0x30,                    # ..Report Count (48)                 114
        0x09, 0x01,                    # ..Usage (Pointer)                   116
        0xb1, 0x02,                    # ..Feature (Data,Var,Abs)            118
        0xc0,                          # .End Collection                     120
        0xa1, 0x02,                    # .Collection (Logical)               121
        0x85, 0xee,                    # ..Report ID (238)                   123
        0x75, 0x08,                    # ..Report Size (8)                   125
        0x95, 0x30,                    # ..Report Count (48)                 127
        0x09, 0x01,                    # ..Usage (Pointer)                   129
        0xb1, 0x02,                    # ..Feature (Data,Var,Abs)            131
        0xc0,                          # .End Collection                     133
        0xa1, 0x02,                    # .Collection (Logical)               134
        0x85, 0xef,                    # ..Report ID (239)                   136
        0x75, 0x08,                    # ..Report Size (8)                   138
        0x95, 0x30,                    # ..Report Count (48)                 140
        0x09, 0x01,                    # ..Usage (Pointer)                   142
        0xb1, 0x02,                    # ..Feature (Data,Var,Abs)            144
        0xc0,                          # .End Collection                     146
        0xc0,                          # End Collection                      147
    ]

    def __init__(self, rdesc=report_descriptor, name='Sony PLAYSTATION(R)3 Controller'):
        super().__init__(rdesc, name, (3, 0x054c, 0x0268))
        self.uniq = ':'.join([f'{random.randint(0, 0xff):02x}' for i in range(6)])
        self.buttons = tuple(range(1, 18))
        self.current_mode = 'plugged-in'
        self.rumble = PS3Rumble()
        self.hw_leds = PS3LEDs()

    def get_report(self, req, rnum, rtype):
        rdesc = None
        for v in self.parsed_rdesc.feature_reports.values():
            if v.report_ID == rnum:
                rdesc = v

        logger.debug(f'get_report {rdesc}, {req}, {rnum}, {rtype}')

        if rnum == 0xf2:
            # undocumented report in the HID report descriptor:
            # the MAC address of the device is stored in the bytes 4-9
            # rest has been dumped on a Sixaxis controller
            r = [0xf2, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x40, 0x80, 0x18, 0x01, 0x8a]

            # store the uniq value in the report
            for id, v in enumerate(self.uniq.split(':')):
                r[4 + id] = int(v, 16)

            # change the mode to operational
            self.current_mode = 'operational'
            return (0, r)

        if rnum == 0xf5:
            return (0, [0x01, 0x00, 0x18, 0x5e, 0x0f, 0x71, 0xa4, 0xbb])

        if rdesc is None:
            return (1, [])

        return (1, [])

    def set_report(self, req, rnum, rtype, data):
        rdesc = None
        for v in self.parsed_rdesc.feature_reports.values():
            if v.report_ID == rnum:
                rdesc = v

        logger.info(f'set_report {bool(rdesc)}, {req}, {rnum}, {rtype}, {data}')

        if rdesc is None:
            return 1

        if rnum != 1:
            return 1

        # we have an output report to set the rumbles and LEDs
        buf = struct.pack(f'< {len(data)}B', *data)
        self.rumble.parse(buf)
        self.hw_leds.parse(buf)

        return 0

    def output_report(self, data, size, rtype):
        logger.debug(f'output_report {data[:size + 1]}, {size}, {rtype}')

    def create_report(self, *, left=(None, None), right=(None, None), hat_switch=None, buttons=None, reportID=None):
        """
        Return an input report for this device.

        :param left: a tuple of absolute (x, y) value of the left joypad
            where ``None`` is "leave unchanged"
        :param right: a tuple of absolute (x, y) value of the right joypad
            where ``None`` is "leave unchanged"
        :param hat_switch: an absolute angular value of the hat switch
            where ``None`` is "leave unchanged"
        :param buttons: a dict of index/bool for the button states,
            where ``None`` is "leave unchanged"
        :param reportID: the numeric report ID for this report, if needed
        """
        if self.current_mode != 'operational':
            raise InvalidHIDCommunication(f'controller in incorrect mode: {self.current_mode}')

        return super().create_report(left=left, right=right, hat_switch=hat_switch, buttons=buttons, reportID=reportID, application='Joystick')


class SonyBaseTest:
    class SonyTest(BaseTest.TestGamepad):
        def uhdev_is_ready(self):
            return super().uhdev_is_ready() and len(self.uhdev.led_classes) == 4

        def test_led(self):
            # emulate a 'PS' button press to tell the kernel we are ready to accept events
            self.assert_button(17)

            # drain any remaining udev events
            while self.uhdev.dispatch(10):
                pass

            for k, v in self.uhdev.led_classes.items():
                # the kernel might have set a LED for us
                logger.info(f'{k}: {v.brightness}')

                idx = int(k[-1]) - 1
                assert self.uhdev.hw_leds.get_led(idx)[0] == bool(v.brightness)

                v.brightness = 0
                self.uhdev.dispatch(10)
                assert self.uhdev.hw_leds.get_led(idx)[0] is False

                v.brightness = v.max_brightness
                self.uhdev.dispatch(10)
                assert self.uhdev.hw_leds.get_led(idx)[0]


class TestPS3Controller(SonyBaseTest.SonyTest):
    def create_device(self):
        return PS3Controller()
