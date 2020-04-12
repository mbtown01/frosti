#!/usr/bin/env python3

import os
import sys
import re
import argparse

from subprocess import call, check_output
from threading import Thread
from io import StringIO
from queue import Queue, Empty


class RptLauncher:
    ALL_HOSTTYPES = {
        'x86_64': 'x86_64',
        'armv7l': 'arm',
        'armv6l': 'arm'
    }

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Central interface for interacting w/ rpt containers')
        parser.add_argument(
            '--build', nargs=argparse.REMAINDER,
            help='Build the rpt containers locally')
        parser.add_argument(
            '--run', nargs=argparse.REMAINDER,
            help='Run the rpt orchestration')
        parser.add_argument(
            '--dev', action='store_true', default=False,
            help='Start a development container to be attached to')
        parser.add_argument(
            '--dryrun', action='store_true', default=False,
            help='Only print commands, do not execute')
        parser.add_argument(
            '--debug', action='store_true', default=False,
            help='Add debugging output')

        self.args = parser.parse_args()

    def shell(self, arglist):
        if self.args.debug:
            print(f"SHELL: {arglist}")

        if not self.args.dryrun:
            return call(arglist)

        return 0

    def execute(self):
        uname = check_output(['uname', '-m']).decode('UTF-8').rstrip()
        hosttype = self.ALL_HOSTTYPES.get(uname)
        if hosttype is None:
            raise Exception(f"Host with uname {uname} is not supported")

        baseComposeArgs = [
            'docker-compose',
            '--file', 'docker/docker-compose.yaml',
            '--env-file', f"docker/docker-hosttype-{hosttype}.env"
        ]
        rptStartArgs = ['python3', '-m', 'src']

        timezone = check_output(
            ['readlink', '/etc/localtime']).decode('UTF-8').rstrip()
        timezone = timezone[(timezone.find("/zoneinfo/")+10):]

        if self.args.run is not None:
            rptStartArgs = rptStartArgs + self.args.run
            return self.shell(
                arglist=baseComposeArgs + ['run', 'rpt'] + rptStartArgs)

        if self.args.build is not None:
            rptStartArgs = rptStartArgs + self.args.build
            return self.shell(
                arglist=baseComposeArgs + ['build', 'rpt'])

        if self.args.dev:
            # run rpt bash -c "while sleep 600; do /bin/false; done"
            rptStartArgs = \
                ['bash', '-c', 'while sleep 600; do /bin/false; done']
            return self.shell(
                arglist=baseComposeArgs + [
                    'run',
                    '--name', 'rpt-dev',
                    '-e', f'TZ={timezone}',
                    'rpt'] + rptStartArgs)


if __name__ == "__main__":
    sys.exit(RptLauncher().execute())
