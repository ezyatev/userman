## Synopsis

This script creates unix account, apache virtual host config for the specified domain name and MySQL database. 
Tested with Apache/2.4+ on Debian 8 only.

Principles are:

* One domain per user.
* User can only log in via sftp and only in the own home directory. It is necessary to create the sftp user group.
* Separated database for the user.

## Installation

1. Clone project repo.
2. Create usergroup for sftp users. For example, 'sftp'.
3. Change `sshd_config` file like this:
<pre>
Subsystem sftp internal-sftp
    Match Group sftp
    ChrootDirectory %h
    ForceCommand internal-sftp
    AllowTcpForwarding no
</pre>
4. Change settings.py file parameters.
5. Make the script executable: `sudo chmod a+x userman.py`

## Usage

`./userman.py [options]`

Available options:
* `--system` - creates UNIX account
* `--apache` - creates apache virtual host config for the specified domain name
* `--mysql` - creates MySQL user and database
* `--django-nginx` - creates Virtualenv, uWSGI and nginx config for the Django project

## Notes

* You must have `apache2-mpm-itk` module installed to set owner of the PHP process.
* You must have password for the root user to use `--mysql` feature.

## Author
Eugene Zyatev ([eu@f1dev.com](mailto:eu@f1dev.com)).