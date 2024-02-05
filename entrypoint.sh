#! /usr/bin/env bash
set -e

/uwsgi-nginx-entrypoint.sh

# Get the listen port for Nginx, default to 80
USE_LISTEN_PORT=${LISTEN_PORT:-80}

if [ -f /app/nginx.conf ]; then
    cp /app/nginx.conf /etc/nginx/nginx.conf
else
    content_server='server {\n'
    content_server=$content_server"    listen ${USE_LISTEN_PORT};\n"
    content_server=$content_server'    location / {\n'
    content_server=$content_server'        try_files $uri @app;\n'
    content_server=$content_server'    }\n'
    content_server=$content_server'    location @app {\n'
    content_server=$content_server'        include uwsgi_params;\n'
    content_server=$content_server'        uwsgi_pass unix:///tmp/uwsgi.sock;\n'
    content_server=$content_server'        uwsgi_buffer_size 256k;\n'
    content_server=$content_server'        uwsgi_buffers 32 512k;\n'
    content_server=$content_server'        uwsgi_busy_buffers_size 512k;\n'
    content_server=$content_server'    }\n'
    content_server=$content_server'}\n'
    # Save generated server /etc/nginx/conf.d/nginx.conf
    printf "$content_server" > /etc/nginx/conf.d/nginx.conf
fi

exec "$@"
