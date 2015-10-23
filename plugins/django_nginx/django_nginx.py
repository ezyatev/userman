from __future__ import absolute_import

r"""Django Nginx plugin.

Creates Virtualenv, uWSGI and nginx config for the Django project.

"""

from userman import Userman
from . import settings

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"


class DjangoNginx(Userman):
    pass
