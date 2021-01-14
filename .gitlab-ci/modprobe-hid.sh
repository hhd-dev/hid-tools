#!/bin/bash -x
#
# modprobe all hid kernel modules

kver=$(uname -r)

pushd /lib/modules/$kver/kernel/drivers/hid
modprobe --all $(ls hid-*.ko* | sed -e 's|\.ko.*||')
popd
