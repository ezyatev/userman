r"""Configuration file for the Django Nginx plugin.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"

VIRTUAL_HOST_FILE = '/etc/nginx/sites-available/%(domain)s'
UWSGI_APP_FILE = '/etc/uwsgi/apps-available/%(project)s.ini'
