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
            help='Run entire rpt orchestration')
        parser.add_argument(
            '--debug', nargs=argparse.REMAINDER,
            help='Run rpt in debug mode')
        parser.add_argument(
            '--test', nargs=argparse.REMAINDER,
            help='Run a test command inside the container')
        parser.add_argument(
            '--dev', action='store_true', default=False,
            help='Start a development container to be attached to')

        self.args = parser.parse_args()

        uname = check_output(['uname', '-m']).decode('UTF-8').rstrip()
        hosttype = self.ALL_HOSTTYPES.get(uname)
        if hosttype is None:
            raise Exception(f"Host with uname {uname} is not supported")

        timezone = check_output(
            ['readlink', '/etc/localtime']).decode('UTF-8').rstrip()
        self.timezone = timezone[(timezone.find("/zoneinfo/")+10):]

        self.baseComposeArgs = [
            'docker-compose',
            '--file', 'docker/docker-compose.yaml',
            '--env-file', f"docker/docker-hosttype-{hosttype}.env"
        ]

    def shell(self, arglist):
        print(f"SHELL: {arglist}")
        return call(arglist)

    def run(self, name: str, runArgList: list=[], arglist: list=[]):
        containerIsRunning = not self.shell(
            ['bash', '-c', f'docker ps | grep {name}; exit $?'])
        if containerIsRunning:
            return 0

        containerExists = not self.shell(
            ['bash', '-c', f'docker ps --all | grep {name}; exit $?'])
        if containerExists:
            return self.shell(arglist=['docker', 'restart', name])

        args = self.baseComposeArgs + \
            ['run', '--name', name, '-e', f'TZ={self.timezone}']
        if len(runArgList):
            args = args + runArgList
        args = args + ['rpt'] + arglist

        return self.shell(arglist=args)

    def execute(self):
        if self.args.test is not None:
            return self.run(name="rpt-test", arglist=self.args.test)

        if self.args.build is not None:
            arglist = self.baseComposeArgs + \
                ['build'] + self.args.build + ['rpt']
            return self.shell(arglist=arglist)

        if self.args.debug is not None:
            # run -p 3001:3001 -p 5000:5000 \
            # rpt python3.7 -m ptvsd --host 0.0.0.0 --port 3001 --wait \
            #     -m src --hardware v2

            runArgList = ['-p', '3001:3001', '-p', '5000:5000']
            arglist = [
                'python3', '-m', 'ptvsd',
                '--host', '0.0.0.0', '--port', '3001', '--wait',
                '-m', 'src'
            ] + self.args.debug
            return self.run(
                name="rpt-debug", runArgList=runArgList, arglist=arglist)

        if self.args.run is not None:
            arglist = ['python3', '-m', 'src'] + self.args.run
            return self.run(name="rpt-run", arglist=arglist)

        if self.args.dev is not None:
            arglist = ['bash', '-c', 'while sleep 60; do /bin/false; done']
            return self.run(name="rpt-dev", arglist=arglist)

        # if self.args.dev:
        #     arglist = baseComposeArgs + baseRunArgs + \
        #         ['bash', '-c', 'while sleep 600; do /bin/false; done']
        #     rtn = self.shell(arglist=arglist)
        #     if 1 == rtn:
        #         print("WARNING: rpt-dev may exist, attempting restasrt")
        #         arglist = ['docker', 'restart', 'rpt-dev']
        #         return self.shell(arglist=arglist)


if __name__ == "__main__":
    RptLauncher().execute()
