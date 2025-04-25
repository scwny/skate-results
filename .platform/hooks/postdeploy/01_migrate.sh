#!/bin/bash
# Runs every time EB successfully deploys a new application version.
#!/usr/bin/env bash
set -e

# Turn OFF history expansion so ! in SECRET_KEY (and others) is literal
set +H          # or:  set +o histexpand


# 1 Load the Elastic Beanstalk environment variables
# creates DB_HOST, SECRET_KEY, etc. for this shell
if [ -f /opt/elasticbeanstalk/deployment/env ]; then
  source /opt/elasticbeanstalk/deployment/env
fi

source /var/app/venv/*/bin/activate        # activates the virtual-env EB created
cd /var/app/current                         # the app code directory
python manage.py migrate --noinput
