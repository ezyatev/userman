from __future__ import absolute_import

r"""Django Nginx plugin.

Creates uWSGI and nginx config for the Django project.

"""

import textwrap
from userman import Userman
from . import settings, templates
from validators import User, DomainName, ProjectName

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"


class DjangoNginx(Userman):
    def __init__(self):
        super(DjangoNginx, self).__init__()
        self.domain = self.get_domain()
        self.user = self.get_user()
        self.project = self.get_project()

    @staticmethod
    def get_user():
        user = raw_input('WSGI process uid: ')
        if User.validate(user):
            return user

    @staticmethod
    def get_domain():
        domain = raw_input('Domain name: ')
        if DomainName.validate(domain):
            return domain

    @staticmethod
    def get_project():
        project = raw_input('Project name: ')
        if ProjectName.validate(project):
            return project

    def __write_nginx_config(self):
        config_file = settings.VIRTUAL_HOST_FILE % dict(domain=self.domain)
        content = templates.VIRTUAL_HOST % dict(
            domain=self.domain,
            project=self.project,
            user=self.user
        )
        content = textwrap.dedent(content)

        f = open(config_file, 'w')
        f.write(content)
        f.close()

        self.report("Nginx config file created: %(config_file)s\n", config_file=config_file)

    def __write_uwsgi_config(self):
        config_file = settings.UWSGI_APP_FILE % dict(project=self.project)
        content = templates.UWSGI_APP % dict(
            project=self.project,
            user=self.user
        )
        content = textwrap.dedent(content)

        f = open(config_file, 'w')
        f.write(content)
        f.close()

        self.report("uWSGI config file created: %(config_file)s\n", config_file=config_file)

    def __enable_uwsgi_app(self):
        config_file = settings.UWSGI_APP_FILE % dict(project=self.project)
        symlink = settings.UWSGI_APP_SYMLINK % dict(project=self.project)
        self.call('ln -s %(config_file)s %(symlink)s' % dict(config_file=config_file, symlink=symlink))
        self.report("Project %(project)s enabled.\n", project=self.project)

    def __enable_nginx_host(self):
        config_file = settings.VIRTUAL_HOST_FILE % dict(domain=self.domain)
        symlink = settings.VIRTUAL_HOST_SYMLINK % dict(domain=self.domain)
        self.call('ln -s %(config_file)s %(symlink)s' % dict(config_file=config_file, symlink=symlink))
        self.report("Host %(domain)s enabled.\n", domain=self.domain)

    def __restart_nginx(self):
        self.call('service nginx restart')
        self.report("nginx service restarted.\n")

    def __final_words(self):
        self.report("[!] Please create virtualenv in the user's home dir, install Django and restart uWSGI service.\n")

    def process(self):
        self.__write_nginx_config()
        self.__write_uwsgi_config()
        self.__enable_uwsgi_app()
        self.__enable_nginx_host()
        self.__restart_nginx()
        self.__final_words()
