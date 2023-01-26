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

# This is for generic devices

import hidtools
from hidtools.hid import HidUnit, Unit
import pytest
import logging

logger = logging.getLogger("hidtools.test.hid")


class TestReportDescriptor:
    def test_vendor_specific_collection(self):
        # From https://gitlab.freedesktop.org/libevdev/hid-tools/-/issues/25
        # contains Collection (Vendor_defined) which crashed hidtools
        # fmt: off
        report_descriptor = [
            0x05, 0x84,                    # Usage Page (Power Device)           0
            0x09, 0x04,                    # Usage (Vendor Usage 0x04)           2
            0xa1, 0x01,                    # Collection (Application)            4
            0x09, 0x24,                    # .Usage (Vendor Usage 0x24)          6
            0xa1, 0x00,                    # .Collection (Physical)              8
            0x09, 0x02,                    # ..Usage (Vendor Usage 0x02)         10
            0xa1, 0x00,                    # ..Collection (Physical)             12
            0x55, 0x00,                    # ...Unit Exponent (0)                14
            0x65, 0x00,                    # ...Unit (None)                      16
            0x85, 0x01,                    # ...Report ID (1)                    18
            0x75, 0x01,                    # ...Report Size (1)                  20
            0x95, 0x05,                    # ...Report Count (5)                 22
            0x15, 0x00,                    # ...Logical Minimum (0)              24
            0x25, 0x01,                    # ...Logical Maximum (1)              26
            0x05, 0x85,                    # ...Usage Page (Battery System)      28
            0x09, 0xd0,                    # ...Usage (Vendor Usage 0xd0)        30
            0x09, 0x44,                    # ...Usage (Vendor Usage 0x44)        32
            0x09, 0x45,                    # ...Usage (Vendor Usage 0x45)        34
            0x09, 0x42,                    # ...Usage (Vendor Usage 0x42)        36
            0x0b, 0x61, 0x00, 0x84, 0x00,  # ...Usage (Vendor Usage 0x840061)    38
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       43
            0x75, 0x03,                    # ...Report Size (3)                  45
            0x95, 0x01,                    # ...Report Count (1)                 47
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        49
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           51
            0x75, 0x01,                    # ...Report Size (1)                  53
            0x95, 0x05,                    # ...Report Count (5)                 55
            0x05, 0x85,                    # ...Usage Page (Battery System)      57
            0x09, 0xd0,                    # ...Usage (Vendor Usage 0xd0)        59
            0x09, 0x44,                    # ...Usage (Vendor Usage 0x44)        61
            0x09, 0x45,                    # ...Usage (Vendor Usage 0x45)        63
            0x09, 0x42,                    # ...Usage (Vendor Usage 0x42)        65
            0x0b, 0x61, 0x00, 0x84, 0x00,  # ...Usage (Vendor Usage 0x840061)    67
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         72
            0x75, 0x03,                    # ...Report Size (3)                  74
            0x95, 0x01,                    # ...Report Count (1)                 76
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        78
            0x81, 0x03,                    # ...Input (Cnst,Var,Abs)             80
            0x85, 0x02,                    # ...Report ID (2)                    82
            0x75, 0x01,                    # ...Report Size (1)                  84
            0x95, 0x04,                    # ...Report Count (4)                 86
            0x05, 0x84,                    # ...Usage Page (Power Device)        88
            0x09, 0x69,                    # ...Usage (Vendor Usage 0x69)        90
            0x09, 0x65,                    # ...Usage (Vendor Usage 0x65)        92
            0x09, 0x62,                    # ...Usage (Vendor Usage 0x62)        94
            0x0b, 0x4b, 0x00, 0x85, 0x00,  # ...Usage (Vendor Usage 0x85004b)    96
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       101
            0x75, 0x04,                    # ...Report Size (4)                  103
            0x95, 0x01,                    # ...Report Count (1)                 105
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        107
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           109
            0x75, 0x01,                    # ...Report Size (1)                  111
            0x95, 0x04,                    # ...Report Count (4)                 113
            0x05, 0x84,                    # ...Usage Page (Power Device)        115
            0x09, 0x69,                    # ...Usage (Vendor Usage 0x69)        117
            0x09, 0x65,                    # ...Usage (Vendor Usage 0x65)        119
            0x09, 0x62,                    # ...Usage (Vendor Usage 0x62)        121
            0x0b, 0x4b, 0x00, 0x85, 0x00,  # ...Usage (Vendor Usage 0x85004b)    123
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         128
            0x95, 0x01,                    # ...Report Count (1)                 130
            0x75, 0x04,                    # ...Report Size (4)                  132
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        134
            0x81, 0x03,                    # ...Input (Cnst,Var,Abs)             136
            0x09, 0x73,                    # ...Usage (Vendor Usage 0x73)        138
            0x75, 0x08,                    # ...Report Size (8)                  140
            0x85, 0x0f,                    # ...Report ID (15)                   142
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       144
            0x09, 0x73,                    # ...Usage (Vendor Usage 0x73)        146
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         148
            0xc0,                          # ..End Collection                    150
            0x85, 0x06,                    # ..Report ID (6)                     151
            0x15, 0x00,                    # ..Logical Minimum (0)               153
            0x55, 0x00,                    # ..Unit Exponent (0)                 155
            0x65, 0x00,                    # ..Unit (None)                       157
            0x95, 0x01,                    # ..Report Count (1)                  159
            0x75, 0x08,                    # ..Report Size (8)                   161
            0x05, 0x85,                    # ..Usage Page (Battery System)       163
            0x25, 0x64,                    # ..Logical Maximum (100)             165
            0x09, 0x66,                    # ..Usage (Vendor Usage 0x66)         167
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        169
            0x75, 0x20,                    # ..Report Size (32)                  171
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           173
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       176
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         181
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        183
            0x65, 0x00,                    # ..Unit (None)                       185
            0x75, 0x08,                    # ..Report Size (8)                   187
            0x05, 0x85,                    # ..Usage Page (Battery System)       189
            0x25, 0x64,                    # ..Logical Maximum (100)             191
            0x09, 0x66,                    # ..Usage (Vendor Usage 0x66)         193
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          195
            0x75, 0x20,                    # ..Report Size (32)                  197
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           199
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       202
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         207
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          209
            0x06, 0xff, 0xff,              # ..Usage Page (Vendor Usage Page 0xffff) 211
            0x85, 0x22,                    # ..Report ID (34)                    214
            0x65, 0x00,                    # ..Unit (None)                       216
            0x25, 0x64,                    # ..Logical Maximum (100)             218
            0x75, 0x08,                    # ..Report Size (8)                   220
            0x09, 0x4d,                    # ..Usage (Vendor Usage 0x4d)         222
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        224
            0x05, 0x85,                    # ..Usage Page (Battery System)       226
            0x75, 0x20,                    # ..Report Size (32)                  228
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           230
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       233
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         238
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          240
            0x85, 0x07,                    # ..Report ID (7)                     242
            0x75, 0x08,                    # ..Report Size (8)                   244
            0x65, 0x00,                    # ..Unit (None)                       246
            0x05, 0x84,                    # ..Usage Page (Power Device)         248
            0x26, 0xff, 0x00,              # ..Logical Maximum (255)             250
            0x09, 0x35,                    # ..Usage (Vendor Usage 0x35)         253
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        255
            0x85, 0x08,                    # ..Report ID (8)                     257
            0x15, 0x00,                    # ..Logical Minimum (0)               259
            0x0b, 0x29, 0x00, 0x85, 0x00,  # ..Usage (Vendor Usage 0x850029)     261
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        266
            0x85, 0x09,                    # ..Report ID (9)                     268
            0x75, 0x20,                    # ..Report Size (32)                  270
            0x05, 0x84,                    # ..Usage Page (Power Device)         272
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           274
            0x15, 0xff,                    # ..Logical Minimum (-1)              277
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       279
            0x09, 0x57,                    # ..Usage (Vendor Usage 0x57)         284
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        286
            0x85, 0x0a,                    # ..Report ID (10)                    288
            0x55, 0x01,                    # ..Unit Exponent (1)                 290
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           292
            0x09, 0x56,                    # ..Usage (Vendor Usage 0x56)         295
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        297
            0x85, 0x0c,                    # ..Report ID (12)                    299
            0x75, 0x08,                    # ..Report Size (8)                   301
            0x15, 0x00,                    # ..Logical Minimum (0)               303
            0x26, 0xff, 0x00,              # ..Logical Maximum (255)             305
            0x65, 0x00,                    # ..Unit (None)                       308
            0x55, 0x00,                    # ..Unit Exponent (0)                 310
            0x05, 0x85,                    # ..Usage Page (Battery System)       312
            0x09, 0x2c,                    # ..Usage (Vendor Usage 0x2c)         314
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            316
            0x25, 0x64,                    # ..Logical Maximum (100)             318
            0x85, 0x0c,                    # ..Report ID (12)                    320
            0x09, 0x8d,                    # ..Usage (Vendor Usage 0x8d)         322
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            324
            0x09, 0x83,                    # ..Usage (Vendor Usage 0x83)         326
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            328
            0x09, 0x67,                    # ..Usage (Vendor Usage 0x67)         330
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            332
            0x26, 0xff, 0x00,              # ..Logical Maximum (255)             334
            0x85, 0x10,                    # ..Report ID (16)                    337
            0x0b, 0x89, 0x00, 0x85, 0x00,  # ..Usage (Vendor Usage 0x850089)     339
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            344
            0x05, 0x84,                    # ..Usage Page (Power Device)         346
            0x09, 0xfd,                    # ..Usage (Vendor Usage 0xfd)         348
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            350
            0x09, 0xfe,                    # ..Usage (Vendor Usage 0xfe)         352
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            354
            0x09, 0xff,                    # ..Usage (Vendor Usage 0xff)         356
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            358
            0x85, 0x0b,                    # ..Report ID (11)                    360
            0x09, 0x25,                    # ..Usage (Vendor Usage 0x25)         362
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            364
            0x09, 0x1f,                    # ..Usage (Vendor Usage 0x1f)         366
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            368
            0x85, 0x10,                    # ..Report ID (16)                    370
            0x06, 0xff, 0xff,              # ..Usage Page (Vendor Usage Page 0xffff) 372
            0x09, 0xf0,                    # ..Usage (Vendor Usage 0xf0)         375
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            377
            0x05, 0x84,                    # ..Usage Page (Power Device)         379
            0x85, 0x1f,                    # ..Report ID (31)                    381
            0x09, 0x5a,                    # ..Usage (Vendor Usage 0x5a)         383
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        385
            0x09, 0x5a,                    # ..Usage (Vendor Usage 0x5a)         387
            0x81, 0x82,                    # ..Input (Data,Var,Abs,Vol)          389
            0xc0,                          # .End Collection                     391
            0x09, 0x18,                    # .Usage (Vendor Usage 0x18)          392
            0xa1, 0x00,                    # .Collection (Physical)              394
            0x09, 0x19,                    # ..Usage (Vendor Usage 0x19)         396
            0x85, 0x0b,                    # ..Report ID (11)                    398
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            400
            0x09, 0x20,                    # ..Usage (Vendor Usage 0x20)         402
            0xa1, 0x81,                    # ..Collection (Vendor_defined)       404
            0x09, 0x21,                    # ...Usage (Vendor Usage 0x21)        406
            0x26, 0xff, 0x00,              # ...Logical Maximum (255)            408
            0x85, 0x0b,                    # ...Report ID (11)                   411
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           413
            0x09, 0x1f,                    # ...Usage (Vendor Usage 0x1f)        415
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           417
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        419
            0xa1, 0x00,                    # ...Collection (Physical)            421
            0x85, 0x0c,                    # ....Report ID (12)                  423
            0x09, 0x6c,                    # ....Usage (Vendor Usage 0x6c)       425
            0x25, 0x01,                    # ....Logical Maximum (1)             427
            0xb1, 0x03,                    # ....Feature (Cnst,Var,Abs)          429
            0xc0,                          # ...End Collection                   431
            0xc0,                          # ..End Collection                    432
            0x09, 0x20,                    # ..Usage (Vendor Usage 0x20)         433
            0xa1, 0x82,                    # ..Collection (Vendor_defined)       435
            0x26, 0xff, 0x00,              # ...Logical Maximum (255)            437
            0x85, 0x0b,                    # ...Report ID (11)                   440
            0x09, 0x21,                    # ...Usage (Vendor Usage 0x21)        442
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           444
            0x85, 0x0d,                    # ...Report ID (13)                   446
            0x09, 0x1f,                    # ...Usage (Vendor Usage 0x1f)        448
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           450
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        452
            0xa1, 0x00,                    # ...Collection (Physical)            454
            0x85, 0x0d,                    # ....Report ID (13)                  456
            0x09, 0x6c,                    # ....Usage (Vendor Usage 0x6c)       458
            0xb1, 0x03,                    # ....Feature (Cnst,Var,Abs)          460
            0xc0,                          # ...End Collection                   462
            0xc0,                          # ..End Collection                    463
            0xc0,                          # .End Collection                     464
            0x09, 0x1e,                    # .Usage (Vendor Usage 0x1e)          465
            0xa1, 0x84,                    # .Collection (Vendor_defined)        467
            0x85, 0x0b,                    # ..Report ID (11)                    469
            0x09, 0x1f,                    # ..Usage (Vendor Usage 0x1f)         471
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            473
            0x85, 0x0d,                    # ..Report ID (13)                    475
            0x09, 0x42,                    # ..Usage (Vendor Usage 0x42)         477
            0x66, 0x01, 0xf0,              # ..Unit (Seconds^-1,SILinear)        479
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        482
            0x09, 0x43,                    # ..Usage (Vendor Usage 0x43)         484
            0x66, 0x21, 0xd1,              # ..Unit (Seconds^-3,Gram,Centimeter^2,SILinear) 486
            0x75, 0x10,                    # ..Report Size (16)                  489
            0x55, 0x07,                    # ..Unit Exponent (7)                 491
            0x26, 0xff, 0x7f,              # ..Logical Maximum (32767)           493
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        496
            0x85, 0x12,                    # ..Report ID (18)                    498
            0x75, 0x08,                    # ..Report Size (8)                   500
            0x26, 0xff, 0x00,              # ..Logical Maximum (255)             502
            0x67, 0x21, 0xd1, 0xf0, 0x00,  # ..Unit (Ampere^-1,Seconds^-3,Gram,Centimeter^2,SILinear) 505
            0x09, 0x40,                    # ..Usage (Vendor Usage 0x40)         510
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        512
            0x55, 0x00,                    # ..Unit Exponent (0)                 514
            0x65, 0x00,                    # ..Unit (None)                       516
            0xc0,                          # .End Collection                     518
            0x09, 0x16,                    # .Usage (Vendor Usage 0x16)          519
            0xa1, 0x00,                    # .Collection (Physical)              521
            0x85, 0x0b,                    # ..Report ID (11)                    523
            0x09, 0x17,                    # ..Usage (Vendor Usage 0x17)         525
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            527
            0x09, 0x1c,                    # ..Usage (Vendor Usage 0x1c)         529
            0xa1, 0x00,                    # ..Collection (Physical)             531
            0x85, 0x0b,                    # ...Report ID (11)                   533
            0x09, 0x1d,                    # ...Usage (Vendor Usage 0x1d)        535
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           537
            0x85, 0x0e,                    # ...Report ID (14)                   539
            0x67, 0x21, 0xd1, 0xf0, 0x00,  # ...Unit (Ampere^-1,Seconds^-3,Gram,Centimeter^2,SILinear) 541
            0x55, 0x07,                    # ...Unit Exponent (7)                546
            0x09, 0x30,                    # ...Usage (Vendor Usage 0x30)        548
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       550
            0x85, 0x13,                    # ...Report ID (19)                   552
            0x09, 0x53,                    # ...Usage (Vendor Usage 0x53)        554
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       556
            0x26, 0xff, 0x7f,              # ...Logical Maximum (32767)          558
            0x75, 0x10,                    # ...Report Size (16)                 561
            0x09, 0x54,                    # ...Usage (Vendor Usage 0x54)        563
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       565
            0x75, 0x08,                    # ...Report Size (8)                  567
            0x26, 0xff, 0x00,              # ...Logical Maximum (255)            569
            0xc0,                          # ..End Collection                    572
            0xc0,                          # .End Collection                     573
            0x55, 0x00,                    # .Unit Exponent (0)                  574
            0x65, 0x00,                    # .Unit (None)                        576
            0x06, 0xff, 0xff,              # .Usage Page (Vendor Usage Page 0xffff) 578
            0x09, 0x18,                    # .Usage (Vendor Usage 0x18)          581
            0xa1, 0x00,                    # .Collection (Physical)              583
            0x85, 0x15,                    # ..Report ID (21)                    585
            0x09, 0x19,                    # ..Usage (Vendor Usage 0x19)         587
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            589
            0x09, 0x1a,                    # ..Usage (Vendor Usage 0x1a)         591
            0xa1, 0x81,                    # ..Collection (Vendor_defined)       593
            0x85, 0x16,                    # ...Report ID (22)                   595
            0x09, 0x90,                    # ...Usage (Vendor Usage 0x90)        597
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       599
            0x85, 0x15,                    # ...Report ID (21)                   601
            0x09, 0x1b,                    # ...Usage (Vendor Usage 0x1b)        603
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           605
            0x85, 0x18,                    # ...Report ID (24)                   607
            0x09, 0x94,                    # ...Usage (Vendor Usage 0x94)        609
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       611
            0x66, 0x01, 0x10,              # ...Unit (Seconds,SILinear)          613
            0x75, 0x18,                    # ...Report Size (24)                 616
            0x27, 0xff, 0xff, 0xff, 0x00,  # ...Logical Maximum (16777215)       618
            0x85, 0x17,                    # ...Report ID (23)                   623
            0x09, 0x92,                    # ...Usage (Vendor Usage 0x92)        625
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           627
            0x55, 0x04,                    # ...Unit Exponent (4)                629
            0x85, 0x1a,                    # ...Report ID (26)                   631
            0x09, 0x91,                    # ...Usage (Vendor Usage 0x91)        633
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       635
            0x55, 0x00,                    # ...Unit Exponent (0)                637
            0x65, 0x00,                    # ...Unit (None)                      639
            0x05, 0x84,                    # ...Usage Page (Power Device)        641
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        643
            0xa1, 0x00,                    # ...Collection (Physical)            645
            0x06, 0xff, 0xff,              # ....Usage Page (Vendor Usage Page 0xffff) 647
            0x75, 0x08,                    # ....Report Size (8)                 650
            0x25, 0x01,                    # ....Logical Maximum (1)             652
            0x85, 0x19,                    # ....Report ID (25)                  654
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       656
            0xb1, 0x83,                    # ....Feature (Cnst,Var,Abs,Vol)      658
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       660
            0x81, 0x83,                    # ....Input (Cnst,Var,Abs,Vol)        662
            0xc0,                          # ...End Collection                   664
            0xc0,                          # ..End Collection                    665
            0x09, 0x1a,                    # ..Usage (Vendor Usage 0x1a)         666
            0xa1, 0x82,                    # ..Collection (Vendor_defined)       668
            0x75, 0x08,                    # ...Report Size (8)                  670
            0x26, 0xff, 0x00,              # ...Logical Maximum (255)            672
            0x85, 0x1b,                    # ...Report ID (27)                   675
            0x09, 0x90,                    # ...Usage (Vendor Usage 0x90)        677
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       679
            0x85, 0x15,                    # ...Report ID (21)                   681
            0x09, 0x1b,                    # ...Usage (Vendor Usage 0x1b)        683
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           685
            0x85, 0x1d,                    # ...Report ID (29)                   687
            0x09, 0x94,                    # ...Usage (Vendor Usage 0x94)        689
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       691
            0x66, 0x01, 0x10,              # ...Unit (Seconds,SILinear)          693
            0x75, 0x18,                    # ...Report Size (24)                 696
            0x27, 0xff, 0xff, 0xff, 0x00,  # ...Logical Maximum (16777215)       698
            0x85, 0x1c,                    # ...Report ID (28)                   703
            0x09, 0x92,                    # ...Usage (Vendor Usage 0x92)        705
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           707
            0x55, 0x04,                    # ...Unit Exponent (4)                709
            0x85, 0x1e,                    # ...Report ID (30)                   711
            0x09, 0x91,                    # ...Usage (Vendor Usage 0x91)        713
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       715
            0x55, 0x00,                    # ...Unit Exponent (0)                717
            0x05, 0x84,                    # ...Usage Page (Power Device)        719
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        721
            0xa1, 0x00,                    # ...Collection (Physical)            723
            0x06, 0xff, 0xff,              # ....Usage Page (Vendor Usage Page 0xffff) 725
            0x75, 0x08,                    # ....Report Size (8)                 728
            0x25, 0x01,                    # ....Logical Maximum (1)             730
            0x85, 0x21,                    # ....Report ID (33)                  732
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       734
            0xb1, 0x83,                    # ....Feature (Cnst,Var,Abs,Vol)      736
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       738
            0x81, 0x83,                    # ....Input (Cnst,Var,Abs,Vol)        740
            0xc0,                          # ...End Collection                   742
            0xc0,                          # ..End Collection                    743
            0xc0,                          # .End Collection                     744
            0x05, 0x84,                    # .Usage Page (Power Device)          745
            0x09, 0x10,                    # .Usage (Vendor Usage 0x10)          747
            0xa1, 0x00,                    # .Collection (Physical)              749
            0x09, 0x12,                    # ..Usage (Vendor Usage 0x12)         751
            0xa1, 0x00,                    # ..Collection (Physical)             753
            0x85, 0x20,                    # ...Report ID (32)                   755
            0x75, 0x08,                    # ...Report Size (8)                  757
            0x26, 0xff, 0x00,              # ...Logical Maximum (255)            759
            0x09, 0x5a,                    # ...Usage (Vendor Usage 0x5a)        762
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       764
            0xc0,                          # ..End Collection                    766
            0xc0,                          # .End Collection                     767
            0xc0,                          # End Collection                      768
        ]
        # fmt: on

        # we only check for the parsing to not crash
        hidtools.hid.ReportDescriptor.from_bytes(report_descriptor)

    def test_human_decode(self):
        # Same report descriptor as above, but a bunch of
        # 0x26, 0xff, 0x00,              # ..Logical Maximum (255)
        # are replaced with the single byte form
        # 0x25, 0xff                     # ..Logical Maximum (255)
        # Because we're parsing a human description and 0xff only needs one
        # byte, the re-generated output would shorten each of these items
        # (since we can't reliably guess that 2 bytes are used here).
        # So the rdesc is manually modified to match the output we'll
        # generated.
        # fmt: off
        report_descriptor = [
            0x05, 0x84,                    # Usage Page (Power Device)           0
            0x09, 0x04,                    # Usage (Vendor Usage 0x04)           2
            0xa1, 0x01,                    # Collection (Application)            4
            0x09, 0x24,                    # .Usage (Vendor Usage 0x24)          6
            0xa1, 0x00,                    # .Collection (Physical)              8
            0x09, 0x02,                    # ..Usage (Vendor Usage 0x02)         10
            0xa1, 0x00,                    # ..Collection (Physical)             12
            0x55, 0x00,                    # ...Unit Exponent (0)                14
            0x65, 0x00,                    # ...Unit (None)                      16
            0x85, 0x01,                    # ...Report ID (1)                    18
            0x75, 0x01,                    # ...Report Size (1)                  20
            0x95, 0x05,                    # ...Report Count (5)                 22
            0x15, 0x00,                    # ...Logical Minimum (0)              24
            0x25, 0x01,                    # ...Logical Maximum (1)              26
            0x05, 0x85,                    # ...Usage Page (Battery System)      28
            0x09, 0xd0,                    # ...Usage (Vendor Usage 0xd0)        30
            0x09, 0x44,                    # ...Usage (Vendor Usage 0x44)        32
            0x09, 0x45,                    # ...Usage (Vendor Usage 0x45)        34
            0x09, 0x42,                    # ...Usage (Vendor Usage 0x42)        36
            0x0b, 0x61, 0x00, 0x84, 0x00,  # ...Usage (Vendor Usage 0x840061)    38
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       43
            0x75, 0x03,                    # ...Report Size (3)                  45
            0x95, 0x01,                    # ...Report Count (1)                 47
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        49
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           51
            0x75, 0x01,                    # ...Report Size (1)                  53
            0x95, 0x05,                    # ...Report Count (5)                 55
            0x05, 0x85,                    # ...Usage Page (Battery System)      57
            0x09, 0xd0,                    # ...Usage (Vendor Usage 0xd0)        59
            0x09, 0x44,                    # ...Usage (Vendor Usage 0x44)        61
            0x09, 0x45,                    # ...Usage (Vendor Usage 0x45)        63
            0x09, 0x42,                    # ...Usage (Vendor Usage 0x42)        65
            0x0b, 0x61, 0x00, 0x84, 0x00,  # ...Usage (Vendor Usage 0x840061)    67
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         72
            0x75, 0x03,                    # ...Report Size (3)                  74
            0x95, 0x01,                    # ...Report Count (1)                 76
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        78
            0x81, 0x03,                    # ...Input (Cnst,Var,Abs)             80
            0x85, 0x02,                    # ...Report ID (2)                    82
            0x75, 0x01,                    # ...Report Size (1)                  84
            0x95, 0x04,                    # ...Report Count (4)                 86
            0x05, 0x84,                    # ...Usage Page (Power Device)        88
            0x09, 0x69,                    # ...Usage (Vendor Usage 0x69)        90
            0x09, 0x65,                    # ...Usage (Vendor Usage 0x65)        92
            0x09, 0x62,                    # ...Usage (Vendor Usage 0x62)        94
            0x0b, 0x4b, 0x00, 0x85, 0x00,  # ...Usage (Vendor Usage 0x85004b)    96
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       101
            0x75, 0x04,                    # ...Report Size (4)                  103
            0x95, 0x01,                    # ...Report Count (1)                 105
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        107
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           109
            0x75, 0x01,                    # ...Report Size (1)                  111
            0x95, 0x04,                    # ...Report Count (4)                 113
            0x05, 0x84,                    # ...Usage Page (Power Device)        115
            0x09, 0x69,                    # ...Usage (Vendor Usage 0x69)        117
            0x09, 0x65,                    # ...Usage (Vendor Usage 0x65)        119
            0x09, 0x62,                    # ...Usage (Vendor Usage 0x62)        121
            0x0b, 0x4b, 0x00, 0x85, 0x00,  # ...Usage (Vendor Usage 0x85004b)    123
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         128
            0x95, 0x01,                    # ...Report Count (1)                 130
            0x75, 0x04,                    # ...Report Size (4)                  132
            0x09, 0x00,                    # ...Usage (Vendor Usage 0x00)        134
            0x81, 0x03,                    # ...Input (Cnst,Var,Abs)             136
            0x09, 0x73,                    # ...Usage (Vendor Usage 0x73)        138
            0x75, 0x08,                    # ...Report Size (8)                  140
            0x85, 0x0f,                    # ...Report ID (15)                   142
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       144
            0x09, 0x73,                    # ...Usage (Vendor Usage 0x73)        146
            0x81, 0x83,                    # ...Input (Cnst,Var,Abs,Vol)         148
            0xc0,                          # ..End Collection                    150
            0x85, 0x06,                    # ..Report ID (6)                     151
            0x15, 0x00,                    # ..Logical Minimum (0)               153
            0x55, 0x00,                    # ..Unit Exponent (0)                 155
            0x65, 0x00,                    # ..Unit (None)                       157
            0x95, 0x01,                    # ..Report Count (1)                  159
            0x75, 0x08,                    # ..Report Size (8)                   161
            0x05, 0x85,                    # ..Usage Page (Battery System)       163
            0x25, 0x64,                    # ..Logical Maximum (100)             165
            0x09, 0x66,                    # ..Usage (Vendor Usage 0x66)         167
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        169
            0x75, 0x20,                    # ..Report Size (32)                  171
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           173
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       176
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         181
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        183
            0x65, 0x00,                    # ..Unit (None)                       185
            0x75, 0x08,                    # ..Report Size (8)                   187
            0x05, 0x85,                    # ..Usage Page (Battery System)       189
            0x25, 0x64,                    # ..Logical Maximum (100)             191
            0x09, 0x66,                    # ..Usage (Vendor Usage 0x66)         193
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          195
            0x75, 0x20,                    # ..Report Size (32)                  197
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           199
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       202
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         207
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          209
            0x06, 0xff, 0xff,              # ..Usage Page (Vendor Usage Page 0xffff) 211
            0x85, 0x22,                    # ..Report ID (34)                    214
            0x65, 0x00,                    # ..Unit (None)                       216
            0x25, 0x64,                    # ..Logical Maximum (100)             218
            0x75, 0x08,                    # ..Report Size (8)                   220
            0x09, 0x4d,                    # ..Usage (Vendor Usage 0x4d)         222
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        224
            0x05, 0x85,                    # ..Usage Page (Battery System)       226
            0x75, 0x20,                    # ..Report Size (32)                  228
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           230
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       233
            0x09, 0x68,                    # ..Usage (Vendor Usage 0x68)         238
            0x81, 0x83,                    # ..Input (Cnst,Var,Abs,Vol)          240
            0x85, 0x07,                    # ..Report ID (7)                     242
            0x75, 0x08,                    # ..Report Size (8)                   244
            0x65, 0x00,                    # ..Unit (None)                       246
            0x05, 0x84,                    # ..Usage Page (Power Device)         248
            0x25, 0xff,                    # ..Logical Maximum (255)             250
            0x09, 0x35,                    # ..Usage (Vendor Usage 0x35)         253
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        255
            0x85, 0x08,                    # ..Report ID (8)                     257
            0x15, 0x00,                    # ..Logical Minimum (0)               259
            0x0b, 0x29, 0x00, 0x85, 0x00,  # ..Usage (Vendor Usage 0x850029)     261
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        266
            0x85, 0x09,                    # ..Report ID (9)                     268
            0x75, 0x20,                    # ..Report Size (32)                  270
            0x05, 0x84,                    # ..Usage Page (Power Device)         272
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           274
            0x15, 0xff,                    # ..Logical Minimum (-1)              277
            0x27, 0x00, 0x65, 0xcd, 0x1d,  # ..Logical Maximum (500000000)       279
            0x09, 0x57,                    # ..Usage (Vendor Usage 0x57)         284
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        286
            0x85, 0x0a,                    # ..Report ID (10)                    288
            0x55, 0x01,                    # ..Unit Exponent (1)                 290
            0x66, 0x01, 0x10,              # ..Unit (Seconds,SILinear)           292
            0x09, 0x56,                    # ..Usage (Vendor Usage 0x56)         295
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        297
            0x85, 0x0c,                    # ..Report ID (12)                    299
            0x75, 0x08,                    # ..Report Size (8)                   301
            0x15, 0x00,                    # ..Logical Minimum (0)               303
            0x25, 0xff,                    # ..Logical Maximum (255)             305
            0x65, 0x00,                    # ..Unit (None)                       308
            0x55, 0x00,                    # ..Unit Exponent (0)                 310
            0x05, 0x85,                    # ..Usage Page (Battery System)       312
            0x09, 0x2c,                    # ..Usage (Vendor Usage 0x2c)         314
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            316
            0x25, 0x64,                    # ..Logical Maximum (100)             318
            0x85, 0x0c,                    # ..Report ID (12)                    320
            0x09, 0x8d,                    # ..Usage (Vendor Usage 0x8d)         322
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            324
            0x09, 0x83,                    # ..Usage (Vendor Usage 0x83)         326
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            328
            0x09, 0x67,                    # ..Usage (Vendor Usage 0x67)         330
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            332
            0x25, 0xff,                    # ..Logical Maximum (255)             334
            0x85, 0x10,                    # ..Report ID (16)                    337
            0x0b, 0x89, 0x00, 0x85, 0x00,  # ..Usage (Vendor Usage 0x850089)     339
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            344
            0x05, 0x84,                    # ..Usage Page (Power Device)         346
            0x09, 0xfd,                    # ..Usage (Vendor Usage 0xfd)         348
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            350
            0x09, 0xfe,                    # ..Usage (Vendor Usage 0xfe)         352
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            354
            0x09, 0xff,                    # ..Usage (Vendor Usage 0xff)         356
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            358
            0x85, 0x0b,                    # ..Report ID (11)                    360
            0x09, 0x25,                    # ..Usage (Vendor Usage 0x25)         362
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            364
            0x09, 0x1f,                    # ..Usage (Vendor Usage 0x1f)         366
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            368
            0x85, 0x10,                    # ..Report ID (16)                    370
            0x06, 0xff, 0xff,              # ..Usage Page (Vendor Usage Page 0xffff) 372
            0x09, 0xf0,                    # ..Usage (Vendor Usage 0xf0)         375
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            377
            0x05, 0x84,                    # ..Usage Page (Power Device)         379
            0x85, 0x1f,                    # ..Report ID (31)                    381
            0x09, 0x5a,                    # ..Usage (Vendor Usage 0x5a)         383
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        385
            0x09, 0x5a,                    # ..Usage (Vendor Usage 0x5a)         387
            0x81, 0x82,                    # ..Input (Data,Var,Abs,Vol)          389
            0xc0,                          # .End Collection                     391
            0x09, 0x18,                    # .Usage (Vendor Usage 0x18)          392
            0xa1, 0x00,                    # .Collection (Physical)              394
            0x09, 0x19,                    # ..Usage (Vendor Usage 0x19)         396
            0x85, 0x0b,                    # ..Report ID (11)                    398
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            400
            0x09, 0x20,                    # ..Usage (Vendor Usage 0x20)         402
            0xa1, 0x81,                    # ..Collection (Vendor_defined)       404
            0x09, 0x21,                    # ...Usage (Vendor Usage 0x21)        406
            0x25, 0xff,                    # ...Logical Maximum (255)            408
            0x85, 0x0b,                    # ...Report ID (11)                   411
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           413
            0x09, 0x1f,                    # ...Usage (Vendor Usage 0x1f)        415
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           417
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        419
            0xa1, 0x00,                    # ...Collection (Physical)            421
            0x85, 0x0c,                    # ....Report ID (12)                  423
            0x09, 0x6c,                    # ....Usage (Vendor Usage 0x6c)       425
            0x25, 0x01,                    # ....Logical Maximum (1)             427
            0xb1, 0x03,                    # ....Feature (Cnst,Var,Abs)          429
            0xc0,                          # ...End Collection                   431
            0xc0,                          # ..End Collection                    432
            0x09, 0x20,                    # ..Usage (Vendor Usage 0x20)         433
            0xa1, 0x82,                    # ..Collection (Vendor_defined)       435
            0x25, 0xff,                    # ...Logical Maximum (255)            437
            0x85, 0x0b,                    # ...Report ID (11)                   440
            0x09, 0x21,                    # ...Usage (Vendor Usage 0x21)        442
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           444
            0x85, 0x0d,                    # ...Report ID (13)                   446
            0x09, 0x1f,                    # ...Usage (Vendor Usage 0x1f)        448
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           450
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        452
            0xa1, 0x00,                    # ...Collection (Physical)            454
            0x85, 0x0d,                    # ....Report ID (13)                  456
            0x09, 0x6c,                    # ....Usage (Vendor Usage 0x6c)       458
            0xb1, 0x03,                    # ....Feature (Cnst,Var,Abs)          460
            0xc0,                          # ...End Collection                   462
            0xc0,                          # ..End Collection                    463
            0xc0,                          # .End Collection                     464
            0x09, 0x1e,                    # .Usage (Vendor Usage 0x1e)          465
            0xa1, 0x84,                    # .Collection (Vendor_defined)        467
            0x85, 0x0b,                    # ..Report ID (11)                    469
            0x09, 0x1f,                    # ..Usage (Vendor Usage 0x1f)         471
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            473
            0x85, 0x0d,                    # ..Report ID (13)                    475
            0x09, 0x42,                    # ..Usage (Vendor Usage 0x42)         477
            0x66, 0x01, 0xf0,              # ..Unit (Seconds^-1,SILinear)        479
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        482
            0x09, 0x43,                    # ..Usage (Vendor Usage 0x43)         484
            0x66, 0x21, 0xd1,              # ..Unit (Seconds^-3,Gram,Centimeter^2,SILinear) 486
            0x75, 0x10,                    # ..Report Size (16)                  489
            0x55, 0x07,                    # ..Unit Exponent (7)                 491
            0x26, 0xff, 0x7f,              # ..Logical Maximum (32767)           493
            0xb1, 0x83,                    # ..Feature (Cnst,Var,Abs,Vol)        496
            0x85, 0x12,                    # ..Report ID (18)                    498
            0x75, 0x08,                    # ..Report Size (8)                   500
            0x25, 0xff,                    # ..Logical Maximum (255)             502
            0x67, 0x21, 0xd1, 0xf0, 0x00,  # ..Unit (Ampere^-1,Seconds^-3,Gram,Centimeter^2,SILinear) 505
            0x09, 0x40,                    # ..Usage (Vendor Usage 0x40)         510
            0xb1, 0x82,                    # ..Feature (Data,Var,Abs,Vol)        512
            0x55, 0x00,                    # ..Unit Exponent (0)                 514
            0x65, 0x00,                    # ..Unit (None)                       516
            0xc0,                          # .End Collection                     518
            0x09, 0x16,                    # .Usage (Vendor Usage 0x16)          519
            0xa1, 0x00,                    # .Collection (Physical)              521
            0x85, 0x0b,                    # ..Report ID (11)                    523
            0x09, 0x17,                    # ..Usage (Vendor Usage 0x17)         525
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            527
            0x09, 0x1c,                    # ..Usage (Vendor Usage 0x1c)         529
            0xa1, 0x00,                    # ..Collection (Physical)             531
            0x85, 0x0b,                    # ...Report ID (11)                   533
            0x09, 0x1d,                    # ...Usage (Vendor Usage 0x1d)        535
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           537
            0x85, 0x0e,                    # ...Report ID (14)                   539
            0x67, 0x21, 0xd1, 0xf0, 0x00,  # ...Unit (Ampere^-1,Seconds^-3,Gram,Centimeter^2,SILinear) 541
            0x55, 0x07,                    # ...Unit Exponent (7)                546
            0x09, 0x30,                    # ...Usage (Vendor Usage 0x30)        548
            0xb1, 0x83,                    # ...Feature (Cnst,Var,Abs,Vol)       550
            0x85, 0x13,                    # ...Report ID (19)                   552
            0x09, 0x53,                    # ...Usage (Vendor Usage 0x53)        554
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       556
            0x26, 0xff, 0x7f,              # ...Logical Maximum (32767)          558
            0x75, 0x10,                    # ...Report Size (16)                 561
            0x09, 0x54,                    # ...Usage (Vendor Usage 0x54)        563
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       565
            0x75, 0x08,                    # ...Report Size (8)                  567
            0x25, 0xff,                    # ...Logical Maximum (255)            569
            0xc0,                          # ..End Collection                    572
            0xc0,                          # .End Collection                     573
            0x55, 0x00,                    # .Unit Exponent (0)                  574
            0x65, 0x00,                    # .Unit (None)                        576
            0x06, 0xff, 0xff,              # .Usage Page (Vendor Usage Page 0xffff) 578
            0x09, 0x18,                    # .Usage (Vendor Usage 0x18)          581
            0xa1, 0x00,                    # .Collection (Physical)              583
            0x85, 0x15,                    # ..Report ID (21)                    585
            0x09, 0x19,                    # ..Usage (Vendor Usage 0x19)         587
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            589
            0x09, 0x1a,                    # ..Usage (Vendor Usage 0x1a)         591
            0xa1, 0x81,                    # ..Collection (Vendor_defined)       593
            0x85, 0x16,                    # ...Report ID (22)                   595
            0x09, 0x90,                    # ...Usage (Vendor Usage 0x90)        597
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       599
            0x85, 0x15,                    # ...Report ID (21)                   601
            0x09, 0x1b,                    # ...Usage (Vendor Usage 0x1b)        603
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           605
            0x85, 0x18,                    # ...Report ID (24)                   607
            0x09, 0x94,                    # ...Usage (Vendor Usage 0x94)        609
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       611
            0x66, 0x01, 0x10,              # ...Unit (Seconds,SILinear)          613
            0x75, 0x18,                    # ...Report Size (24)                 616
            0x27, 0xff, 0xff, 0xff, 0x00,  # ...Logical Maximum (16777215)       618
            0x85, 0x17,                    # ...Report ID (23)                   623
            0x09, 0x92,                    # ...Usage (Vendor Usage 0x92)        625
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           627
            0x55, 0x04,                    # ...Unit Exponent (4)                629
            0x85, 0x1a,                    # ...Report ID (26)                   631
            0x09, 0x91,                    # ...Usage (Vendor Usage 0x91)        633
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       635
            0x55, 0x00,                    # ...Unit Exponent (0)                637
            0x65, 0x00,                    # ...Unit (None)                      639
            0x05, 0x84,                    # ...Usage Page (Power Device)        641
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        643
            0xa1, 0x00,                    # ...Collection (Physical)            645
            0x06, 0xff, 0xff,              # ....Usage Page (Vendor Usage Page 0xffff) 647
            0x75, 0x08,                    # ....Report Size (8)                 650
            0x25, 0x01,                    # ....Logical Maximum (1)             652
            0x85, 0x19,                    # ....Report ID (25)                  654
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       656
            0xb1, 0x83,                    # ....Feature (Cnst,Var,Abs,Vol)      658
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       660
            0x81, 0x83,                    # ....Input (Cnst,Var,Abs,Vol)        662
            0xc0,                          # ...End Collection                   664
            0xc0,                          # ..End Collection                    665
            0x09, 0x1a,                    # ..Usage (Vendor Usage 0x1a)         666
            0xa1, 0x82,                    # ..Collection (Vendor_defined)       668
            0x75, 0x08,                    # ...Report Size (8)                  670
            0x25, 0xff,                    # ...Logical Maximum (255)            672
            0x85, 0x1b,                    # ...Report ID (27)                   675
            0x09, 0x90,                    # ...Usage (Vendor Usage 0x90)        677
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       679
            0x85, 0x15,                    # ...Report ID (21)                   681
            0x09, 0x1b,                    # ...Usage (Vendor Usage 0x1b)        683
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           685
            0x85, 0x1d,                    # ...Report ID (29)                   687
            0x09, 0x94,                    # ...Usage (Vendor Usage 0x94)        689
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       691
            0x66, 0x01, 0x10,              # ...Unit (Seconds,SILinear)          693
            0x75, 0x18,                    # ...Report Size (24)                 696
            0x27, 0xff, 0xff, 0xff, 0x00,  # ...Logical Maximum (16777215)       698
            0x85, 0x1c,                    # ...Report ID (28)                   703
            0x09, 0x92,                    # ...Usage (Vendor Usage 0x92)        705
            0xb1, 0x03,                    # ...Feature (Cnst,Var,Abs)           707
            0x55, 0x04,                    # ...Unit Exponent (4)                709
            0x85, 0x1e,                    # ...Report ID (30)                   711
            0x09, 0x91,                    # ...Usage (Vendor Usage 0x91)        713
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       715
            0x55, 0x00,                    # ...Unit Exponent (0)                717
            0x05, 0x84,                    # ...Usage Page (Power Device)        719
            0x09, 0x02,                    # ...Usage (Vendor Usage 0x02)        721
            0xa1, 0x00,                    # ...Collection (Physical)            723
            0x06, 0xff, 0xff,              # ....Usage Page (Vendor Usage Page 0xffff) 725
            0x75, 0x08,                    # ....Report Size (8)                 728
            0x25, 0x01,                    # ....Logical Maximum (1)             730
            0x85, 0x21,                    # ....Report ID (33)                  732
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       734
            0xb1, 0x83,                    # ....Feature (Cnst,Var,Abs,Vol)      736
            0x09, 0x93,                    # ....Usage (Vendor Usage 0x93)       738
            0x81, 0x83,                    # ....Input (Cnst,Var,Abs,Vol)        740
            0xc0,                          # ...End Collection                   742
            0xc0,                          # ..End Collection                    743
            0xc0,                          # .End Collection                     744
            0x05, 0x84,                    # .Usage Page (Power Device)          745
            0x09, 0x10,                    # .Usage (Vendor Usage 0x10)          747
            0xa1, 0x00,                    # .Collection (Physical)              749
            0x09, 0x12,                    # ..Usage (Vendor Usage 0x12)         751
            0xa1, 0x00,                    # ..Collection (Physical)             753
            0x85, 0x20,                    # ...Report ID (32)                   755
            0x75, 0x08,                    # ...Report Size (8)                  757
            0x25, 0xff,                    # ...Logical Maximum (255)            759
            0x09, 0x5a,                    # ...Usage (Vendor Usage 0x5a)        762
            0xb1, 0x82,                    # ...Feature (Data,Var,Abs,Vol)       764
            0xc0,                          # ..End Collection                    766
            0xc0,                          # .End Collection                     767
            0xc0,                          # End Collection                      768
        ]
        # fmt: on
        import io

        initial_rdesc = hidtools.hid.ReportDescriptor.from_bytes(report_descriptor)
        string = io.StringIO()
        initial_rdesc.dump(dump_file=string, output_type="human")
        parsed_rdesc = hidtools.hid.ReportDescriptor.from_human_descr(string.getvalue())

        assert initial_rdesc.bytes == parsed_rdesc.bytes

    def test_report_type(self):
        # MS Comfort Sculpt keyboard, has a input, output and feature report
        # fmt: off
        report_descriptor = [
            0x05, 0x01,                    # Usage Page (Generic Desktop)        0
            0x09, 0x06,                    # Usage (Keyboard)                    2
            0xa1, 0x01,                    # Collection (Application)            4
            0x05, 0x08,                    # .Usage Page (LEDs)                  6
            0x19, 0x01,                    # .Usage Minimum (1)                  8
            0x29, 0x03,                    # .Usage Maximum (3)                  10
            0x15, 0x00,                    # .Logical Minimum (0)                12
            0x25, 0x01,                    # .Logical Maximum (1)                14
            0x75, 0x01,                    # .Report Size (1)                    16
            0x95, 0x03,                    # .Report Count (3)                   18
            0x91, 0x02,                    # .Output (Data,Var,Abs)              20
            0x95, 0x05,                    # .Report Count (5)                   22
            0x91, 0x01,                    # .Output (Cnst,Arr,Abs)              24
            0x05, 0x07,                    # .Usage Page (Keyboard)              26
            0x1a, 0xe0, 0x00,              # .Usage Minimum (224)                28
            0x2a, 0xe7, 0x00,              # .Usage Maximum (231)                31
            0x95, 0x08,                    # .Report Count (8)                   34
            0x81, 0x02,                    # .Input (Data,Var,Abs)               36
            0x75, 0x08,                    # .Report Size (8)                    38
            0x95, 0x01,                    # .Report Count (1)                   40
            0x81, 0x01,                    # .Input (Cnst,Arr,Abs)               42
            0x19, 0x00,                    # .Usage Minimum (0)                  44
            0x2a, 0x91, 0x00,              # .Usage Maximum (145)                46
            0x26, 0xff, 0x00,              # .Logical Maximum (255)              49
            0x95, 0x06,                    # .Report Count (6)                   52
            0x81, 0x00,                    # .Input (Data,Arr,Abs)               54
            0x05, 0x0c,                    # .Usage Page (Consumer Devices)      56
            0x0a, 0xc0, 0x02,              # .Usage (Extended Keyboard Attributes Collection) 58
            0xa1, 0x02,                    # .Collection (Logical)               61
            0x1a, 0xc1, 0x02,              # ..Usage Minimum (705)               63
            0x2a, 0xc6, 0x02,              # ..Usage Maximum (710)               66
            0x95, 0x06,                    # ..Report Count (6)                  69
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            71
            0xc0,                          # .End Collection                     73
            0xc0,                          # End Collection                      74
        ]
        # fmt: on
        rdesc = hidtools.hid.ReportDescriptor.from_bytes(report_descriptor)
        for r in rdesc.input_reports.values():
            assert r.type == hidtools.hid.HidReport.Type.INPUT

        for r in rdesc.output_reports.values():
            assert r.type == hidtools.hid.HidReport.Type.OUTPUT

        for r in rdesc.feature_reports.values():
            assert r.type == hidtools.hid.HidReport.Type.FEATURE

    def test_const_feature_report(self):
        # MS Comfort Sculpt keyboard, has a const Feature report (byte 69)
        # fmt: off
        report_descriptor = [
            0x05, 0x01,                    # Usage Page (Generic Desktop)        0
            0x09, 0x06,                    # Usage (Keyboard)                    2
            0xa1, 0x01,                    # Collection (Application)            4
            0x05, 0x08,                    # .Usage Page (LEDs)                  6
            0x19, 0x01,                    # .Usage Minimum (1)                  8
            0x29, 0x03,                    # .Usage Maximum (3)                  10
            0x15, 0x00,                    # .Logical Minimum (0)                12
            0x25, 0x01,                    # .Logical Maximum (1)                14
            0x75, 0x01,                    # .Report Size (1)                    16
            0x95, 0x03,                    # .Report Count (3)                   18
            0x91, 0x02,                    # .Output (Data,Var,Abs)              20
            0x95, 0x05,                    # .Report Count (5)                   22
            0x91, 0x01,                    # .Output (Cnst,Arr,Abs)              24
            0x05, 0x07,                    # .Usage Page (Keyboard)              26
            0x1a, 0xe0, 0x00,              # .Usage Minimum (224)                28
            0x2a, 0xe7, 0x00,              # .Usage Maximum (231)                31
            0x95, 0x08,                    # .Report Count (8)                   34
            0x81, 0x02,                    # .Input (Data,Var,Abs)               36
            0x75, 0x08,                    # .Report Size (8)                    38
            0x95, 0x01,                    # .Report Count (1)                   40
            0x81, 0x01,                    # .Input (Cnst,Arr,Abs)               42
            0x19, 0x00,                    # .Usage Minimum (0)                  44
            0x2a, 0x91, 0x00,              # .Usage Maximum (145)                46
            0x26, 0xff, 0x00,              # .Logical Maximum (255)              49
            0x95, 0x06,                    # .Report Count (6)                   52
            0x81, 0x00,                    # .Input (Data,Arr,Abs)               54
            0x05, 0x0c,                    # .Usage Page (Consumer Devices)      56
            0x0a, 0xc0, 0x02,              # .Usage (Extended Keyboard Attributes Collection) 58
            0xa1, 0x02,                    # .Collection (Logical)               61
            0x1a, 0xc1, 0x02,              # ..Usage Minimum (705)               63
            0x2a, 0xc6, 0x02,              # ..Usage Maximum (710)               66
            0x95, 0x06,                    # ..Report Count (6)                  69
            0xb1, 0x03,                    # ..Feature (Cnst,Var,Abs)            71
            0xc0,                          # .End Collection                     73
            0xc0,                          # End Collection                      74
        ]
        # fmt: on
        rdesc = hidtools.hid.ReportDescriptor.from_bytes(report_descriptor)
        # pretty convoluted to get the first value out of a dict...
        report = next(iter(rdesc.feature_reports.values()))
        # Make sure that our expected usages are present as separate fields
        # in the report, and that they're represented in the string format
        feature_usages = (f.usage for f in report.fields)
        printout = report.format_report([0] * report.size)
        for usage in range(0xC02C1, 0xC02C6 + 1):  # see bytes 63/66
            assert usage in feature_usages, f"Usage {usage:#x} missing in report"
            string = hidtools.hut.HUT[0xC][usage].name
            assert string in printout


class TestHidUnit:
    def test_unit_none(self):
        for x in range(1, 5):
            assert HidUnit.from_bytes(bytes(x)) is None
        assert HidUnit.from_value(0) is None

    @pytest.mark.parametrize("exp", range(0x1, 0x10))
    def test_exponent(self, exp):
        value = 0x1 | (exp << 4)
        unit = HidUnit.from_value(value)
        expected_exponent = exp if exp < 0x8 else (exp - 16)
        assert unit.units == {Unit.CENTIMETER: expected_exponent}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_length(self, system):
        value = system.value | 0x70  # exp of 7
        unit = HidUnit.from_value(value)
        expected_unit = {
            HidUnit.System.NONE: None,
            HidUnit.System.SI_LINEAR: Unit.CENTIMETER,
            HidUnit.System.SI_ROTATION: Unit.RADIANS,
            HidUnit.System.ENGLISH_LINEAR: Unit.INCH,
            HidUnit.System.ENGLISH_ROTATION: Unit.DEGREES,
        }[system]
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {expected_unit: 7}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_mass(self, system):
        value = system.value | 0x700  # exp of 7
        unit = HidUnit.from_value(value)
        expected_unit = {
            HidUnit.System.NONE: None,
            HidUnit.System.SI_LINEAR: Unit.GRAM,
            HidUnit.System.SI_ROTATION: Unit.GRAM,
            HidUnit.System.ENGLISH_LINEAR: Unit.SLUG,
            HidUnit.System.ENGLISH_ROTATION: Unit.SLUG,
        }[system]
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {expected_unit: 7}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_time(self, system):
        value = system.value | 0x7000  # exp of 7
        unit = HidUnit.from_value(value)
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {Unit.SECONDS: 7}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_temperature(self, system):
        value = system.value | 0x70000  # exp of 7
        unit = HidUnit.from_value(value)
        expected_unit = {
            HidUnit.System.NONE: None,
            HidUnit.System.SI_LINEAR: Unit.KELVIN,
            HidUnit.System.SI_ROTATION: Unit.KELVIN,
            HidUnit.System.ENGLISH_LINEAR: Unit.FAHRENHEIT,
            HidUnit.System.ENGLISH_ROTATION: Unit.FAHRENHEIT,
        }[system]
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {expected_unit: 7}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_current(self, system):
        value = system.value | 0x700000  # exp of 7
        unit = HidUnit.from_value(value)
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {Unit.AMPERE: 7}

    @pytest.mark.parametrize("system", HidUnit.System)
    def test_unit_lum_intensity(self, system):
        value = system.value | 0x7000000  # exp of 7
        unit = HidUnit.from_value(value)
        if system == HidUnit.System.NONE:
            assert unit is None
        else:
            assert unit.units == {Unit.CANDELA: 7}

    # Examples from HID Spec (page 39)
    def test_hid_examples(self):
        # Velocity (cm/s)
        unit = HidUnit.from_value(0xF011)
        assert unit.units == {
            Unit.CENTIMETER: 1,
            Unit.SECONDS: -1,
        }
        # Momentum
        unit = HidUnit.from_value(0xF111)
        assert unit.units == {
            Unit.CENTIMETER: 1,
            Unit.GRAM: 1,
            Unit.SECONDS: -1,
        }
        # Acceleration
        unit = HidUnit.from_value(0xE011)
        assert unit.units == {
            Unit.CENTIMETER: 1,
            Unit.SECONDS: -2,
        }
        # Force
        unit = HidUnit.from_value(0xE111)
        assert unit.units == {
            Unit.CENTIMETER: 1,
            Unit.GRAM: 1,
            Unit.SECONDS: -2,
        }
        # Energy
        unit = HidUnit.from_value(0xE121)
        assert unit.units == {
            Unit.CENTIMETER: 2,
            Unit.GRAM: 1,
            Unit.SECONDS: -2,
        }
        # Angular Acceleration
        unit = HidUnit.from_value(0xE012)
        assert unit.units == {
            Unit.RADIANS: 1,
            Unit.SECONDS: -2,
        }
        # Voltage
        unit = HidUnit.from_value(0x00F0D121)
        assert unit.units == {
            Unit.CENTIMETER: 2,
            Unit.GRAM: 1,
            Unit.SECONDS: -3,
            Unit.AMPERE: -1,
        }

    # The example values from above
    @pytest.mark.parametrize(
        "value", [0xF111, 0xE011, 0xE111, 0xE121, 0xE012, 0x00F0D121]
    )
    def test_value(self, value):
        assert HidUnit.from_value(value).value == value

    # The example values from above
    @pytest.mark.parametrize(
        "value", [0xF111, 0xE011, 0xE111, 0xE121, 0xE012, 0x00F0D121]
    )
    def test_from_string(self, value):
        before = HidUnit.from_value(0xF011)
        after = HidUnit.from_string(str(before))
        assert before == after

    # All possible permutations of allowed values
    # We don't test None/Reserved here
    @pytest.mark.parametrize("system", range(0x1, 0x5))
    @pytest.mark.parametrize("exp", range(0x1, 0x10))
    @pytest.mark.parametrize("nibble", range(0x1, 0x7))
    def test_from_string_all(self, system, exp, nibble):
        value = system | (exp << (nibble * 4))
        before = HidUnit.from_value(value)
        after = HidUnit.from_string(str(before))
        assert before == after
