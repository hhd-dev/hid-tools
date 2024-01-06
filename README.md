# HID-TOOLS
hid-tools is a set of tools to interact with the kernel's HID subsystem.

It is quite useful, but its printing options are limited for emulating controller
devices.
This repository improves the printing options, with several quality of life
features.

## Installation
Run the following:
```
git clone https://github.com/hhd-dev/hid-tools
cd hid-tools

python -m venv venv
source venv/bin/activate

pip install click parse
```

## Running
You can now run hid-tools.

### Descriptors and input reports
The first step in this is identifying which devices exist
in your system with the following command.
```bash
sudo venv/bin/python hid-recorder
```

You can then dump them with:
```bash
sudo venv/bin/python hid-recorder /dev/hidraw# | tee mydevice.txt
```
Try to press all the buttons!

You can also strip the decription of events with the following:
```bash
sudo venv/bin/python hid-recorder /dev/hidraw# --strip-desc | tee mydevice.txt
```
This makes it much easier to distinguish changed values from each other.
Devices with vendor-specific descriptors result in garbled descriptions so this
should be used.

### Feature reports
Then, you should dump the device feature reports:
```bash
sudo venv/bin/python hid-feature /dev/hidraw# | tee mydevice_features.txt
```

This will only print the report data with the format `{report_id}: <hex_report>`.
You can append `--classic` to restore the old behavior.
Then, you should dump the device feature reports:
```bash
sudo venv/bin/python hid-feature --classic /dev/hidraw# | tee mydevice_features.txt
```

## Other functionality
The input and feature reports consist of most useful information that can
be gleamed from the device.
`hid-tools` also allows you to change feature report values and send output
reports.
But these tools only work well with devices that implement the hid protocol
the way it was meant to.

Modern devices communicate using commands, so the tools of this repo
can not be used for that.
Use wireshark (with `usbmon`) in linux to capture communication between
devices and manufacturer software.

Then, use `hidapi`, with either python `hid` or `hhd.controller.lib.hid`
to communicate with those devices.
Python package `hidapi` was found to be buggy.

# License
`hid-tools` is licensed under the GPLv2+.

# Credits
This repo is forked from the awesome hid-tools library by Benjamin Tissoires.
You can now find it in gitlab under here.
https://gitlab.freedesktop.org/bentiss/hid-tools
