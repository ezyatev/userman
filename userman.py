r"""userman - simple web server management tool.

This script creates unix account, apache virtual host config for the specified domain name and MySQL database.

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


def get_salt():
    return "en2llow9w"


def get_sftp_group():
    return "sftp"


def get_apache_host_file(domain):
    return '/etc/apache2/sites-available/%s.conf' % domain


def get_user_home(kwargs):
    return '/home/%(user)s/' % kwargs


def get_domain_home(kwargs):
    return '%(domain)s/public' % kwargs


def get_random_password():
    return call_command('mkpasswd %u' % uuid.uuid4())


def get_apache_template(kwargs):
    return """
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
    """ % kwargs


def get_sql_query():
    return """
CREATE USER %(user)s;
CREATE DATABASE IF NOT EXISTS %(db)s;
GRANT ALL PRIVILEGES ON %(db)s.* TO '%(user)s'@'localhost' IDENTIFIED BY '%(password)s';
FLUSH PRIVILEGES;
"""


def get_report():
    return """
-----------------------
Completed successfully.
-----------------------
SFTP:
    Host: %(domain)s
    User: %(user)s
    Password: %(unix_password)s

MySQL:
    Host: localhost
    User: %(user)s
    Password: %(mysql_password)s
"""


def write_apache_host_file(domain, content):
    f = open(get_apache_host_file(domain), 'w')
    f.write(content)
    f.close()


def call_command(command):
    output = None
    try:
        output = subprocess.check_output(command, shell=True)
    except Exception as e:
        print("An error occurred while processing '%s' command: %s." % (command, e))
        sys.exit()
    return output.strip()


def main():
    unix_password = get_random_password()
    mysql_password = get_random_password()

    # create user
    user, domain = raw_input('Username: '), raw_input('Site domain: ')
    call_command(
        'useradd -p %(password)s %(user)s' %
        dict(
            user=user,
            password=crypt.crypt(unix_password, get_salt())
        )
    )

    # user home create
    user_home = get_user_home(dict(user=user))
    call_command('sudo mkdir -p %(user_home)s' % dict(user_home=user_home))
    call_command('chown %(user)s:%(user)s %(user_home)s' % dict(user=user, user_home=user_home))

    # domain home create
    print('Creating domain home directory...')
    domain_home = user_home + get_domain_home(dict(domain=domain))
    call_command('sudo -u %(user)s mkdir -p %(domain_home)s' % dict(user=user, domain_home=domain_home))

    # change owner of the user home to root:root
    call_command('chown root:root %(user_home)s' % dict(user_home=user_home))

    # write apache host config
    print('Apache host config writing...')
    apache_host_content = get_apache_template(
        dict(
            domain_home=domain_home,
            domain=domain,
            user=user
        )
    )
    write_apache_host_file(domain, apache_host_content)

    # enable new host
    print('New apache host enable...')
    call_command('a2ensite %(domain)s' % dict(domain=domain))

    # add user to sftp group
    print('Adding user to sftp group...')
    call_command('usermod -a -G %(group)s %(user)s' % dict(user=user, group=get_sftp_group()))

    # create mysql database
    print('Creating mysql user, database and grant permissions...')
    sql = get_sql_query() % dict(
        user=user,
        db=user,
        password=mysql_password
    )
    call_command('mysql -uroot -p -e "%(sql)s"' % dict(sql=sql))

    # report
    report = get_report() % dict(
        domain=domain,
        user=user,
        unix_password=unix_password,
        mysql_password=mysql_password
    )

    print(report)


if __name__ == '__main__':
    main()
