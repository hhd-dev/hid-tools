hid-tools is a set of tools to interact with the kernel's HID subsystem.

It can be run directly from the git repository or installed via `pip3
install hid-tools`.

# Installation

The `hid-tools` repository does not need to be installed, all tools and
kernel tests can be run straight from the git repository, for example the
following commands clone the repository and run the `hid-recorder` tool.

```
$ git clone https://gitlab.freedesktop.org/libevdev/hid-tools
$ cd hid-tools
$ sudo ./hid-recorder
```

Where the tools need to be installed, it is recommended to use `pip`:

```
$ sudo pip3 install .
```

This installs all tools into the system-wide Python path. hid-tools needs
root access to the `/dev/hidraw` nodes, an installation in the user-specific
paths will not usually work without further commandline tweaking
configuration.  Removal of the tools works with `pip` as well:

```
$ pip3 uninstall hid-tools
```

# Debugging tools for users

## hid-recorder

`hid-recorder` prints the HID Report Descriptor from a `/dev/hidraw` device
node and any HID reports coming from that device. The output format can be
used with `hid-replay` for debugging. When run without any arguments, the
tool prints a list of available devices.

```
$ sudo hid-recorder
```

## hid-replay

`hid-replay` takes the output from `hid-recorder` and replays it through a
virtual HID device that looks exactly like the one recorded. `hid-replay`
requires UHID support so make sure `pyudev` is installed.

```
$ sudo hid-replay recording-file.hid
```

## hid-decode

`hid-decode` takes a HID Report Descriptor and prints a human-readable
version of it. `hid-decode` takes binary report descriptors, strings of
bytes, and other formats.

```
$ hid-decode /sys/class/input/event5/device/device/report_descriptor
```

# kernel tests

The `hid-tools` repository contains a number of tests exercising the kernel
HID subsystem. The tests are not part of the `pip3` module and must be run
from the git repository. The most convenient invocation of the tests is by
simply calling `pytest`. The test suite requires UHID support so make sure
`pyudev` is installed.

```
$ git clone https://gitlab.freedesktop.org/libevdev/hid-tools
$ cd hid-tools
```

**Note** If your testing system is running X, please follow the steps
below to let X drivers ignore uhid test devices. Otherwise, the X driver
will recognize and handle the test devices, which would interfere with
the kernel tests and the running session.

```
$ sudo cp tests/91-hid-tools-uhid-test.conf /etc/X11/xorg.conf.d/
```

Restart your X server
**End of Note**

```
$ sudo pytest-3
```

See the `pytest` documentation for information on how to run a subset of
tests.

# hidtools python module

Technical limitations require that `hid-tools` ships with a Python module
called `hidtools`. This module is **not** to be used by external
applications.

**The hidtools python module does not provide any API stability guarantee.
It may change at any time**

# License

`hid-tools` is licensed under the GPLv2+.
