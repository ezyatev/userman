## Synopsis

Script for automating web site deployments on Debian.

Principles are:

* One domain per user.
* User can only log in via SFTP and only in the own home directory. It is necessary to create the SFTP user group.
* Separated database for the user.
* Separated app for the user.

## Installation

1. Clone project repo.
2. Create user group for sftp users. For example, 'sftp'.
3. Change `sshd_config` file like this:
<pre>
Subsystem sftp internal-sftp
</pre>
<pre>
Match Group sftp
ChrootDirectory %h
ForceCommand internal-sftp
AllowTcpForwarding no
</pre>
4. Change settings.py file parameters each plugin.
5. Make the script executable: `sudo chmod a+x userman.py`

## Usage

`./userman.py [options]`

Available options:
* `--system` - creates UNIX account and allows SFTP access only
* `--apache` - creates Apache virtual host config for the specified domain name
* `--mysql` - creates MySQL user and database
* `--django-nginx` - creates uWSGI and nginx config for Django project

## Notes
* You must have `apache2-mpm-itk` module installed to set owner of the PHP process.
* You must have password for the root user to use `--mysql` feature.
* You must have `uwsgi`, `uwsgi-plugin-python` and `virtualenv` installed to use `--django-nginx` feature.
* Tested with Apache/2.4+ on Debian 8 only.

## Author
Eugene Zyatev ([eu@f1dev.com](mailto:eu@f1dev.com)).