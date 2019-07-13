#!/usr/bin/python3

import os
import re
import argparse
import subprocess
from io import StringIO


class ImageBuilder:

    def __init__(self):
        userName = os.environ.get('SUDO_USER')
        if userName is None:
            userName = os.environ.get('USER')

        parser = argparse.ArgumentParser(
            description='Create a bootable Pi image')
        parser.add_argument(
            '--hostname', type=str, required=True,
            help='Name of the host')
        parser.add_argument(
            '--image', type=str, required=True,
            help='Path to input image file')
        parser.add_argument(
            '--user', type=str, default=userName,
            help='Name of the user to create, defaults to SUDO_USER')
        parser.add_argument(
            '--netroot', type=str, default=None,
            help='Build image designed to PXIE mount from NFS location')
        parser.add_argument(
            '--debug', dest='debug', action='store_true',
            help='Add debugging output')
        parser.set_defaults(debug=False)

        self.args = parser.parse_args()
        if self.args.debug:
            print(f"{self.args.user}")
            print(f"{self.args.hostname}")
            print(f"{self.args.image}")
            print(f"{self.args.netroot}")
            print(f"{self.args.debug}")

    def shell(self, arglist, expect=None):
        if self.args.debug:
            print(f"SHELL: {arglist}")

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
                print(f"|-- stdout> {line.rstrip()}")
            for line in StringIO(rtn['stderr']).readlines():
                print(f"|-- stdout> {line.rstrip()}")

        if expect is not None and expect != process.returncode:
            raise Exception(
                f"Command '{' '.join(arglist)}' failed, " +
                f"returned {rtn['rtn']}: {rtn['stderr']}")

        return rtn

    def mount(self, fstype, mountpoint):
        rtn = self.shell(
            [
                'fdisk', '-b', '512', '-o', 'type,size,start', '-l',
                '--bytes', self.args.image
            ], 0)

        offset = -1
        for line in StringIO(rtn['stdout']).readlines():
            if line.startswith(fstype):
                match = re.search(r'(\d+)\s+(\d+)$', line)
                size = match.group(1)
                offset = 512*int(match.group(2))
        if -1 == offset:
            raise Exception("Couldn't find file system {fs} in {image}".format(
                fs=fstype, image=self.args.image))

        self.shell(['mkdir', '-p', mountpoint], 0)
        self.shell(
            [
                'mount', '-v', '-o',
                'offset='+str(offset)+',sizelimit='+size,
                self.args.image, mountpoint
            ], 0)

    def execute(self):
        mount_root = '/tmp/build-root'
        mount_boot = '/tmp/build-boot'

        # Mount the two default partitions
        self.mount("W95 FAT32", mount_boot)
        self.mount("Linux", mount_root)

        # Establish an image that can boot over the network
        if self.args.netroot is not None:
            # Move boot information from the boot partition to the image
            mount_boot_new = mount_root+'/boot'
            self.shell(['rm', '-rf', mount_boot_new], 0)
            self.shell(['cp', '-R', mount_boot, mount_boot_new], 0)
            mount_boot = mount_boot_new

            # TODO: Should we add 'program_usb_boot_mode=1'
            # to /boot/config.txt?

            # Don't try to mount the SD card
            self.shell(
                [
                    'cp', mount_root+'/etc/fstab',
                    mount_root+'/etc/fstab.orig'
                ], 0)
            rtn = self.shell(
                [
                    'grep', '-v', '^PARTUUID',
                    mount_root+'/etc/fstab.orig'
                ], 0)
            with open(mount_root+'/etc/fstab', "w") as outfile:
                outfile.write(rtn['stdout'])

            # Update the boot parameters
            with open(mount_boot+'/cmdline.txt', "w") as outfile:
                outfile.write(
                    r'selinux=0 dwc_otg.lpm_enable=0 console=tty1 ' +
                    f'rootwait rw nfsroot={self.args.netroot} ip=dhcp ' +
                    r'root=/dev/nfs elevator=deadline'
                )

        # Setup ssh user
        user_home = "/home/" + self.args.user + "/.ssh"
        if not os.path.isdir(user_home):
            raise Exception(
                f"Path '{user_home}' does not exist. " +
                r"Check that this user has an ssh keypair")
        pi_home = mount_root + "/home/pi"
        if not os.path.isdir(pi_home):
            raise Exception(f"Path '{pi_home}' does not exist")

        # Copy the user's ssh pub key to 'pi's authorized keys
        self.shell(['mkdir', '-p', pi_home+"/.ssh"], 0)
        self.shell(
            [
                'bash', '-c',
                f'cat {user_home}/id_rsa.pub >> {pi_home}/.ssh/authorized_keys'
            ], 0)
        self.shell(['chmod', '600', pi_home+"/.ssh/authorized_keys"], 0)
        self.shell(['chown', '--reference', pi_home, '-R', pi_home+'/.ssh'], 0)

        # Enable ssh on the pi
        self.shell(
            [
                'bash', '-c',
                f'echo {self.args.hostname} > {mount_root}/etc/hostname'
            ], 0)
        self.shell(['touch', mount_boot+'/ssh'], 0)


if __name__ == "__main__":
    ImageBuilder().execute()
