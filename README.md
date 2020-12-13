MobiShopper Web
===============

The MobiShopper web app: public API and managment site.

Built in Python, Django, Django REST Framework, and using Vue and Bootstrap for the UI.

This project was part of my BSc diploma thesis. This diploma thesis was written
in 2020, and so all of its dependencies are probably quite old.

Copyright © 2020, Krzysztof Wojciechowski. All rights reserved.
This code is not open-source, but is made available as an archive and showcase.

Deployment
==========

Deploy to a Linux/Unix server with Python 3.6+. A web server (nginx) and a WSGI
server (gunicorn, uwsgi) is required.

1. Install PostgreSQL, create a user and database
2. Set up the app and Python:

       # mkdir -p /srv/mobishopper.krzysztofwojciechowski.pl/{static,media}
       # git clone mobishopper-web.git /srv/mobishopper.krzysztofwojciechowski.pl/appdata
       # (Or extract from a ZIP to that location)
       # python3 -m venv /srv/mobishopper.krzysztofwojciechowski.pl/venv
       # /srv/mobishopper.krzysztofwojciechowski.pl/venv/bin/pip install -r /srv/mobishopper.krzysztofwojciechowski.pl/appdata/prod-requirements.txt

3. Install and configure nginx and a WSGI server, see <https://docs.djangoproject.com/en/3.1/howto/deployment/> for details
4. Ensure the WSGI server sets the environment variables listed below. Also
   ensure correct permissions to all directories.

Environment configuration
-------------------------

The following environment variables are expected:

* `DJANGO_SETTINGS_MODULE=mobishopper.settings`
* `SECRET_KEY` — can be generated with `python -c 'from django.core.management import utils; print(utils.get_random_secret_key())'`
* `MOBISHOPPER_ENV` — choose `dev`, `prod`, or `debug` (production settings + debug mode)
* `DJANGO_LOG_PATH` — application logs will be written to that file
* `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL database credentials

nginx configuration
-------------------

Sample server block:

    server {
        listen 80;
        server_name mobishopper.krzysztofwojciechowski.pl;
        root /srv/mobishopper.krzysztofwojciechowski.pl;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/srv/mobishopper.krzysztofwojciechowski.pl/uwsgi.sock;
        }

        location /favicon.ico {
            alias /srv/mobishopper.krzysztofwojciechowski.pl/static/favicon.ico;
        }

        location /static {
            alias /srv/mobishopper.krzysztofwojciechowski.pl/static;
        }

        location /media {
            alias /srv/mobishopper.krzysztofwojciechowski.pl/media;
        }
