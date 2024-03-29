r"""Configuration file for the Apache Host plugin.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"

USER_HOME = '/home/%(user)s'
DOCUMENT_ROOT = '%(domain)s/public'
VIRTUAL_HOST_FILE = '/etc/apache2/sites-available/%(domain)s.conf'
