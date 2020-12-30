#!/usr/bin/python3

import os
import stat
import re
import argparse
import subprocess
from io import StringIO


"""
Some testing I did...

zz_orig=2020-12-02-raspios-buster-armhf-lite.img
zz_image=test.img

dd if=/dev/zero of=${zz_image} bs=4096k count=1k
dd if=${zz_orig} of=${zz_image} bs=1M conv=notrunc
sudo parted ${zz_image}
resizepart 2 4000
mkpart extended 4000 4096
quit


"""


class ImageBuilder:

    def __init__(self, args):
        self.args = args

    def shell(self, arglist, expect=0):
        arglist = list(str(a) for a in arglist)
        if self.args.debug:
            argsAsStrings = list(f"'{a}'" for a in arglist)
            print(f"SHELL: {' '.join(argsAsStrings)}")

        process = subprocess.Popen(
            arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o, e = process.communicate()
        rtn = {
            'stdout': o.decode('ascii'),
            'stderr': e.decode('ascii'),
            'rtn': process.returncode
        }

        if self.args.debug:
            for line in StringIO(rtn['stdout']).readlines():
                print(f"> {line.rstrip()}")
            for line in StringIO(rtn['stderr']).readlines():
                print(f"!!! {line.rstrip()}")

        if expect is not None and expect != process.returncode:
            raise Exception(
                f"Command '{' '.join(arglist)}' failed, " +
                f"returned {rtn['rtn']}: {rtn['stderr']}")

        return rtn

    def build_device_map(self):
        rtn = self.shell([
            'fdisk', '-b', '512', '-o', 'device,size,start,end', '-l',
            '--bytes', self.args.output
        ])

        offset = -1
        deviceMap = dict()
        for line in StringIO(rtn['stdout']).readlines():
            if line.startswith(self.args.output):
                name, size, offset, end = line.split()
                deviceMap[name[-1]] = \
                    (name, int(size), int(offset)*512, int(end)*512)

        return deviceMap

    def build_image(self):
        # Create the base image with a larger size
        self.shell(['dd', 'if=/dev/zero', f'of={self.args.output}', 'bs=1M',
                    'count=4096'])

        # Bring the original image into the front of the new image
        self.shell(['dd', f'if={self.args.input}', f'of={self.args.output}',
                    'bs=4096k', 'conv=notrunc'])

        # Resize the original root file system to ~4GB
        self.shell(['parted', self.args.output, 'resizepart', '2', '4000'])

        # Create a new partition at the end of the root partition to be our
        # R/W partition later
        self.shell(['parted', self.args.output,
                    'mkpart', 'primary', 'ext4', '4000', '4096'])

        deviceMap = self.build_device_map()
        deviceInfo = deviceMap.get('3')
        if deviceInfo is None:
            raise Exception(
                f"Couldn't find the new device in {self.args.output}")

        name, size, offset, end = deviceInfo

        # This is overly complete, but we'll for sure get the next available
        # loop device by seeing which ones already exist and taking the
        # next available
        loopFileList = list(f"/dev/loop{i}" for i in range(21, 50))
        loopDevList = list()
        for loopFile in loopFileList:
            try:
                if not stat.S_ISBLK(os.stat(loopFile).st_mode):
                    loopDevList.append(loopFile)
            except:
                loopDevList.append(loopFile)

        if not len(loopDevList):
            raise RuntimeError(
                "For some reason, there are no /dev/loop devices available")

        # Loopback the new partition and create the file system
        loopDev = loopDevList[0]
        self.shell(['sudo', 'losetup', '-o', str(offset), '--sizelimit',
                    size, loopDev, self.args.output])
        self.shell(['sudo', 'mkfs.ext4', '-F', loopDev])
        self.shell(['sudo', 'losetup', '-d', loopDev])
        # self.shell(['sudo', 'rm', loopDev]

    def mount(self, device: str, mountpoint: str):
        deviceMap = self.build_device_map()
        deviceInfo = deviceMap.get(str(device))
        if deviceInfo is None:
            raise Exception(
                f"Couldn't find device {device} in {self.args.output}")

        name, size, offset, end = deviceInfo
        self.shell(['sudo', 'mkdir', '-p', mountpoint])
        self.shell(['sudo', 'mount', '-v', '-o',
                    f'offset={offset},sizelimit={size}',
                    self.args.output, mountpoint])

    def execute(self):
        mount_root = '/tmp/frosti-root'
        mount_boot = '/tmp/frosti-boot'
        mount_data = '/tmp/frosti-data'

        # self.build_image()

        self.mount(1, mount_boot)
        self.mount(2, mount_root)
        self.mount(3, mount_data)

        return

        # If the current user has an id_rsa.pub file, use it
        id_rsa_file = os.path.expanduser("~/.ssh/id_rsa.pub")
        if os.path.isfile(id_rsa_file):
            pi_home = mount_root + "/home/pi"
            if not os.path.isdir(pi_home):
                raise Exception(f"Path '{pi_home}' does not exist")

            # Copy the user's ssh pub key to 'pi's authorized keys
            self.shell(['mkdir', '-p', pi_home+"/.ssh"])
            self.shell(['bash', '-c',
                        f'cat {id_rsa_file} >> {pi_home}/.ssh/authorized_keys'])
            self.shell(['chmod', '600', f"{pi_home}/.ssh/authorized_keys"])
            self.shell(['chown', '--reference',
                        pi_home, '-R', pi_home+'/.ssh'])

        # if self.args.ssid is not None:
        #     with open(mount_boot+'/wpa_supplicant.conf', "w") as outfile:
        #         outfile.write(
        #             'country=US\n'
        #             'ctrl_interface=DIR=/var/run/wpa_supplicant '
        #             'GROUP=netdev\n'
        #             'update_config=1\n\n'
        #             'network={\n'
        #             f'    ssid="{self.args.ssid}"\n'
        #             f'    psk="{self.args.passwd}"\n'
        #             '    key_mgmt=WPA-PSK\n'
        #             '}\n'
        #         )

        # # Enable ssh on the pi
        # if self.args.hostname is not None:
        #     self.shell([
        #         'bash', '-c',
        #         f'echo {self.args.hostname} > {mount_root}/etc/hostname'
        #     ])

        self.shell(['sudo', 'cp', 'scripts/setup.sh', f"{mount_root}/etc"])
        self.shell(['sudo', 'chmod', '755', f"{mount_root}/etc/setup.sh"])

        rcLocalFile = f"{mount_root}/etc/rc.local"
        with open(rcLocalFile, "r") as f:
            contents = f.readlines()

        contents.insert(-1, '/etc/setup.sh || exit 1\n')
        with open('/tmp/rc.local', "w") as f:
            f.writelines(contents)

        self.shell(['sudo', 'cp', '/tmp/rc.local', f"{mount_root}/etc"])
        self.shell(['sudo', 'chmod', '755', f"{mount_root}/etc/rc.local"])
        self.shell(['sudo', 'touch', mount_boot+'/ssh'])
        self.shell(['sudo', 'umount', mount_root, mount_boot, mount_data])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create a bootable Pi image')
    parser.add_argument(
        '--hostname', type=str, default=None,
        help='Name of the host')
    parser.add_argument(
        '--input', type=str, required=True,
        help='Path to the input image file')
    parser.add_argument(
        '--output', type=str, required=True, default='output.img',
        help='Path to the output file')
    parser.add_argument(
        '--user', type=str, default=None,
        help='Name of the user to create')
    parser.add_argument(
        '--debug', dest='debug', action='store_true',
        help='Add debugging output')
    parser.add_argument(
        '--ssid', type=str, default=None,
        help='SSID of a wifi network to add')
    parser.add_argument(
        '--passwd', type=str, default=None,
        help='Password of a wifi network to add')
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    ImageBuilder(args).execute()
