#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2017 Benjamin Tissoires <benjamin.tissoires@gmail.com>
# Copyright (c) 2012-2017 Red Hat, Inc.
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

import enum


class BusType(enum.IntEnum):
    """
    The numerical bus type (``0x3`` for USB, ``0x5`` for Bluetooth, see
        ``linux/input.h``)
    """
    USB = 0x3
    BLUETOOTH = 0x5
    VIRTUAL = 0x6
    I2C = 0x18
    HOST = 0x19


def twos_comp(val, bits):
    """compute the 2's complement of val.

    :param int val:
        the value to compute the two's complement for

    :param int bits:
        size of val in bits
    """
    if bits and (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def to_twos_comp(val, bits):
    return val & ((1 << bits) - 1)
