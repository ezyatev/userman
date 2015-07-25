r"""userman - simple web server management tool.

This script creates UNIX account, apache virtual host config for the specified domain name and MySQL database.

Principles are:
    1. One domain per user.
    2. User can only log in via sftp and only in the own home directory. It is necessary to create the sftp user group.
    3. Separated database for the user.
        ChrootDirectory %h
        ForceCommand internal-sftp
        AllowTcpForwarding no
"""

import uuid
import sys
import crypt
import textwrap

import settings
from validator import User, DomainName


class Base(object):
    def __init__(self):
        self.__user = None
        self.__domain = None

    @property
    def user(self):
        if not self.__user:
            string = raw_input('User: ')
            if User.validate(string):
                self.__user = string
        return self.__user

    @property
    def domain(self):
        if not self.__domain:
            string = raw_input('Domain: ')
            if DomainName.validate(string):
                self.__domain = string
        return self.__domain

    def random_password(self):
        return self.call('mkpasswd %u' % uuid.uuid4())

    def call(self, command):
        output = None
        try:
            output = command
            # output = subprocess.check_output(command, shell=True)
        except Exception as e:
            print("An error occurred while processing '%s' command: %s." % (command, e))
            sys.exit()
        return output.strip()

    def process(self):
        return NotImplementedError('You should to implement the process method.')

    def report(self, message, **kwargs):
        print(textwrap.dedent(message) % kwargs)


class SystemUser(Base):
    @property
    def __unix_password(self):
        return crypt.crypt(self.random_password(), settings.PASSWORD_SALT)

    def create(self):
        kwargs = dict(
            user=self.user,
            password=self.__unix_password,
            user_home=settings.USER_HOME % dict(user=self.user)
        )
        self.call(
            'useradd -p %(password)s %(user)s -d %(user_home)s' % kwargs
        )
        message = (
            """
            System user was successfully created.
            --------------------------------------------
            User: %(user)s
            Password: %(password)s
            Home dir: %(user_home)s
            --------------------------------------------
            """
        )
        self.report(message % kwargs)

    def add_to_group(self):
        kwargs = dict(user=self.user, group=settings.SFTP_GROUP)
        self.call('usermod -a -G %(group)s %(user)s' % kwargs)
        self.report('User %(user)s successfully added to the %(group)s group.' % kwargs)

    def process(self):
        self.create()
        self.add_to_group()


class ApacheHost(Base):
    def __init__(self):
        super(ApacheHost, self).__init__()
        print(self.domain)


class MySQLDatabase(Base):
    pass


def main():
    for entity in Base.__subclasses__():
        e = entity()
        e.process()


if __name__ == '__main__':
    main()
