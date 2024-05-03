from psycopg import connect
from dotenv import load_dotenv
from os import getenv
from random import randint
from uuid import uuid4

load_dotenv()

creds = (
    ('host', 'PG_HOST'),
    ('port', 'PG_PORT'),
    ('user', 'PG_USER'),
    ('password', 'PG_PASSWORD'),
    ('dbname', 'PG_DBNAME')
)

creds = {var: getenv(env_var) for var, env_var in creds}

connection = connect(**creds)
cursor = connection.cursor()

COUNTRIES = []

import csv
file_path = 'countries.csv'
with open(file_path, 'r', encoding='utf-8') as countries_csv:
    reader = csv.reader(countries_csv)
    COUNTRIES.extend(next(reader))

insert_link = 'INSERT INTO tours_data.country (id, name) VALUES (%s, %s)'

for country in COUNTRIES:
    cursor.execute(insert_link, (uuid4(), country))

connection.commit()