import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pyodbc
from msvcrt import getch
import getpass
import sys

# Setting the connection
DRIVER_NAME = '{ODBC Driver 18 for SQL Server}'
SERVER_NAME = 'PRDBI'
DATABASE_NAME = 'paytel_olap'


def connect_single_query(query, passw, user):
    try:
        user_name = user
        user_password = passw
        engine = create_engine(
            f'mssql+pyodbc://{user_name}:{user_password}@' + SERVER_NAME + '/' + DATABASE_NAME + '?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&authentication=ActiveDirectoryIntegrated')

        with engine.connect() as connection:
            connection.echo = False
            tableResult = pd.read_sql(f'{query}', connection)

        engine.dispose()
    except ConnectionError:
        print('Connection error')

    return tableResult
