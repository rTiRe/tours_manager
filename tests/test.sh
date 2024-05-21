#!/bin/bash
export DJANGO_SECRET_KEY="django-insecure-pt4!7*d%-dn)&lx6@598y(1!!rljgaieunnwk!n)-#r^ew(dcb"
export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=test
export MINIO_ACCESS_KEY_ID=ULk99g9UwyucWln57ypo
export MINIO_SECRET_ACCESS_KEY=dGKHOvOO9166VEMOO0tSRdUVVUcm5odgYgB2Yfjs
export MINIO_STORAGE_BUCKET_NAME=static
export MINIO_API=http://localhost:9000
export MINIO_CONSISTENCY_CHECK_ON_START=False

python3 manage.py test $1