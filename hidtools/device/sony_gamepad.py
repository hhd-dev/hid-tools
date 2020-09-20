import random
import struct

from hidtools.device.base_gamepad import AxisMapping, BaseGamepad

import logging
logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s',
                    level=logging.INFO)
base_logger = logging.getLogger('hidtools')
logger = logging.getLogger('hidtools.device.sony_gamepad')


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

    axes_map = {
        'left_stick': {
            'x': AxisMapping('x'),
            'y': AxisMapping('y'),
        },
        'right_stick': {
            'x': AxisMapping('z', 'ABS_RX'),
            'y': AxisMapping('Rz', 'ABS_RY'),
        },
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

    def is_ready(self):
        return super().is_ready() and len(self.led_classes) == 4

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

        logger.debug(f'set_report {bool(rdesc)}, {req}, {rnum}, {rtype}, {data}')

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


class PS4Controller(BaseGamepad):
    buttons_map = {
        1: 'BTN_WEST',              # square
        2: 'BTN_SOUTH',             # cross
        3: 'BTN_EAST',              # circle
        4: 'BTN_NORTH',             # triangle
        5: 'BTN_TL',                # L1
        6: 'BTN_TR',                # R1
        7: 'BTN_TL2',               # L2
        8: 'BTN_TR2',               # R2
        9: 'BTN_SELECT',            # share
        10: 'BTN_START',            # options
        11: 'BTN_THUMBL',           # L3
        12: 'BTN_THUMBR',           # R3
        13: 'BTN_MODE',             # PS button
    }

    axes_map = {
        'left_stick': {
            'x': AxisMapping('x'),
            'y': AxisMapping('y'),
        },
        'right_stick': {
            'x': AxisMapping('z', 'ABS_RX'),
            'y': AxisMapping('Rz', 'ABS_RY'),
        },
    }

    def __init__(self, rdesc, name, input_info):
        super().__init__(rdesc, name, input_info)
        self.uniq = ':'.join([f'{random.randint(0, 0xff):02x}' for i in range(6)])
        self.buttons = tuple(range(1, 13))

    def is_ready(self):
        return super().is_ready() and len(self.input_nodes) == 3 and len(self.led_classes) == 4


class PS4ControllerUSB(PS4Controller):
    report_descriptor = [
        0x05, 0x01,                    # Usage Page (Generic Desktop)        0
        0x09, 0x05,                    # Usage (Game Pad)                    2
        0xa1, 0x01,                    # Collection (Application)            4
        0x85, 0x01,                    # .Report ID (1)                      6
        0x09, 0x30,                    # .Usage (X)                          8
        0x09, 0x31,                    # .Usage (Y)                          10
        0x09, 0x32,                    # .Usage (Z)                          12
        0x09, 0x35,                    # .Usage (Rz)                         14
        0x15, 0x00,                    # .Logical Minimum (0)                16
        0x26, 0xff, 0x00,              # .Logical Maximum (255)              18
        0x75, 0x08,                    # .Report Size (8)                    21
        0x95, 0x04,                    # .Report Count (4)                   23
        0x81, 0x02,                    # .Input (Data,Var,Abs)               25
        0x09, 0x39,                    # .Usage (Hat switch)                 27
        0x15, 0x00,                    # .Logical Minimum (0)                29
        0x25, 0x07,                    # .Logical Maximum (7)                31
        0x35, 0x00,                    # .Physical Minimum (0)               33
        0x46, 0x3b, 0x01,              # .Physical Maximum (315)             35
        0x65, 0x14,                    # .Unit (Degrees,EngRotation)         38
        0x75, 0x04,                    # .Report Size (4)                    40
        0x95, 0x01,                    # .Report Count (1)                   42
        0x81, 0x42,                    # .Input (Data,Var,Abs,Null)          44
        0x65, 0x00,                    # .Unit (None)                        46
        0x05, 0x09,                    # .Usage Page (Button)                48
        0x19, 0x01,                    # .Usage Minimum (1)                  50
        0x29, 0x0e,                    # .Usage Maximum (14)                 52
        0x15, 0x00,                    # .Logical Minimum (0)                54
        0x25, 0x01,                    # .Logical Maximum (1)                56
        0x75, 0x01,                    # .Report Size (1)                    58
        0x95, 0x0e,                    # .Report Count (14)                  60
        0x81, 0x02,                    # .Input (Data,Var,Abs)               62
        0x06, 0x00, 0xff,              # .Usage Page (Vendor Defined Page 1) 64
        0x09, 0x20,                    # .Usage (Vendor Usage 0x20)          67
        0x75, 0x06,                    # .Report Size (6)                    69
        0x95, 0x01,                    # .Report Count (1)                   71
        0x15, 0x00,                    # .Logical Minimum (0)                73
        0x25, 0x7f,                    # .Logical Maximum (127)              75
        0x81, 0x02,                    # .Input (Data,Var,Abs)               77
        0x05, 0x01,                    # .Usage Page (Generic Desktop)       79
        0x09, 0x33,                    # .Usage (Rx)                         81
        0x09, 0x34,                    # .Usage (Ry)                         83
        0x15, 0x00,                    # .Logical Minimum (0)                85
        0x26, 0xff, 0x00,              # .Logical Maximum (255)              87
        0x75, 0x08,                    # .Report Size (8)                    90
        0x95, 0x02,                    # .Report Count (2)                   92
        0x81, 0x02,                    # .Input (Data,Var,Abs)               94
        0x06, 0x00, 0xff,              # .Usage Page (Vendor Defined Page 1) 96
        0x09, 0x21,                    # .Usage (Vendor Usage 0x21)          99
        0x95, 0x36,                    # .Report Count (54)                  101
        0x81, 0x02,                    # .Input (Data,Var,Abs)               103
        0x85, 0x05,                    # .Report ID (5)                      105
        0x09, 0x22,                    # .Usage (Vendor Usage 0x22)          107
        0x95, 0x1f,                    # .Report Count (31)                  109
        0x91, 0x02,                    # .Output (Data,Var,Abs)              111
        0x85, 0x04,                    # .Report ID (4)                      113
        0x09, 0x23,                    # .Usage (Vendor Usage 0x23)          115
        0x95, 0x24,                    # .Report Count (36)                  117
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             119
        0x85, 0x02,                    # .Report ID (2)                      121
        0x09, 0x24,                    # .Usage (Vendor Usage 0x24)          123
        0x95, 0x24,                    # .Report Count (36)                  125
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             127
        0x85, 0x08,                    # .Report ID (8)                      129
        0x09, 0x25,                    # .Usage (Vendor Usage 0x25)          131
        0x95, 0x03,                    # .Report Count (3)                   133
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             135
        0x85, 0x10,                    # .Report ID (16)                     137
        0x09, 0x26,                    # .Usage (Vendor Usage 0x26)          139
        0x95, 0x04,                    # .Report Count (4)                   141
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             143
        0x85, 0x11,                    # .Report ID (17)                     145
        0x09, 0x27,                    # .Usage (Vendor Usage 0x27)          147
        0x95, 0x02,                    # .Report Count (2)                   149
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             151
        0x85, 0x12,                    # .Report ID (18)                     153
        0x06, 0x02, 0xff,              # .Usage Page (Vendor Usage Page 0xff02) 155
        0x09, 0x21,                    # .Usage (Vendor Usage 0x21)          158
        0x95, 0x0f,                    # .Report Count (15)                  160
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             162
        0x85, 0x13,                    # .Report ID (19)                     164
        0x09, 0x22,                    # .Usage (Vendor Usage 0x22)          166
        0x95, 0x16,                    # .Report Count (22)                  168
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             170
        0x85, 0x14,                    # .Report ID (20)                     172
        0x06, 0x05, 0xff,              # .Usage Page (Vendor Usage Page 0xff05) 174
        0x09, 0x20,                    # .Usage (Vendor Usage 0x20)          177
        0x95, 0x10,                    # .Report Count (16)                  179
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             181
        0x85, 0x15,                    # .Report ID (21)                     183
        0x09, 0x21,                    # .Usage (Vendor Usage 0x21)          185
        0x95, 0x2c,                    # .Report Count (44)                  187
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             189
        0x06, 0x80, 0xff,              # .Usage Page (Vendor Usage Page 0xff80) 191
        0x85, 0x80,                    # .Report ID (128)                    194
        0x09, 0x20,                    # .Usage (Vendor Usage 0x20)          196
        0x95, 0x06,                    # .Report Count (6)                   198
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             200
        0x85, 0x81,                    # .Report ID (129)                    202
        0x09, 0x21,                    # .Usage (Vendor Usage 0x21)          204
        0x95, 0x06,                    # .Report Count (6)                   206
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             208
        0x85, 0x82,                    # .Report ID (130)                    210
        0x09, 0x22,                    # .Usage (Vendor Usage 0x22)          212
        0x95, 0x05,                    # .Report Count (5)                   214
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             216
        0x85, 0x83,                    # .Report ID (131)                    218
        0x09, 0x23,                    # .Usage (Vendor Usage 0x23)          220
        0x95, 0x01,                    # .Report Count (1)                   222
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             224
        0x85, 0x84,                    # .Report ID (132)                    226
        0x09, 0x24,                    # .Usage (Vendor Usage 0x24)          228
        0x95, 0x04,                    # .Report Count (4)                   230
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             232
        0x85, 0x85,                    # .Report ID (133)                    234
        0x09, 0x25,                    # .Usage (Vendor Usage 0x25)          236
        0x95, 0x06,                    # .Report Count (6)                   238
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             240
        0x85, 0x86,                    # .Report ID (134)                    242
        0x09, 0x26,                    # .Usage (Vendor Usage 0x26)          244
        0x95, 0x06,                    # .Report Count (6)                   246
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             248
        0x85, 0x87,                    # .Report ID (135)                    250
        0x09, 0x27,                    # .Usage (Vendor Usage 0x27)          252
        0x95, 0x23,                    # .Report Count (35)                  254
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             256
        0x85, 0x88,                    # .Report ID (136)                    258
        0x09, 0x28,                    # .Usage (Vendor Usage 0x28)          260
        0x95, 0x3f,                    # .Report Count (63)                  262
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             264
        0x85, 0x89,                    # .Report ID (137)                    266
        0x09, 0x29,                    # .Usage (Vendor Usage 0x29)          268
        0x95, 0x02,                    # .Report Count (2)                   270
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             272
        0x85, 0x90,                    # .Report ID (144)                    274
        0x09, 0x30,                    # .Usage (Vendor Usage 0x30)          276
        0x95, 0x05,                    # .Report Count (5)                   278
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             280
        0x85, 0x91,                    # .Report ID (145)                    282
        0x09, 0x31,                    # .Usage (Vendor Usage 0x31)          284
        0x95, 0x03,                    # .Report Count (3)                   286
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             288
        0x85, 0x92,                    # .Report ID (146)                    290
        0x09, 0x32,                    # .Usage (Vendor Usage 0x32)          292
        0x95, 0x03,                    # .Report Count (3)                   294
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             296
        0x85, 0x93,                    # .Report ID (147)                    298
        0x09, 0x33,                    # .Usage (Vendor Usage 0x33)          300
        0x95, 0x0c,                    # .Report Count (12)                  302
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             304
        0x85, 0x94,                    # .Report ID (148)                    306
        0x09, 0x34,                    # .Usage (Vendor Usage 0x34)          308
        0x95, 0x3f,                    # .Report Count (63)                  310
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             312
        0x85, 0xa0,                    # .Report ID (160)                    314
        0x09, 0x40,                    # .Usage (Vendor Usage 0x40)          316
        0x95, 0x06,                    # .Report Count (6)                   318
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             320
        0x85, 0xa1,                    # .Report ID (161)                    322
        0x09, 0x41,                    # .Usage (Vendor Usage 0x41)          324
        0x95, 0x01,                    # .Report Count (1)                   326
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             328
        0x85, 0xa2,                    # .Report ID (162)                    330
        0x09, 0x42,                    # .Usage (Vendor Usage 0x42)          332
        0x95, 0x01,                    # .Report Count (1)                   334
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             336
        0x85, 0xa3,                    # .Report ID (163)                    338
        0x09, 0x43,                    # .Usage (Vendor Usage 0x43)          340
        0x95, 0x30,                    # .Report Count (48)                  342
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             344
        0x85, 0xa4,                    # .Report ID (164)                    346
        0x09, 0x44,                    # .Usage (Vendor Usage 0x44)          348
        0x95, 0x0d,                    # .Report Count (13)                  350
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             352
        0x85, 0xf0,                    # .Report ID (240)                    354
        0x09, 0x47,                    # .Usage (Vendor Usage 0x47)          356
        0x95, 0x3f,                    # .Report Count (63)                  358
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             360
        0x85, 0xf1,                    # .Report ID (241)                    362
        0x09, 0x48,                    # .Usage (Vendor Usage 0x48)          364
        0x95, 0x3f,                    # .Report Count (63)                  366
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             368
        0x85, 0xf2,                    # .Report ID (242)                    370
        0x09, 0x49,                    # .Usage (Vendor Usage 0x49)          372
        0x95, 0x0f,                    # .Report Count (15)                  374
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             376
        0x85, 0xa7,                    # .Report ID (167)                    378
        0x09, 0x4a,                    # .Usage (Vendor Usage 0x4a)          380
        0x95, 0x01,                    # .Report Count (1)                   382
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             384
        0x85, 0xa8,                    # .Report ID (168)                    386
        0x09, 0x4b,                    # .Usage (Vendor Usage 0x4b)          388
        0x95, 0x01,                    # .Report Count (1)                   390
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             392
        0x85, 0xa9,                    # .Report ID (169)                    394
        0x09, 0x4c,                    # .Usage (Vendor Usage 0x4c)          396
        0x95, 0x08,                    # .Report Count (8)                   398
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             400
        0x85, 0xaa,                    # .Report ID (170)                    402
        0x09, 0x4e,                    # .Usage (Vendor Usage 0x4e)          404
        0x95, 0x01,                    # .Report Count (1)                   406
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             408
        0x85, 0xab,                    # .Report ID (171)                    410
        0x09, 0x4f,                    # .Usage (Vendor Usage 0x4f)          412
        0x95, 0x39,                    # .Report Count (57)                  414
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             416
        0x85, 0xac,                    # .Report ID (172)                    418
        0x09, 0x50,                    # .Usage (Vendor Usage 0x50)          420
        0x95, 0x39,                    # .Report Count (57)                  422
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             424
        0x85, 0xad,                    # .Report ID (173)                    426
        0x09, 0x51,                    # .Usage (Vendor Usage 0x51)          428
        0x95, 0x0b,                    # .Report Count (11)                  430
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             432
        0x85, 0xae,                    # .Report ID (174)                    434
        0x09, 0x52,                    # .Usage (Vendor Usage 0x52)          436
        0x95, 0x01,                    # .Report Count (1)                   438
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             440
        0x85, 0xaf,                    # .Report ID (175)                    442
        0x09, 0x53,                    # .Usage (Vendor Usage 0x53)          444
        0x95, 0x02,                    # .Report Count (2)                   446
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             448
        0x85, 0xb0,                    # .Report ID (176)                    450
        0x09, 0x54,                    # .Usage (Vendor Usage 0x54)          452
        0x95, 0x3f,                    # .Report Count (63)                  454
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             456
        0x85, 0xe0,                    # .Report ID (224)                    458
        0x09, 0x57,                    # .Usage (Vendor Usage 0x57)          460
        0x95, 0x02,                    # .Report Count (2)                   462
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             464
        0x85, 0xb3,                    # .Report ID (179)                    466
        0x09, 0x55,                    # .Usage (Vendor Usage 0x55)          468
        0x95, 0x3f,                    # .Report Count (63)                  470
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             472
        0x85, 0xb4,                    # .Report ID (180)                    474
        0x09, 0x55,                    # .Usage (Vendor Usage 0x55)          476
        0x95, 0x3f,                    # .Report Count (63)                  478
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             480
        0x85, 0xb5,                    # .Report ID (181)                    482
        0x09, 0x56,                    # .Usage (Vendor Usage 0x56)          484
        0x95, 0x3f,                    # .Report Count (63)                  486
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             488
        0x85, 0xd0,                    # .Report ID (208)                    490
        0x09, 0x58,                    # .Usage (Vendor Usage 0x58)          492
        0x95, 0x3f,                    # .Report Count (63)                  494
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             496
        0x85, 0xd4,                    # .Report ID (212)                    498
        0x09, 0x59,                    # .Usage (Vendor Usage 0x59)          500
        0x95, 0x3f,                    # .Report Count (63)                  502
        0xb1, 0x02,                    # .Feature (Data,Var,Abs)             504
        0xc0,                          # End Collection                      506
    ]

    def __init__(self, rdesc=report_descriptor):
        super().__init__(rdesc, 'Sony Computer Entertainment Wireless Controller', (3, 0x054c, 0x05c4))

    def get_report(self, req, rnum, rtype):
        rdesc = None
        for v in self.parsed_rdesc.feature_reports.values():
            if v.report_ID == rnum:
                rdesc = v

        logger.debug(f'get_report {rdesc}, {req}, {rnum}, {rtype}')

        if rnum == 0x02:
            # Report to retrieve motion sensor calibration data.
            r = [0x02, 0x1e, 0x00, 0x05, 0x00, 0xe2, 0xff, 0xf2, 0x22, 0x4f, 0xdd, 0x4d, 0xdd, 0xbe,
                 0x22, 0x8d, 0x22, 0x39, 0xdd, 0x1c, 0x02, 0x1c, 0x02, 0xe3, 0x1f, 0x8b, 0xdf, 0x8c,
                 0x1e, 0xb4, 0xde, 0x30, 0x20, 0x71, 0xe0, 0x10, 0x00]
            return (0, r)

        elif rnum == 0x81:
            # Report to retrieve MAC address of DS4.
            # MAC address is stored in byte 1-7
            r = [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

            # store the uniq value in the report
            for id, v in enumerate(self.uniq.split(':')):
                # store in little endian
                r[6 - id] = int(v, 16)

            return (0, r)

        elif rnum == 0xa3:
            # Report to retrieve hardware and firmware version.
            r = [0xa3, 0x41, 0x70, 0x72, 0x20, 0x20, 0x38, 0x20, 0x32, 0x30, 0x31, 0x34, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x30, 0x39, 0x3a, 0x34, 0x36, 0x3a, 0x30, 0x36, 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x43, 0x03, 0x00, 0x00, 0x00, 0x51, 0x00, 0x05,
                 0x00, 0x00, 0x80, 0x03, 0x00]
            return (0, r)

        if rdesc is None:
            return (1, [])

        return (1, [])
