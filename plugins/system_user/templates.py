r"""Templates file for the System User plugin.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "eu@f1dev.com"

CREDENTIALS = (
    """
    System user credentials:
    ------------------------
    User: %(user)s
    Password: %(password)s
    Home dir: %(user_home)s
    """
)
