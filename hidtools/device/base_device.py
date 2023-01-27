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
import pathlib

try:
    import pyudev
except ImportError:
    raise ImportError("UHID is not supported due to missing pyudev dependency")

import logging

import hidtools.hid as hid
from hidtools.uhid import UHIDDevice
from hidtools.util import BusType

from typing import Optional, Type

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
    def __init__(self, udev_object):
        self.sys_path = pathlib.Path(udev_object.sys_path)
        self.max_brightness = SysfsFile(self.sys_path / "max_brightness").int_value
        self.__brightness = SysfsFile(self.sys_path / "brightness")

    @property
    def brightness(self):
        return self.__brightness.int_value

    @brightness.setter
    def brightness(self, value):
        self.__brightness.int_value = value


class PowerSupply(object):
    """Represents Linux power_supply_class sysfs nodes."""

    def __init__(self, udev_object):
        self.sys_path = pathlib.Path(udev_object.sys_path)
        self._capacity = SysfsFile(self.sys_path / "capacity")
        self._status = SysfsFile(self.sys_path / "status")
        self._type = SysfsFile(self.sys_path / "type")

    @property
    def capacity(self):
        return self._capacity.int_value

    @property
    def status(self):
        return self._status.str_value

    @property
    def type(self):
        return self._type.str_value


class _BaseDevice(UHIDDevice):
    def __init__(self, name, application, rdesc_str=None, rdesc=None, input_info=None):
        self._opened_files = []
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
        self.application = application
        self.input_nodes = {}
        self.led_classes = {}
        self.power_supply_class = None
        if rdesc is None:
            assert rdesc_str is not None
            self.rdesc = hid.ReportDescriptor.from_human_descr(rdesc_str)
        else:
            self.rdesc = rdesc

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
            del self.input_nodes[name]

    def next_sync_events(self, application=None):
        evdev = self.get_evdev(application)
        if evdev is not None:
            return list(evdev.events())
        return []

    def get_evdev(self, application=None):
        if application is None:
            application = self.application

        if application not in self.input_nodes:
            return None

        return self.input_nodes[application]

    def is_ready(self):
        """Returns whether a UHID device is ready. Can be overwritten in
        subclasses to add extra conditions on when to consider a UHID
        device ready. This can be:

        - we need to wait on different types of input devices to be ready
          (Touch Screen and Pen for example)
        - we need to have at least 4 LEDs present
          (len(self.uhdev.leds_classes) == 4)
        - or any other combinations"""
        return self.application in self.input_nodes


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
            logger.debug(f"udev event: {event.action} -> {event}")

            for d in cls._devices:
                if (
                    isinstance(d, BaseDevice)
                    and d.udev_device is not None
                    and d.udev_device.sys_path in event.sys_path
                ):
                    d._udev_event(event)

    def _udev_event(self: "BaseDevice", event: pyudev.Device) -> None:
        # we do not need to process the udev events if the device is being
        # removed
        if not self._ready:
            return

        self.udev_event(event)

    @property
    def udev_device(self: "BaseDevice") -> Optional[pyudev.Device]:
        """
        The devices' udev device.

        The device may be None if udev hasn't processed the device yet.
        """
        if self._udev_device is None and self._pyudev_context is not None:
            device: pyudev.Device
            for device in self._pyudev_context.list_devices(subsystem="hid"):
                try:
                    if self.uniq == device.properties["HID_UNIQ"]:
                        self._udev_device = device
                        break
                except KeyError:
                    pass
        return self._udev_device

    def udev_input_event(self, device):
        if "DEVNAME" not in device.properties:
            return

        devname = device.properties["DEVNAME"]
        if not devname.startswith("/dev/input/event"):
            return

        # associate the Input type to the matching HID application
        # we reuse the guess work from udev
        types = []
        for name, type_list in BaseDevice.input_type_mapping.items():
            for type in type_list:
                # do not duplicate event nodes if the application matches
                # one of the type
                if len(type_list) > 1:
                    if self.application in type_list and type != self.application:
                        continue
                if name in device.properties:
                    types.append(type)

        if not types:
            # abort, the device has not been processed by udev
            print("abort", devname, list(device.properties.items()))
            return

        event_node = open(devname, "rb")
        self._opened_files.append(event_node)
        evdev = libevdev.Device(event_node)

        assert evdev.fd is not None

        fd = evdev.fd.fileno()
        flag = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

        used = False
        for type in types:
            # check for custom defined matching
            if self.match_evdev_rule(type, evdev):
                self.input_nodes[type] = evdev
                used = True
        if not used:
            evdev.fd.close()

    def udev_led_event(self, device):
        led = LED(device)
        self.led_classes[led.sys_path.name] = led

    def udev_power_supply_event(self, device):
        # we may be presented the event more than once
        if self.power_supply_class is not None:
            return

        self.power_supply_class = PowerSupply(device)

    def udev_event(self, event):
        if event.action == "remove":
            return

        device = event

        subsystem = device.properties["SUBSYSTEM"]

        # power_supply events are presented with a 'change' event
        if subsystem == "power_supply":
            return self.udev_power_supply_event(device)

        # others are still using 'add'
        if event.action != "add":
            return

        if subsystem == "input":
            return self.udev_input_event(device)
        elif subsystem == "leds":
            return self.udev_led_event(device)
        elif subsystem == "hwmon":
            # Often power_supply is managed by hwmon and it will appear during 'add'
            # and not the power_supply itself directly.
            if "power_supply" in device.sys_path:
                # The 'device' directory brings us back to the power_supply.
                power_supply = pyudev.Devices.from_sys_path(
                    device.context, device.sys_path + "/device"
                )
                return self.udev_power_supply_event(power_supply)

        logger.debug(f"{subsystem}: {device}")
