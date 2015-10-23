r"""Configuration file for the MySQL Database plugin.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"

SQL_QUERY = (
    """
    CREATE USER %(user)s;
    CREATE DATABASE IF NOT EXISTS %(db)s;
    GRANT ALL PRIVILEGES ON %(db)s.* TO '%(user)s'@'localhost' IDENTIFIED BY '%(password)s';
    FLUSH PRIVILEGES;
    """
)
