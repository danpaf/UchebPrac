import getpass
import re
from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField
import psycopg2
from peewee import CharField, DateField, UUIDField, TimeField, IntegerField
from peewee import Model, DatabaseProxy, ForeignKeyField
from peewee import PostgresqlDatabase,MySQLDatabase

import uuid

import settings

database = PostgresqlDatabase(database=settings.database, user=settings.user, password=settings.password, host=settings.host, port=settings.port)
# database = MySQLDatabase()


class User(Model):
    login = CharField(unique=True)
    password = CharField()

    class Meta:
        database = database


# Определение модели данных
class AccessLog(Model):
    ip_address = CharField()
    date = DateTimeField()
    http_method = CharField()
    response_code = IntegerField()
    some_int = IntegerField()

    class Meta:
        database = database

    def to_dict(self):
        return {
            'ip_address': self.ip_address,
            'date': self.date,
            'method': self.http_method,
            'response_Code': self.response_code,
            'some_int':self.some_int
        }

# Создание таблицы в базе данных
def create_table():
    with database:
        database.create_tables([AccessLog])
        database.create_tables([User])
        # print('БД создана')

def authenticate_user(login,password):

    user = User.select().where(User.login == login, User.password == password).first()

    if user:
        print("Authentication successful.")
        return True
    else:
        print("Authentication failed. Please try again.")
        return False

def parse_logs(log_file):
    log_pattern = settings.log_pattern
    # print('parse active')
    with open(log_file, 'r') as file:
        for log in file:
            match = re.search(log_pattern, log)
            if match:
                ip_address = match.group(1)
                date_str = match.group(2)
                http_method = match.group(3)
                response_code = int(match.group(4))
                some_int = int(match.group(5))
                # print('match', ip_address, date_str, http_method,response_code)
                date = datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")

                AccessLog.get_or_create(ip_address=ip_address, date=date, http_method=http_method,
                                  response_code=response_code,some_int=some_int)
            else:
                print('err')
    print(" [SUCCESS] Logs Saved")
    print(' [SUCCESS] Database initialized and logs parsed.')




