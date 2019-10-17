#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2019 Red Hat, Inc.
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

import base
import libevdev
import sys
from base import main, setUpModule, tearDownModule  # noqa

import logging
logger = logging.getLogger('hidtools.test.gamepad')


class InvalidHIDCommunication(Exception):
    pass


class GamepadData(object):
    pass


class BaseGamepad(base.UHIDTestDevice):
    def __init__(self, rdesc, name=None, info=None):
        assert rdesc is not None
        super().__init__(name, 'Joystick', info=info, rdesc=rdesc)
        self.buttons = (1, 2, 3)
        self._buttons = {}
        self.left = (127, 127)
        self.right = (127, 127)
        self.hat_switch = 15

    def create_report(self, *, left=(None, None), right=(None, None), hat_switch=None, buttons=None, reportID=None, application='Game Pad'):
        """
        Return an input report for this device.

        :param left: a tuple of absolute (x, y) value of the left joypad
            where ``None`` is "leave unchanged"
        :param right: a tuple of absolute (x, y) value of the right joypad
            where ``None`` is "leave unchanged"
        :param hat_switch: an absolute angular value of the hat switch
            where ``None`` is "leave unchanged"
        :param buttons: a (0, 1, 2, 3) tuple of bools for the button states,
            where ``None`` is "leave unchanged"
        :param reportID: the numeric report ID for this report, if needed
        :param application: the application used to report the values
        """
        if buttons is not None:
            for i, b in enumerate(buttons):
                if b is not None:
                    self._buttons[self.buttons.index(i + 1) + 1] = b

        def replace_none_in_tuple(item, default):
            if item is None:
                item = (None, None)

            if None in item:
                if item[0] is None:
                    item = (default[0], item[1])
                if item[1] is None:
                    item = (item[0], default[1])

            return item

        right = replace_none_in_tuple(right, self.right)
        self.right = right
        left = replace_none_in_tuple(left, self.left)
        self.left = left

        if hat_switch is None:
            hat_switch = self.hat_switch
        else:
            self.hat_switch = hat_switch

        reportID = reportID or self.default_reportID

        gamepad = GamepadData()
        for i, b in self._buttons.items():
            gamepad.__setattr__(f'b{i}', int(b) if b is not None else 0)
        gamepad.x = left[0]
        gamepad.y = left[1]
        gamepad.rudder = right[0]
        gamepad.throttle = right[1]
        gamepad.hatswitch = hat_switch
        return super().create_report(gamepad, reportID=reportID, application=application)

    def event(self, *, left=(None, None), right=(None, None), hat_switch=None, buttons=None):
        """
        Send an input event on the default report ID.

        :param left: a tuple of absolute (x, y) value of the left joypad
            where ``None`` is "leave unchanged"
        :param right: a tuple of absolute (x, y) value of the right joypad
            where ``None`` is "leave unchanged"
        :param hat_switch: an absolute angular value of the hat switch
            where ``None`` is "leave unchanged"
        :param buttons: a (0, 1, 2, 3) tuple of bools for the button states,
            where ``None`` is "leave unchanged"
        """
        r = self.create_report(left=left, right=right, hat_switch=hat_switch, buttons=buttons)
        self.call_input_event(r)
        return [r]


class JoystickGamepad(BaseGamepad):
    def create_report(self, *, left=(None, None), right=(None, None), hat_switch=None, buttons=None, reportID=None):
        """
        Return an input report for this device.

        :param left: a tuple of absolute (x, y) value of the left joypad
            where ``None`` is "leave unchanged"
        :param right: a tuple of absolute (x, y) value of the right joypad
            where ``None`` is "leave unchanged"
        :param hat_switch: an absolute angular value of the hat switch
            where ``None`` is "leave unchanged"
        :param buttons: a (0, 1, 2, 3) tuple of bools for the button states,
            where ``None`` is "leave unchanged"
        :param reportID: the numeric report ID for this report, if needed
        """
        return super().create_report(left=left, right=right, hat_switch=hat_switch, buttons=buttons, reportID=reportID, application='Joystick')


class SaitekGamepad(JoystickGamepad):
    report_descriptor = [
        0x05, 0x01,                    # Usage Page (Generic Desktop)        0
        0x09, 0x04,                    # Usage (Joystick)                    2
        0xa1, 0x01,                    # Collection (Application)            4
        0x09, 0x01,                    # .Usage (Pointer)                    6
        0xa1, 0x00,                    # .Collection (Physical)              8
        0x85, 0x01,                    # ..Report ID (1)                     10
        0x09, 0x30,                    # ..Usage (X)                         12
        0x15, 0x00,                    # ..Logical Minimum (0)               14
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             16
        0x35, 0x00,                    # ..Physical Minimum (0)              19
        0x46, 0xff, 0x00,              # ..Physical Maximum (255)            21
        0x75, 0x08,                    # ..Report Size (8)                   24
        0x95, 0x01,                    # ..Report Count (1)                  26
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              28
        0x09, 0x31,                    # ..Usage (Y)                         30
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              32
        0x05, 0x02,                    # ..Usage Page (Simulation Controls)  34
        0x09, 0xba,                    # ..Usage (Rudder)                    36
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              38
        0x09, 0xbb,                    # ..Usage (Throttle)                  40
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              42
        0x05, 0x09,                    # ..Usage Page (Button)               44
        0x19, 0x01,                    # ..Usage Minimum (1)                 46
        0x29, 0x0c,                    # ..Usage Maximum (12)                48
        0x25, 0x01,                    # ..Logical Maximum (1)               50
        0x45, 0x01,                    # ..Physical Maximum (1)              52
        0x75, 0x01,                    # ..Report Size (1)                   54
        0x95, 0x0c,                    # ..Report Count (12)                 56
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              58
        0x95, 0x01,                    # ..Report Count (1)                  60
        0x75, 0x00,                    # ..Report Size (0)                   62
        0x81, 0x03,                    # ..Input (Cnst,Var,Abs)              64
        0x05, 0x01,                    # ..Usage Page (Generic Desktop)      66
        0x09, 0x39,                    # ..Usage (Hat switch)                68
        0x25, 0x07,                    # ..Logical Maximum (7)               70
        0x46, 0x3b, 0x01,              # ..Physical Maximum (315)            72
        0x55, 0x00,                    # ..Unit Exponent (0)                 75
        0x65, 0x44,                    # ..Unit (Degrees^4,EngRotation)      77
        0x75, 0x04,                    # ..Report Size (4)                   79
        0x81, 0x42,                    # ..Input (Data,Var,Abs,Null)         81
        0x65, 0x00,                    # ..Unit (None)                       83
        0xc0,                          # .End Collection                     85
        0x05, 0x0f,                    # .Usage Page (Vendor Usage Page 0x0f) 86
        0x09, 0x92,                    # .Usage (Vendor Usage 0x92)          88
        0xa1, 0x02,                    # .Collection (Logical)               90
        0x85, 0x02,                    # ..Report ID (2)                     92
        0x09, 0xa0,                    # ..Usage (Vendor Usage 0xa0)         94
        0x09, 0x9f,                    # ..Usage (Vendor Usage 0x9f)         96
        0x25, 0x01,                    # ..Logical Maximum (1)               98
        0x45, 0x00,                    # ..Physical Maximum (0)              100
        0x75, 0x01,                    # ..Report Size (1)                   102
        0x95, 0x02,                    # ..Report Count (2)                  104
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              106
        0x75, 0x06,                    # ..Report Size (6)                   108
        0x95, 0x01,                    # ..Report Count (1)                  110
        0x81, 0x03,                    # ..Input (Cnst,Var,Abs)              112
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         114
        0x75, 0x07,                    # ..Report Size (7)                   116
        0x25, 0x7f,                    # ..Logical Maximum (127)             118
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              120
        0x09, 0x94,                    # ..Usage (Vendor Usage 0x94)         122
        0x75, 0x01,                    # ..Report Size (1)                   124
        0x25, 0x01,                    # ..Logical Maximum (1)               126
        0x81, 0x02,                    # ..Input (Data,Var,Abs)              128
        0xc0,                          # .End Collection                     130
        0x09, 0x21,                    # .Usage (Vendor Usage 0x21)          131
        0xa1, 0x02,                    # .Collection (Logical)               133
        0x85, 0x0b,                    # ..Report ID (11)                    135
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         137
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             139
        0x75, 0x08,                    # ..Report Size (8)                   142
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             144
        0x09, 0x53,                    # ..Usage (Vendor Usage 0x53)         146
        0x25, 0x0a,                    # ..Logical Maximum (10)              148
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             150
        0x09, 0x50,                    # ..Usage (Vendor Usage 0x50)         152
        0x27, 0xfe, 0xff, 0x00, 0x00,  # ..Logical Maximum (65534)           154
        0x47, 0xfe, 0xff, 0x00, 0x00,  # ..Physical Maximum (65534)          159
        0x75, 0x10,                    # ..Report Size (16)                  164
        0x55, 0xfd,                    # ..Unit Exponent (237)               166
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           168
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             171
        0x55, 0x00,                    # ..Unit Exponent (0)                 173
        0x65, 0x00,                    # ..Unit (None)                       175
        0x09, 0x54,                    # ..Usage (Vendor Usage 0x54)         177
        0x55, 0xfd,                    # ..Unit Exponent (237)               179
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           181
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             184
        0x55, 0x00,                    # ..Unit Exponent (0)                 186
        0x65, 0x00,                    # ..Unit (None)                       188
        0x09, 0xa7,                    # ..Usage (Vendor Usage 0xa7)         190
        0x55, 0xfd,                    # ..Unit Exponent (237)               192
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           194
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             197
        0x55, 0x00,                    # ..Unit Exponent (0)                 199
        0x65, 0x00,                    # ..Unit (None)                       201
        0xc0,                          # .End Collection                     203
        0x09, 0x5a,                    # .Usage (Vendor Usage 0x5a)          204
        0xa1, 0x02,                    # .Collection (Logical)               206
        0x85, 0x0c,                    # ..Report ID (12)                    208
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         210
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             212
        0x45, 0x00,                    # ..Physical Maximum (0)              215
        0x75, 0x08,                    # ..Report Size (8)                   217
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             219
        0x09, 0x5c,                    # ..Usage (Vendor Usage 0x5c)         221
        0x26, 0x10, 0x27,              # ..Logical Maximum (10000)           223
        0x46, 0x10, 0x27,              # ..Physical Maximum (10000)          226
        0x75, 0x10,                    # ..Report Size (16)                  229
        0x55, 0xfd,                    # ..Unit Exponent (237)               231
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           233
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             236
        0x55, 0x00,                    # ..Unit Exponent (0)                 238
        0x65, 0x00,                    # ..Unit (None)                       240
        0x09, 0x5b,                    # ..Usage (Vendor Usage 0x5b)         242
        0x25, 0x7f,                    # ..Logical Maximum (127)             244
        0x75, 0x08,                    # ..Report Size (8)                   246
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             248
        0x09, 0x5e,                    # ..Usage (Vendor Usage 0x5e)         250
        0x26, 0x10, 0x27,              # ..Logical Maximum (10000)           252
        0x75, 0x10,                    # ..Report Size (16)                  255
        0x55, 0xfd,                    # ..Unit Exponent (237)               257
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           259
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             262
        0x55, 0x00,                    # ..Unit Exponent (0)                 264
        0x65, 0x00,                    # ..Unit (None)                       266
        0x09, 0x5d,                    # ..Usage (Vendor Usage 0x5d)         268
        0x25, 0x7f,                    # ..Logical Maximum (127)             270
        0x75, 0x08,                    # ..Report Size (8)                   272
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             274
        0xc0,                          # .End Collection                     276
        0x09, 0x73,                    # .Usage (Vendor Usage 0x73)          277
        0xa1, 0x02,                    # .Collection (Logical)               279
        0x85, 0x0d,                    # ..Report ID (13)                    281
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         283
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             285
        0x45, 0x00,                    # ..Physical Maximum (0)              288
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             290
        0x09, 0x70,                    # ..Usage (Vendor Usage 0x70)         292
        0x15, 0x81,                    # ..Logical Minimum (-127)            294
        0x25, 0x7f,                    # ..Logical Maximum (127)             296
        0x36, 0xf0, 0xd8,              # ..Physical Minimum (-10000)         298
        0x46, 0x10, 0x27,              # ..Physical Maximum (10000)          301
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             304
        0xc0,                          # .End Collection                     306
        0x09, 0x6e,                    # .Usage (Vendor Usage 0x6e)          307
        0xa1, 0x02,                    # .Collection (Logical)               309
        0x85, 0x0e,                    # ..Report ID (14)                    311
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         313
        0x15, 0x00,                    # ..Logical Minimum (0)               315
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             317
        0x35, 0x00,                    # ..Physical Minimum (0)              320
        0x45, 0x00,                    # ..Physical Maximum (0)              322
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             324
        0x09, 0x70,                    # ..Usage (Vendor Usage 0x70)         326
        0x25, 0x7f,                    # ..Logical Maximum (127)             328
        0x46, 0x10, 0x27,              # ..Physical Maximum (10000)          330
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             333
        0x09, 0x6f,                    # ..Usage (Vendor Usage 0x6f)         335
        0x15, 0x81,                    # ..Logical Minimum (-127)            337
        0x36, 0xf0, 0xd8,              # ..Physical Minimum (-10000)         339
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             342
        0x09, 0x71,                    # ..Usage (Vendor Usage 0x71)         344
        0x15, 0x00,                    # ..Logical Minimum (0)               346
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             348
        0x35, 0x00,                    # ..Physical Minimum (0)              351
        0x46, 0x68, 0x01,              # ..Physical Maximum (360)            353
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             356
        0x09, 0x72,                    # ..Usage (Vendor Usage 0x72)         358
        0x75, 0x10,                    # ..Report Size (16)                  360
        0x26, 0x10, 0x27,              # ..Logical Maximum (10000)           362
        0x46, 0x10, 0x27,              # ..Physical Maximum (10000)          365
        0x55, 0xfd,                    # ..Unit Exponent (237)               368
        0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           370
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             373
        0x55, 0x00,                    # ..Unit Exponent (0)                 375
        0x65, 0x00,                    # ..Unit (None)                       377
        0xc0,                          # .End Collection                     379
        0x09, 0x77,                    # .Usage (Vendor Usage 0x77)          380
        0xa1, 0x02,                    # .Collection (Logical)               382
        0x85, 0x51,                    # ..Report ID (81)                    384
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         386
        0x25, 0x7f,                    # ..Logical Maximum (127)             388
        0x45, 0x00,                    # ..Physical Maximum (0)              390
        0x75, 0x08,                    # ..Report Size (8)                   392
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             394
        0x09, 0x78,                    # ..Usage (Vendor Usage 0x78)         396
        0xa1, 0x02,                    # ..Collection (Logical)              398
        0x09, 0x7b,                    # ...Usage (Vendor Usage 0x7b)        400
        0x09, 0x79,                    # ...Usage (Vendor Usage 0x79)        402
        0x09, 0x7a,                    # ...Usage (Vendor Usage 0x7a)        404
        0x15, 0x01,                    # ...Logical Minimum (1)              406
        0x25, 0x03,                    # ...Logical Maximum (3)              408
        0x91, 0x00,                    # ...Output (Data,Arr,Abs)            410
        0xc0,                          # ..End Collection                    412
        0x09, 0x7c,                    # ..Usage (Vendor Usage 0x7c)         413
        0x15, 0x00,                    # ..Logical Minimum (0)               415
        0x26, 0xfe, 0x00,              # ..Logical Maximum (254)             417
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             420
        0xc0,                          # .End Collection                     422
        0x09, 0x92,                    # .Usage (Vendor Usage 0x92)          423
        0xa1, 0x02,                    # .Collection (Logical)               425
        0x85, 0x52,                    # ..Report ID (82)                    427
        0x09, 0x96,                    # ..Usage (Vendor Usage 0x96)         429
        0xa1, 0x02,                    # ..Collection (Logical)              431
        0x09, 0x9a,                    # ...Usage (Vendor Usage 0x9a)        433
        0x09, 0x99,                    # ...Usage (Vendor Usage 0x99)        435
        0x09, 0x97,                    # ...Usage (Vendor Usage 0x97)        437
        0x09, 0x98,                    # ...Usage (Vendor Usage 0x98)        439
        0x09, 0x9b,                    # ...Usage (Vendor Usage 0x9b)        441
        0x09, 0x9c,                    # ...Usage (Vendor Usage 0x9c)        443
        0x15, 0x01,                    # ...Logical Minimum (1)              445
        0x25, 0x06,                    # ...Logical Maximum (6)              447
        0x91, 0x00,                    # ...Output (Data,Arr,Abs)            449
        0xc0,                          # ..End Collection                    451
        0xc0,                          # .End Collection                     452
        0x05, 0xff,                    # .Usage Page (Vendor Usage Page 0xff) 453
        0x0a, 0x01, 0x03,              # .Usage (Vendor Usage 0x301)         455
        0xa1, 0x02,                    # .Collection (Logical)               458
        0x85, 0x40,                    # ..Report ID (64)                    460
        0x0a, 0x02, 0x03,              # ..Usage (Vendor Usage 0x302)        462
        0xa1, 0x02,                    # ..Collection (Logical)              465
        0x1a, 0x11, 0x03,              # ...Usage Minimum (785)              467
        0x2a, 0x20, 0x03,              # ...Usage Maximum (800)              470
        0x25, 0x10,                    # ...Logical Maximum (16)             473
        0x91, 0x00,                    # ...Output (Data,Arr,Abs)            475
        0xc0,                          # ..End Collection                    477
        0x0a, 0x03, 0x03,              # ..Usage (Vendor Usage 0x303)        478
        0x15, 0x00,                    # ..Logical Minimum (0)               481
        0x27, 0xff, 0xff, 0x00, 0x00,  # ..Logical Maximum (65535)           483
        0x75, 0x10,                    # ..Report Size (16)                  488
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             490
        0xc0,                          # .End Collection                     492
        0x05, 0x0f,                    # .Usage Page (Vendor Usage Page 0x0f) 493
        0x09, 0x7d,                    # .Usage (Vendor Usage 0x7d)          495
        0xa1, 0x02,                    # .Collection (Logical)               497
        0x85, 0x43,                    # ..Report ID (67)                    499
        0x09, 0x7e,                    # ..Usage (Vendor Usage 0x7e)         501
        0x26, 0x80, 0x00,              # ..Logical Maximum (128)             503
        0x46, 0x10, 0x27,              # ..Physical Maximum (10000)          506
        0x75, 0x08,                    # ..Report Size (8)                   509
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             511
        0xc0,                          # .End Collection                     513
        0x09, 0x7f,                    # .Usage (Vendor Usage 0x7f)          514
        0xa1, 0x02,                    # .Collection (Logical)               516
        0x85, 0x0b,                    # ..Report ID (11)                    518
        0x09, 0x80,                    # ..Usage (Vendor Usage 0x80)         520
        0x26, 0xff, 0x7f,              # ..Logical Maximum (32767)           522
        0x45, 0x00,                    # ..Physical Maximum (0)              525
        0x75, 0x0f,                    # ..Report Size (15)                  527
        0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            529
        0x09, 0xa9,                    # ..Usage (Vendor Usage 0xa9)         531
        0x25, 0x01,                    # ..Logical Maximum (1)               533
        0x75, 0x01,                    # ..Report Size (1)                   535
        0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            537
        0x09, 0x83,                    # ..Usage (Vendor Usage 0x83)         539
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             541
        0x75, 0x08,                    # ..Report Size (8)                   544
        0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            546
        0xc0,                          # .End Collection                     548
        0x09, 0xab,                    # .Usage (Vendor Usage 0xab)          549
        0xa1, 0x03,                    # .Collection (Report)                551
        0x85, 0x15,                    # ..Report ID (21)                    553
        0x09, 0x25,                    # ..Usage (Vendor Usage 0x25)         555
        0xa1, 0x02,                    # ..Collection (Logical)              557
        0x09, 0x26,                    # ...Usage (Vendor Usage 0x26)        559
        0x09, 0x30,                    # ...Usage (Vendor Usage 0x30)        561
        0x09, 0x32,                    # ...Usage (Vendor Usage 0x32)        563
        0x09, 0x31,                    # ...Usage (Vendor Usage 0x31)        565
        0x09, 0x33,                    # ...Usage (Vendor Usage 0x33)        567
        0x09, 0x34,                    # ...Usage (Vendor Usage 0x34)        569
        0x15, 0x01,                    # ...Logical Minimum (1)              571
        0x25, 0x06,                    # ...Logical Maximum (6)              573
        0xb1, 0x00,                    # ...Feature (Data,Arr,Abs)           575
        0xc0,                          # ..End Collection                    577
        0xc0,                          # .End Collection                     578
        0x09, 0x89,                    # .Usage (Vendor Usage 0x89)          579
        0xa1, 0x03,                    # .Collection (Report)                581
        0x85, 0x16,                    # ..Report ID (22)                    583
        0x09, 0x8b,                    # ..Usage (Vendor Usage 0x8b)         585
        0xa1, 0x02,                    # ..Collection (Logical)              587
        0x09, 0x8c,                    # ...Usage (Vendor Usage 0x8c)        589
        0x09, 0x8d,                    # ...Usage (Vendor Usage 0x8d)        591
        0x09, 0x8e,                    # ...Usage (Vendor Usage 0x8e)        593
        0x25, 0x03,                    # ...Logical Maximum (3)              595
        0xb1, 0x00,                    # ...Feature (Data,Arr,Abs)           597
        0xc0,                          # ..End Collection                    599
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         600
        0x15, 0x00,                    # ..Logical Minimum (0)               602
        0x26, 0xfe, 0x00,              # ..Logical Maximum (254)             604
        0xb1, 0x02,                    # ..Feature (Data,Var,Abs)            607
        0xc0,                          # .End Collection                     609
        0x09, 0x90,                    # .Usage (Vendor Usage 0x90)          610
        0xa1, 0x03,                    # .Collection (Report)                612
        0x85, 0x50,                    # ..Report ID (80)                    614
        0x09, 0x22,                    # ..Usage (Vendor Usage 0x22)         616
        0x26, 0xff, 0x00,              # ..Logical Maximum (255)             618
        0x91, 0x02,                    # ..Output (Data,Var,Abs)             621
        0xc0,                          # .End Collection                     623
        0xc0,                          # End Collection                      624
    ]

    def __init__(self, rdesc=report_descriptor, name=None):
        super().__init__(rdesc, name, (3, 0x06a3, 0xff0d))
        self.buttons = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)


class BaseTest:
    class TestGamepad(base.BaseTestCase.TestUhid):
        def test_buttons(self):
            """check for button reliability."""
            uhdev = self.uhdev
            syn_event = self.syn_event

            buttons_map = [
                'BTN_TRIGGER',  # corresponds to Button 1
                'BTN_THUMB',
                'BTN_THUMB2',
                'BTN_TOP',
                'BTN_TOP2',
                'BTN_PINKIE',
                'BTN_BASE',
                'BTN_BASE2',
                'BTN_BASE3',
                'BTN_BASE4',
                'BTN_BASE5',
                'BTN_BASE6',
                'BTN_DEAD',
            ]

            # first send an empty report to initialize the axes
            r = uhdev.event()
            events = uhdev.next_sync_events()
            self.debug_reports(r, uhdev, events)

            for button in uhdev.buttons:
                buttons = [None] * (max(uhdev.buttons))
                b = button - 1  # buttons are 1-indexed
                key = libevdev.evbit(buttons_map[b])

                buttons[b] = True
                r = uhdev.event(buttons=buttons)
                expected_event = libevdev.InputEvent(key, 1)
                events = uhdev.next_sync_events()
                self.debug_reports(r, uhdev, events)
                self.assertInputEventsIn((syn_event, expected_event), events)
                self.assertEqual(uhdev.evdev.value[key], 1)

                buttons[b] = False

                r = uhdev.event(buttons=buttons)
                expected_event = libevdev.InputEvent(key, 0)
                events = uhdev.next_sync_events()
                self.debug_reports(r, uhdev, events)
                self.assertInputEventsIn((syn_event, expected_event), events)
                self.assertEqual(uhdev.evdev.value[key], 0)

            r = uhdev.event(buttons=(True, True))
            expected_event0 = libevdev.InputEvent(libevdev.EV_KEY.BTN_TRIGGER, 1)
            expected_event1 = libevdev.InputEvent(libevdev.EV_KEY.BTN_THUMB, 1)
            events = uhdev.next_sync_events()
            self.debug_reports(r, uhdev, events)
            self.assertInputEventsIn((syn_event, expected_event0, expected_event1), events)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_TRIGGER], 1)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_THUMB], 1)

            r = uhdev.event(buttons=(False, None))
            expected_event = libevdev.InputEvent(libevdev.EV_KEY.BTN_TRIGGER, 0)
            events = uhdev.next_sync_events()
            self.debug_reports(r, uhdev, events)
            self.assertInputEventsIn((syn_event, expected_event), events)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_THUMB], 1)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_TRIGGER], 0)

            r = uhdev.event(buttons=(None, False))
            expected_event = libevdev.InputEvent(libevdev.EV_KEY.BTN_THUMB, 0)
            events = uhdev.next_sync_events()
            self.debug_reports(r, uhdev, events)
            self.assertInputEventsIn((syn_event, expected_event), events)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_THUMB], 0)
            self.assertEqual(uhdev.evdev.value[libevdev.EV_KEY.BTN_TRIGGER], 0)


class TestSaitekGamepad(BaseTest.TestGamepad):
    def create_device(self):
        return SaitekGamepad()


if __name__ == "__main__":
    main(sys.argv[1:])
