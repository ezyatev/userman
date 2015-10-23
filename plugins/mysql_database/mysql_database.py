from __future__ import absolute_import

r"""MySQL Database plugin.

Creates MySQL user and database.

"""

import textwrap

from userman import Userman
from . import settings, templates
from validators import DBName, User

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"


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

        self.report(templates.CREDENTIALS, **kwargs)
