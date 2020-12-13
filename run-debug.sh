#!/usr/bin/zsh
source local-config
export MOBISHOPPER_ENV=debug
../venv/bin/python manage.py runserver
