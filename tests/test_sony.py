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

from .test_gamepad import BaseTest
from hidtools.device.sony_gamepad import PS3Controller, PS4ControllerBluetooth, PS4ControllerUSB

import logging
import pytest
logger = logging.getLogger('hidtools.test.sony')


class SonyBaseTest:
    class SonyTest(BaseTest.TestGamepad):
        pass


class TestPS3Controller(SonyBaseTest.SonyTest):
    def create_device(self):
        return PS3Controller()

    @pytest.fixture(autouse=True)
    def start_controller(self):
        # emulate a 'PS' button press to tell the kernel we are ready to accept events
        self.assert_button(17)

        # drain any remaining udev events
        while self.uhdev.dispatch(10):
            pass

        def test_led(self):
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


class TestPS4ControllerBluetooth(SonyBaseTest.SonyTest):
    def create_device(self):
        return PS4ControllerBluetooth()


class TestPS4ControllerUSB(SonyBaseTest.SonyTest):
    def create_device(self):
        return PS4ControllerUSB()
