from __future__ import absolute_import

r"""Apache Host plugin.

Creates Apache virtual host config file for the specified domain name.

"""

import textwrap
import os

from userman import Userman
from . import settings, templates
from validators import DomainName, User

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"


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
        config_file = settings.VIRTUAL_HOST_FILE % dict(domain=self.domain)
        content = templates.VIRTUAL_HOST % dict(
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
