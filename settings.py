r"""settings - configuration file for the userman utility.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "eu@f1dev.com"

USER_HOME = '/home/%(user)s'
DOCUMENT_ROOT = '%(domain)s/public'
SFTP_GROUP = 'sftp'
PASSWORD_SALT = 'en2llow9w'

APACHE_HOST_FILE = '/etc/apache2/sites-available/%(domain)s.conf'
APACHE_HOST_CONTENT = (
    """
    <VirtualHost *:80>
        ServerName %(domain)s
        ServerAlias www.%(domain)s
        ServerAdmin webmaster@%(domain)s

        AssignUserId %(user)s %(user)s

        DocumentRoot "%(document_root)s"

        <Directory "%(document_root)s">
            AllowOverride all
            Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/%(domain)s.error.log
        CustomLog ${APACHE_LOG_DIR}/%(domain)s.access.log combined
    </VirtualHost>
    """
)

SQL_QUERY = (
    """
    CREATE USER %(user)s;
    CREATE DATABASE IF NOT EXISTS %(db)s;
    GRANT ALL PRIVILEGES ON %(db)s.* TO '%(user)s'@'localhost' IDENTIFIED BY '%(password)s';
    FLUSH PRIVILEGES;
    """
)
