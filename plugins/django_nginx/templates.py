r"""Templates file for the Django Nginx plugin.

There are main configuration parameters in this file.

"""

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "eu@f1dev.com"

VIRTUAL_HOST = (
    """
    server {
        listen         80;
        server_name    www.%(domain)s;
        return         301 http://%(domain)s$request_uri;
    }
    server {
        listen         80;

        server_name    %(domain)s;

        access_log     /var/log/nginx/%(domain)s.access.log;
        error_log      /var/log/nginx/%(domain)s.error.log;

        client_max_body_size 50m;

        location /media/ {
            alias      /home/%(user)s/%(project)s/media/;
            add_header Pragma public;
            add_header Cache-Control "public";
            expires 30d;
        }

        location /static/ {
            alias      /home/%(user)s/%(project)s/static/;
            add_header Pragma public;
            add_header Cache-Control "public";
            expires 30d;
        }

        location / {
            include    uwsgi_params;
            uwsgi_pass unix:///var/run/uwsgi/app/%(project)s/socket;
        }
    }
    """
)

UWSGI_APP = (
    """
    plugins=python27
    chdir=/home/%(user)s/%(project)s
    virtualenv=/home/%(user)s/venv
    module=%(project)s.wsgi:application
    master=True
    uid=%(user)s
    gid=%(user)s
    """
)
