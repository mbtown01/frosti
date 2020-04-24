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
            '--down', action='store_true', default=False,
            help='Stops all containers related to rpt')
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

    def run(
            self,
            name: str,
            runArgList: list=[],
            arglist: list=[],
            restart: bool=False):

        self.shell(arglist=[
            'bash', '-c', f'FOO=$(docker ps '
            f'--filter name={name} --format "{{{{.ID}}}}");'
            f'if [ "$FOO" != "" ]; then docker kill $FOO; fi'
        ])

        if restart:
            containerExists = not self.shell(
                ['bash', '-c', f'docker ps --all | grep {name}; exit $?'])
            if containerExists:
                return self.shell(arglist=['docker', 'restart', name])
        else:
            self.shell(arglist=[
                'bash', '-c', f'FOO=$(docker ps --all '
                f'--filter name={name} --format "{{{{.ID}}}}");'
                f'if [ "$FOO" != "" ]; then docker rm $FOO; fi'
            ])

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
            runArgList = ['-p', '3001:3001', '-p', '5000:5000']
            arglist = [
                'python3', '-m', 'ptvsd',
                '--host', '0.0.0.0', '--port', '3001', '--wait', '-m', 'src'
            ] + self.args.debug
            return self.run(
                name="rpt-debug", runArgList=runArgList, arglist=arglist)

        if self.args.run is not None:
            arglist = ['python3', '-m', 'src'] + self.args.run
            return self.run(name="rpt-run", arglist=arglist)

        if self.args.dev:
            runArgList = ['-p', '5000:5000']
            arglist = ['bash', '-c', 'while sleep 60; do /bin/false; done']
            return self.run(
                name="rpt-dev", runArgList=runArgList,
                arglist=arglist, restart=True)

        if self.args.down:
            arglist = self.baseComposeArgs + ['down']
            return self.shell(arglist=arglist)


if __name__ == "__main__":
    RptLauncher().execute()
