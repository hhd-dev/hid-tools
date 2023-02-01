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

import fcntl
import functools
import libevdev
import os

try:
    import pyudev
except ImportError:
    raise ImportError("UHID is not supported due to missing pyudev dependency")

import logging

import hidtools.hid as hid
from hidtools.uhid import UHIDDevice
from hidtools.util import BusType

from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Type

logger = logging.getLogger("hidtools.device.base_device")


class SysfsFile(object):
    def __init__(self, path):
        self.path = path

    def __set_value(self, value):
        with open(self.path, "w") as f:
            return f.write(f"{value}\n")

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
    def __init__(self, sys_path):
        self.max_brightness = SysfsFile(sys_path / "max_brightness").int_value
        self.__brightness = SysfsFile(sys_path / "brightness")

    @property
    def brightness(self):
        return self.__brightness.int_value

    @brightness.setter
    def brightness(self, value):
        self.__brightness.int_value = value


class PowerSupply(object):
    """Represents Linux power_supply_class sysfs nodes."""

    def __init__(self, sys_path):
        self._capacity = SysfsFile(sys_path / "capacity")
        self._status = SysfsFile(sys_path / "status")
        self._type = SysfsFile(sys_path / "type")

    @property
    def capacity(self):
        return self._capacity.int_value

    @property
    def status(self):
        return self._status.str_value

    @property
    def type(self):
        return self._type.str_value


class EvdevMatch(object):
    def __init__(
        self: "EvdevMatch",
        *,
        requires: List[Any] = [],
        excludes: List[Any] = [],
        req_properties: List[Any] = [],
        excl_properties: List[Any] = [],
    ) -> None:
        self.requires = requires
        self.excludes = excludes
        self.req_properties = req_properties
        self.excl_properties = excl_properties

    def is_a_match(self: "EvdevMatch", evdev: libevdev.Device) -> bool:
        for m in self.requires:
            if not evdev.has(m):
                return False
        for m in self.excludes:
            if evdev.has(m):
                return False
        for p in self.req_properties:
            if not evdev.has_property(p):
                return False
        for p in self.excl_properties:
            if evdev.has_property(p):
                return False
        return True


class EvdevDevice(object):
    """
    Represents an Evdev node and its properties.
    This is a stub for the libevdev devices, as they are relying on
    uevent to get the data, saving us some ioctls to fetch the names
    and properties.
    """

    # application to matches
    _application_matches: Final = {
        # pyright: ignore
        "Accelerometer": EvdevMatch(
            req_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ]
        ),
        "Game Pad": EvdevMatch(  # in systemd, this is a lot more complex, but that will do
            requires=[
                libevdev.EV_ABS.ABS_X,
                libevdev.EV_ABS.ABS_Y,
                libevdev.EV_ABS.ABS_RX,
                libevdev.EV_ABS.ABS_RY,
                libevdev.EV_KEY.BTN_START,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Joystick": EvdevMatch(  # in systemd, this is a lot more complex, but that will do
            requires=[
                libevdev.EV_ABS.ABS_RX,
                libevdev.EV_ABS.ABS_RY,
                libevdev.EV_KEY.BTN_START,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Key": EvdevMatch(
            requires=[
                libevdev.EV_KEY.KEY_A,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
                libevdev.INPUT_PROP_DIRECT,
                libevdev.INPUT_PROP_POINTER,
            ],
        ),
        "Mouse": EvdevMatch(
            requires=[
                libevdev.EV_REL.REL_X,
                libevdev.EV_REL.REL_Y,
                libevdev.EV_KEY.BTN_LEFT,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Pad": EvdevMatch(
            requires=[
                libevdev.EV_KEY.BTN_0,
            ],
            excludes=[
                libevdev.EV_KEY.BTN_TOOL_PEN,
                libevdev.EV_KEY.BTN_TOUCH,
                libevdev.EV_ABS.ABS_DISTANCE,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Pen": EvdevMatch(
            requires=[
                libevdev.EV_KEY.BTN_STYLUS,
                libevdev.EV_ABS.ABS_X,
                libevdev.EV_ABS.ABS_Y,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Stylus": EvdevMatch(
            requires=[
                libevdev.EV_KEY.BTN_STYLUS,
                libevdev.EV_ABS.ABS_X,
                libevdev.EV_ABS.ABS_Y,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Touch Pad": EvdevMatch(
            requires=[
                libevdev.EV_KEY.BTN_LEFT,
                libevdev.EV_ABS.ABS_X,
                libevdev.EV_ABS.ABS_Y,
            ],
            excludes=[libevdev.EV_KEY.BTN_TOOL_PEN, libevdev.EV_KEY.BTN_STYLUS],
            req_properties=[
                libevdev.INPUT_PROP_POINTER,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
        "Touch Screen": EvdevMatch(
            requires=[
                libevdev.EV_KEY.BTN_TOUCH,
                libevdev.EV_ABS.ABS_X,
                libevdev.EV_ABS.ABS_Y,
            ],
            excludes=[libevdev.EV_KEY.BTN_TOOL_PEN, libevdev.EV_KEY.BTN_STYLUS],
            req_properties=[
                libevdev.INPUT_PROP_DIRECT,
            ],
            excl_properties=[
                libevdev.INPUT_PROP_ACCELEROMETER,
            ],
        ),
    }

    def __init__(self: "EvdevDevice", sysfs: Path) -> None:
        self.sysfs = sysfs
        self.event_node: Any = None
        self.libevdev: Optional[libevdev.Device] = None

        self.uevents = {}
        # all of the interesting properties are stored in the input uevent, so in the parent
        # so convert the uevent file of the parent input node into a dict
        with open(sysfs.parent / "uevent") as f:
            for line in f.readlines():
                key, value = line.strip().split("=")
                self.uevents[key] = value.strip('"')

        # we open all evdev nodes in order to not miss any event
        self.open()

    @property
    def name(self: "EvdevDevice") -> str:
        assert "NAME" in self.uevents

        return self.uevents["NAME"]

    @property
    def evdev(self: "EvdevDevice") -> Path:
        return Path("/dev/input") / self.sysfs.name

    def matches_application(self: "EvdevDevice", application: str) -> bool:
        if self.libevdev is None:
            return False

        if application in self._application_matches:
            return self._application_matches[application].is_a_match(self.libevdev)

        logger.error(
            f"application '{application}' is unknown, please update/fix hid-tools"
        )
        assert False  # hid-tools likely needs an update

    def open(self: "EvdevDevice") -> libevdev.Device:
        self.event_node = open(self.evdev, "rb")
        self.libevdev = libevdev.Device(self.event_node)

        assert self.libevdev.fd is not None

        fd = self.libevdev.fd.fileno()
        flag = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

        return self.libevdev

    def close(self: "EvdevDevice") -> None:
        if self.libevdev is not None and self.libevdev.fd is not None:
            self.libevdev.fd.close()
            self.libevdev = None
        if self.event_node is not None:
            self.event_node.close()
            self.event_node = None


class _BaseDevice(UHIDDevice):
    def __init__(self, name, application, rdesc_str=None, rdesc=None, input_info=None):
        if rdesc_str is None and rdesc is None:
            raise Exception("Please provide at least a rdesc or rdesc_str")
        super().__init__()
        if name is None:
            name = f"uhid gamepad test {self.__class__.__name__}"
        if input_info is None:
            input_info = (BusType.USB, 1, 2)
        self.name = name
        self.info = input_info
        self.default_reportID = None
        self.opened = False
        self.started = False
        self.application = application
        self._input_nodes = None
        if rdesc is None:
            assert rdesc_str is not None
            self.rdesc = hid.ReportDescriptor.from_human_descr(rdesc_str)
        else:
            self.rdesc = rdesc

    @property
    def power_supply_class(self: "_BaseDevice") -> Optional[PowerSupply]:
        ps = self.walk_sysfs("power_supply", "power_supply/*")
        if ps is None or len(ps) < 1:
            return None

        return PowerSupply(ps[0])

    @property
    def led_classes(self: "_BaseDevice") -> List[LED]:
        leds = self.walk_sysfs("led", "**/max_brightness")
        if leds is None:
            return []

        return [LED(led.parent) for led in leds]

    @property
    def kernel_is_ready(self: "_BaseDevice") -> bool:
        return True

    @property
    def input_nodes(self: "_BaseDevice") -> List[EvdevDevice]:
        if self._input_nodes is not None:
            return self._input_nodes

        if not self.kernel_is_ready or not self.started:
            return []

        self._input_nodes = [
            EvdevDevice(path)
            for path in self.walk_sysfs("input", "input/input*/event*")
        ]
        return self._input_nodes

    def match_evdev_rule(self, application, evdev):
        """Replace this in subclasses if the device has multiple reports
        of the same type and we need to filter based on the actual evdev
        node.

        returning True will append the corresponding report to
        `self.input_nodes[type]`
        returning False  will ignore this report / type combination
        for the device.
        """
        return True

    def open(self):
        self.opened = True

    def _close_all_opened_evdev(self):
        if self._input_nodes is not None:
            for e in self._input_nodes:
                e.close()

    def __del__(self):
        self._close_all_opened_evdev()

    def close(self):
        self.opened = False

    def start(self, flags):
        self.started = True

    def stop(self):
        self.started = False
        self._close_all_opened_evdev()

    def next_sync_events(self, application=None):
        evdev = self.get_evdev(application)
        if evdev is not None:
            return list(evdev.events())
        return []

    def get_evdev(self, application=None):
        if application is None:
            application = self.application

        if len(self.input_nodes) == 0:
            return None

        assert self._input_nodes is not None

        if len(self._input_nodes) == 1:
            evdev = self._input_nodes[0]
            if self.match_evdev_rule(application, evdev.libevdev):
                return evdev.libevdev
        else:
            for _evdev in self._input_nodes:
                if _evdev.matches_application(application):
                    if self.match_evdev_rule(application, _evdev.libevdev):
                        return _evdev.libevdev

    def is_ready(self):
        """Returns whether a UHID device is ready. Can be overwritten in
        subclasses to add extra conditions on when to consider a UHID
        device ready. This can be:

        - we need to wait on different types of input devices to be ready
          (Touch Screen and Pen for example)
        - we need to have at least 4 LEDs present
          (len(self.uhdev.leds_classes) == 4)
        - or any other combinations"""
        return self.kernel_is_ready and self.started


class BaseDevice(_BaseDevice):
    """
    A uhid device with a udev manager. uhid is a kernel interface to
    create virtual HID devices based on a report descriptor.

    This class also acts as context manager for any :class:`UHIDDevice`
    objects. See :meth:`dispatch` for details.

    .. attribute:: uniq

        A uniq string assigned to this device. This string is autogenerated
        and can be used to reliably identify the device.

    """

    input_type_mapping = {
        "ID_INPUT_TOUCHSCREEN": ["Touch Screen"],
        "ID_INPUT_TOUCHPAD": ["Touch Pad"],
        "ID_INPUT_TABLET": ["Pen"],
        "ID_INPUT_TABLET_PAD": ["Pad"],
        "ID_INPUT_MOUSE": ["Mouse"],
        "ID_INPUT_KEY": ["Key"],
        "ID_INPUT_JOYSTICK": ["Joystick", "Game Pad"],
        "ID_INPUT_ACCELEROMETER": ["Accelerometer"],
    }

    _pyudev_context: Optional[pyudev.Context] = None
    _pyudev_monitor: Optional[pyudev.Monitor] = None
    _uhid_devices: Dict[int, bool] = {}

    def __init__(
        self: "BaseDevice",
        name,
        application,
        rdesc_str=None,
        rdesc=None,
        input_info=None,
    ) -> None:
        self._init_pyudev()
        self._udev_device: Optional[pyudev.Device] = None
        super().__init__(name, application, rdesc_str, rdesc, input_info)

    @classmethod
    def _init_pyudev(cls: Type["BaseDevice"]) -> None:
        if cls._pyudev_context is None:
            cls._pyudev_context = pyudev.Context()
            cls._pyudev_monitor = pyudev.Monitor.from_netlink(cls._pyudev_context)
            cls._pyudev_monitor.filter_by("hid")
            cls._pyudev_monitor.start()

            cls._append_fd_to_poll(
                cls._pyudev_monitor.fileno(), cls._cls_udev_event_callback
            )

    @classmethod
    def _cls_udev_event_callback(cls: Type["BaseDevice"]) -> None:
        if cls._pyudev_monitor is None:
            return
        event: pyudev.Device
        for event in iter(functools.partial(cls._pyudev_monitor.poll, 0.02), None):
            if event.action not in ["bind", "remove"]:
                return

            logger.debug(f"udev event: {event.action} -> {event}")

            id = int(event.sys_path.strip().split(".")[-1], 16)

            cls._uhid_devices[id] = event.action == "bind"

    @property
    def kernel_is_ready(self: "BaseDevice") -> bool:
        try:
            return self._uhid_devices[self.hid_id]
        except KeyError:
            return False
