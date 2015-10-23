from __future__ import absolute_import

r"""System User plugin.

Creates UNIX account.

"""

import crypt

from userman import Userman
from . import settings, templates
from validators import User

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"


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
        self.report(templates.CREDENTIALS, **kwargs)

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
