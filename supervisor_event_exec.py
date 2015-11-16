#!/usr/bin/env python
from __future__ import print_function
import shlex
import subprocess
import sys
try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

from supervisor import childutils
from supervisor.options import make_namespec
from supervisor.states import ProcessStates


class SupervisorEventExec(object):
    def __init__(self, rpc, command, restart_programs, restart_any_program):
        self.rpc = rpc
        self.command = command
        self.restart_programs = restart_programs
        self.restart_any_program = restart_any_program
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def _restart_processes(self):
        try:
            specs = self.rpc.supervisor.getAllProcessInfo()
        except Exception as e:
            print("Unable to get process info: {}. No action taken.".format(e), file=self.stderr)
        else:
            waiting = set(self.restart_programs)
            for spec in specs:
                name = spec["name"]
                namespec = make_namespec(spec["group"], name)
                if self.restart_any_program or name in waiting or namespec in waiting:
                    if spec["state"] is ProcessStates.RUNNING:
                        print("Restarting process: {}.".format(namespec), file=self.stderr)
                        try:
                            self.rpc.supervisor.stopProcess(namespec)
                        except xmlrpclib.Fault as e:
                            print("Unable to stop process {}: {}.".format(namespec, e), file=self.stderr)
                        try:
                            self.rpc.supervisor.startProcess(namespec)
                        except xmlrpclib.Fault as e:
                            print("Unable to start process {}: {}.".format(namespec, e), file=self.stderr)
                        else:
                            print("Restarted process {}.".format(namespec), file=self.stderr)
                    else:
                        print("Process {} is not in RUNNING state. No action taken.".format(namespec))
                    waiting.discard(name)
                    waiting.discard(namespec)
            if len(waiting) > 0:
                print("Programs specified could not be found: {}.".format(", ".join(waiting)), file=self.stderr)

    def runforever(self):
        while True:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            print("Executing command: {}.".format(self.command), file=self.stderr)
            exit_status = subprocess.Popen(self.command, shell=True).wait()
            if exit_status != 0 and (len(self.restart_programs) > 0 or self.restart_any_program):
                print("The command exit status was non-zero, restarting processes.", file=self.stderr)
                self._restart_processes()
            childutils.listener.ok(self.stdout)


def main():
    import argparse
    import os
    parser = argparse.ArgumentParser("supervisor-event-exec")
    parser.add_argument("-e", "--execute", metavar="COMMAND", dest="command", required=True,
                        help="Command or script to execute on supervisor events.")
    parser.add_argument("-p", "--restart-programs", type=str, nargs="*", metavar="PROGRAM",
                        help="Supervisor process name/s to be restarted on non-zero exit status if in RUNNING state.")
    parser.add_argument("-a", "--restart-any-program", action="store_true",
                        help="Restart any supervisor processes in RUNNING state on non-zero exit status.")
    args = parser.parse_args()

    try:
        rpc = childutils.getRPCInterface(os.environ)
    except KeyError as e:
        if e.args[0] == "SUPERVISOR_SERVER_URL":
            print("supervisor-event-exec must be run as a supervisor event listener.", file=sys.stderr)
            sys.exit(1)
        else:
            raise

    event_exec = SupervisorEventExec(rpc, args.command, args.restart_programs, args.restart_any_program)
    event_exec.runforever()


if __name__ == "__main__":
    main()
