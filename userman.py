#!/usr/bin/env python

r"""Simple web server management tool.

This script creates UNIX account, apache virtual host config for the specified domain name and MySQL database.
Tested with Apache/2.4+ on Debian 8 only.

usage: python userman.py [options]


Available options:
    --system - create UNIX account
    --apache - create apache virtual host config for the specified domain name
    --mysql - create MySQL user and database


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

import uuid
import sys
import crypt
import textwrap
import os
import subprocess
import errno
from collections import OrderedDict

import settings
from validator import User, DomainName, DBName

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


class SystemUser(Userman):
    def __init__(self):
        super(SystemUser, self).__init__()
        self.user = self.get_user()
        self.__password = self.random_password()
        self.__crypted_password = crypt.crypt(self.__password, settings.PASSWORD_SALT)

    @staticmethod
    def get_user():
        user = raw_input('System username: ')
        if User.validate(user):
            return user

    def __create(self):
        kwargs = dict(
            user=self.user,
            password=self.__password,
            crypted_password=self.__crypted_password,
            user_home=settings.USER_HOME % dict(user=self.user)
        )
        self.call(
            'useradd -p %(crypted_password)s %(user)s -d %(user_home)s -m' % kwargs
        )
        message = (
            """
            System user credentials:
            ------------------------
            User: %(user)s
            Password: %(password)s
            Home dir: %(user_home)s
            """
        )
        self.report(message, **kwargs)

    def __add_to_group(self):
        kwargs = dict(user=self.user, group=settings.SFTP_GROUP)
        self.call('usermod -a -G %(group)s %(user)s' % kwargs)
        self.report("User %(user)s successfully added to the %(group)s group.\n", **kwargs)

    def __change_owner(self):
        kwargs = dict(
            user_home=settings.USER_HOME % dict(user=self.user)
        )
        self.call('chown root:root %(user_home)s' % kwargs)
        self.report("Successfully changed ownership for the %(user_home)s.\n", **kwargs)

    def process(self):
        self.__create()
        self.__add_to_group()
        self.__change_owner()


class ApacheHost(Userman):
    def __init__(self):
        super(ApacheHost, self).__init__()
        self.domain = self.get_domain()
        self.user = self.get_user()
        self.__document_root = self.__get_document_root()

    @staticmethod
    def get_user():
        user = raw_input('ITK MPM username: ')
        if User.validate(user):
            return user

    @staticmethod
    def get_domain():
        domain = raw_input('Domain name: ')
        if DomainName.validate(domain):
            return domain

    def __get_document_root(self):
        return os.path.join(settings.USER_HOME, settings.DOCUMENT_ROOT) % dict(
            domain=self.domain,
            user=self.user
        )

    def __create_document_root(self):
        self.call('mkdir -p %(document_root)s' % dict(user=self.user, document_root=self.__document_root))
        self.call('cd %(user_home)s && chown -R %(user)s:%(user)s *' % dict(
            user_home=settings.USER_HOME % dict(user=self.user),
            user=self.user
        ))
        self.report("\nDomain home path created: %(document_root)s", document_root=self.__document_root)

    def __write_config(self):
        config_file = settings.APACHE_HOST_FILE % dict(domain=self.domain)
        content = settings.APACHE_HOST_CONTENT % dict(
            document_root=self.__document_root,
            domain=self.domain,
            user=self.user
        )
        content = textwrap.dedent(content)

        f = open(config_file, 'w')
        f.write(content)
        f.close()

        self.report("Config file created: %(config_file)s\n", config_file=config_file)

    def __restart_service(self):
        self.call('service apache2 restart')
        self.report("Apache service restarted.\n")

    def __enable_host(self):
        self.call('a2ensite %(domain)s' % dict(domain=self.domain))

    def process(self):
        self.__create_document_root()
        self.__write_config()
        self.__enable_host()
        self.__restart_service()


class MySQLDatabase(Userman):
    def __init__(self):
        super(MySQLDatabase, self).__init__()
        self.user = self.get_user()
        self.db = self.get_db()

    @staticmethod
    def get_user():
        user = raw_input('MySQL username: ')
        if User.validate(user):
            return user

    @staticmethod
    def get_db():
        db = raw_input('MySQL DB name: ')
        if DBName.validate(db):
            return db

    def process(self):
        kwargs = dict(
            user=self.user,
            db=self.db,
            password=self.random_password()
        )
        self.report('Please specify password for the MySQL root user.')
        sql = textwrap.dedent(settings.SQL_QUERY % kwargs)
        self.call('mysql -uroot -p -e "%(sql)s"' % dict(sql=sql))
        message = (
            """
            MySQL credentials:
            ------------------
            User: %(user)s
            Password: %(password)s
            Database: %(db)s
            Host: localhost
            """
        )
        self.report(message, **kwargs)


def main():
    if not os.geteuid() == 0:
        print('Script must be run as root')
        sys.exit(errno.EACCES)

    plugins = OrderedDict(
        ('--system', SystemUser),
        ('--apache', ApacheHost),
        ('--mysql', MySQLDatabase)
    )
    for k in sys.argv[1:] or plugins.keys():
        plugin = plugins[k]()
        plugin.process()


if __name__ == '__main__':
    main()
