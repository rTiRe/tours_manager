"""Module for insert countries names into table."""

import csv
from os import getenv
from uuid import uuid4

from dotenv import load_dotenv
from psycopg import Connection, connect

load_dotenv()

creds = (
    ('host', 'PG_HOST'),
    ('port', 'PG_PORT'),
    ('user', 'PG_USER'),
    ('password', 'PG_PASSWORD'),
    ('dbname', 'PG_DBNAME'),
)

creds = {var_name: getenv(env_var) for var_name, env_var in creds}

connection: Connection = connect(**creds)
cursor = connection.cursor()

countries = []

file_path = 'countries.csv'
with open(file_path, 'r', encoding='utf-8') as countries_csv:
    reader = csv.reader(countries_csv)
    countries.extend(next(reader))

insert_link = 'INSERT INTO tours_data.country (id, name) VALUES ({0}, {1})'

for country in countries:
    cursor.execute(insert_link.format(uuid4(), country))

connection.commit()
