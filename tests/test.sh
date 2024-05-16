#!/bin/bash
export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=test
export MINIO_ACCESS_KEY_ID=user
export MINIO_SECRET_ACCESS_KEY=password
export MINIO_STORAGE_BUCKET_NAME=static
export MINIO_API=http://localhost:9000
export MINIO_CONSISTENCY_CHECK_ON_START=False

python3 manage.py test $1