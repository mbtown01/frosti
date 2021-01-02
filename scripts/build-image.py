#!/usr/bin/python3

import os
import stat
import argparse
import subprocess
from io import StringIO


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

    def finalize_partitions(self):
        rootSize, totalSize = 3002, '100%'
        localDevice = '/dev/mmcblk0'

        # Resize the original root file system to ~4GB
        self.shell(['parted', localDevice, 'resizepart', '2', rootSize])

        # Create a new partition at the end of the root partition to be our
        # R/W partition later
        self.shell(['sudo' 'parted', 'mkpart', 'primary',
                    'ext4', rootSize, totalSize])

        # Format the new file system to ext4
        self.shell(['sudo', 'mkfs.ext4', '-F', f"{localDevice}p3"])

        # TODO: STill neeed to mount this and add it to fstab

    def build_image(self):
        # Simply make a copy of the original image
        self.shell(['dd', f'if={self.args.input}', f'of={self.args.output}',
                    'bs=1M'])

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
        # mount_data = '/tmp/frosti-data'

        self.build_image()

        self.mount(1, mount_boot)
        self.mount(2, mount_root)
        # self.mount(3, mount_data)

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

        self.shell(['sudo', 'cp', 'scripts/setup.sh', f"{mount_root}/etc"])
        self.shell(['sudo', 'chmod', '755', f"{mount_root}/etc/setup.sh"])

        def modFile(fileName: str, modifier, permissions: str = '755'):
            tmpFile = '/tmp/modfile'
            with open(fileName, "r") as f:
                contents = f.readlines()

            modifier(contents)
            with open(tmpFile, "w") as f:
                f.writelines(contents)

            self.shell(['sudo', 'cp', tmpFile, fileName])
            if permissions is not None:
                self.shell(['sudo', 'chmod', permissions, fileName])

        setupArgs = ''
        if self.args.wifi is not None:
            ssid, passphrase = self.args.wifi.split('/')
            setupArgs = \
                f"'--wait 90 --ssid={ssid}' '--passphrase={passphrase}'"
        setupCmd = f"/etc/setup.sh {setupArgs} || exit 1"

        modFile(
            f"{mount_root}/etc/rc.local",
            lambda contents: contents.insert(-1, f"{setupCmd} &\n"),
            permissions=700)

        def modCmndline(contents):
            contents[0] = contents[0].replace(
                ' init=/usr/lib/raspi-config/init_resize.sh',
                ' fastboot noswap ro')

        modFile(f"{mount_boot}/cmdline.txt", modCmndline)

        self.shell(['sudo', 'touch', mount_boot+'/ssh'])
        self.shell(['sudo', 'umount', mount_root, mount_boot])


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
        '--wifi', type=str, default=None,
        help='WIFI credentials as "ssid/passphrase"')
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    ImageBuilder(args).execute()
