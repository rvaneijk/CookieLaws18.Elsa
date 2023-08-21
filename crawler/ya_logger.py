# yet another logger :)
# (possibly swith with python's own, or some 3rd party library)
from __future__ import absolute_import, division, print_function
from sys import stderr
# import logging
from colorama import Fore, Back, Style  # pip


class Logger:

    def __init__(self, logfile, console):
        self.logfile = open(logfile, "a") if type(logfile) is str else logfile
        self.console = console

    def log(self, text):
        if self.console:
            print(Fore.GREEN, "\n\n", text, "\n\n", Style.RESET_ALL, file=stderr)
            stderr.flush()
        self.logfile.write(text + "\n")
        self.logfile.flush()
