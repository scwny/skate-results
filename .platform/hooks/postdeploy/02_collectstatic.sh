#!/usr/bin/env bash
set -e

# Turn OFF history expansion so ! in SECRET_KEY (and others) is literal
set +H          # or:  set +o histexpand


# 1 Load the Elastic Beanstalk environment variables
# creates DB_HOST, SECRET_KEY, etc. for this shell
if [ -f /opt/elasticbeanstalk/deployment/env ]; then
  source /opt/elasticbeanstalk/deployment/env
fi

# 2 Run collectstatic as the 'webapp' user so permissions are correct
sudo -u webapp -E bash -c '
  source /var/app/venv/*/bin/activate
  cd /var/app/current
  python manage.py collectstatic --noinput
'
