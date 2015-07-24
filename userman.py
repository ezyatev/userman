r"""userman - simple web server management tool.

This script creates UNIX account, apache virtual host config for the specified domain name and MySQL database.

Principles are:
    1. One domain per user.
    2. User can only log in via sftp and only in the own home directory. It is necessary to create the sftp user group.
    3. Separated database for the user.

Possible sshd_config file settings:
    Subsystem sftp internal-sftp
    Match Group sftp
        ChrootDirectory %h
        ForceCommand internal-sftp
        AllowTcpForwarding no
"""

import subprocess
import uuid
import sys
import crypt

USER_HOME = '/home/%(user)s/'
DOMAIN_HOME = '%(domain)s/public'
SFTP_USER_GROUP = 'sftp'
PASSWORD_SALT = 'en2llow9w'

APACHE_HOST_FILE = '/etc/apache2/sites-available/%(domain)s.conf'
APACHE_HOST_CONTENT = """
<VirtualHost *:80>
    ServerName %(domain)s
    ServerAlias www.%(domain)s
    ServerAdmin webmaster@%(domain)s

    AssignUserId %(user)s %(user)s

    DocumentRoot "%(domain_home)s"

    <Directory "%(domain_home)s">
        AllowOverride all
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/%(domain)s.error.log
    CustomLog ${APACHE_LOG_DIR}/%(domain)s.access.log combined
</VirtualHost>
"""

SQL_QUERY = """
CREATE USER %(user)s;
CREATE DATABASE IF NOT EXISTS %(db)s;
GRANT ALL PRIVILEGES ON %(db)s.* TO '%(user)s'@'localhost' IDENTIFIED BY '%(password)s';
FLUSH PRIVILEGES;
"""

CREDENTIALS = """
-------------------------------------------
%(domain)s credentials:
-------------------------------------------
SFTP:
    Host: %(domain)s
    User: %(user)s
    Password: %(unix_password)s

MySQL:
    Host: localhost
    User: %(user)s
    Password: %(mysql_password)s
"""


def random_password():
    return call('mkpasswd %u' % uuid.uuid4())


def write_apache_host(domain, content):
    f = open(APACHE_HOST_FILE % dict(domain=domain), 'w')
    f.write(content)
    f.close()


def call(command):
    output = None
    try:
        output = subprocess.check_output(command, shell=True)
    except Exception as e:
        print("An error occurred while processing '%s' command: %s." % (command, e))
        sys.exit()
    return output.strip()


def main():
    unix_password, mysql_password = random_password(), random_password()

    # create user
    user, domain = raw_input('Username: '), raw_input('Site domain: ')
    call(
        'useradd -p %(password)s %(user)s' %
        dict(
            user=user,
            password=crypt.crypt(unix_password, PASSWORD_SALT)
        )
    )

    # user home create
    user_home = USER_HOME % dict(user=user)
    call('sudo mkdir -p %(user_home)s' % dict(user_home=user_home))
    call('chown %(user)s:%(user)s %(user_home)s' % dict(user=user, user_home=user_home))

    # domain home create
    print('Creating domain home directory...')
    domain_home = user_home + DOMAIN_HOME % dict(domain=domain)
    call('sudo -u %(user)s mkdir -p %(domain_home)s' % dict(user=user, domain_home=domain_home))

    # change owner of the user home to root:root
    call('chown root:root %(user_home)s' % dict(user_home=user_home))

    # write apache host config
    print('Apache host config writing...')
    apache_host_content = APACHE_HOST_CONTENT % dict(
        domain_home=domain_home,
        domain=domain,
        user=user
    )
    write_apache_host(domain, apache_host_content)

    # enable new host
    print('New apache host enable...')
    call('a2ensite %(domain)s' % dict(domain=domain))

    # add user to sftp group
    print('Adding user to sftp group...')
    call('usermod -a -G %(group)s %(user)s' % dict(user=user, group=SFTP_USER_GROUP))

    # create mysql database
    print('Creating mysql user, database and grant permissions...')
    sql = SQL_QUERY % dict(
        user=user,
        db=user,
        password=mysql_password
    )
    call('mysql -uroot -p -e "%(sql)s"' % dict(sql=sql))

    # report
    report = CREDENTIALS % dict(
        domain=domain,
        user=user,
        unix_password=unix_password,
        mysql_password=mysql_password
    )

    print(report)


if __name__ == '__main__':
    main()
