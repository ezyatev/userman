#!/usr/bin/env python

r"""Simple web server management tool.

This script creates UNIX account, apache virtual host config for the specified domain name and MySQL database.
Tested with Apache/2.4+ on Debian 8 only.

usage: python userman.py [options]


Available options:
    --system - create UNIX account
    --apache - create apache virtual host config for the specified domain name
    --mysql - create MySQL user and database
    --django-nginx - create Virtualenv, uWSGI and nginx config for the Django project


Principles are:
    1. One domain per user.
    2. User can only log in via sftp and only in the own home directory. It is necessary to create the sftp user group.
    3. Separated database for the user.


Possible sshd_config file settings:
    Subsystem sftp internal-sftp
        Match Group sftp
        ChrootDirectory %h
        ForceCommand internal-sftp
        AllowTcpForwarding no

"""
from __future__ import absolute_import
import uuid
import sys
import textwrap
import os
import subprocess
import errno
from collections import OrderedDict

import plugins

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "eu@f1dev.com"

sys.tracebacklimit = 0


class Userman(object):
    def random_password(self):
        return self.call('mkpasswd %u' % uuid.uuid4())

    @staticmethod
    def call(command):
        output = None
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print("An error occurred while processing '%s' command." % command)
            sys.exit(e.returncode)
        return output.strip()

    def process(self):
        return NotImplementedError('You should to implement the process method.')

    @staticmethod
    def report(message, **kwargs):
        print(textwrap.dedent(message) % kwargs)


def main():
    if not os.geteuid() == 0:
        print('Script must be run as root')
        sys.exit(errno.EACCES)

    extensions = OrderedDict(
        (
            ('--system', plugins.system_user.SystemUser),
            ('--apache', plugins.apache_host.ApacheHost),
            ('--mysql', plugins.mysql_database.MySQLDatabase),
            ('--django-nginx', plugins.django_nginx.DjangoNginx)
        )
    )
    for k in sys.argv[1:]:
        extension = extensions[k]()
        extension.process()


if __name__ == '__main__':
    main()
