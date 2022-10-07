#!/usr/bin/env bash

/usr/local/bin/uwsgi --chdir=/app \
    --http 0.0.0.0:8000 \
    --module=wsgi:application \
    --env DJANGO_SETTINGS_MODULE=tritium.conf \
    --master --pidfile=/tmp/project-master.pid \
    --socket=127.0.0.1:49152 \
    --processes=5 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum
