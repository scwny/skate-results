#!/usr/bin/env bash
sudo -u webapp -i bash <<'INNER'
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py collectstatic --noinput
INNER
