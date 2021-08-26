from fastapi import FastAPI
import uvicorn
from mysql.connector import connect, Error
import json, datetime, os, configparser

app = FastAPI()

path = os.path.dirname(__file__)
config = configparser.ConfigParser()

configfile = os.path.join(path, 'mysql-settings.ini')
config.read(configfile)

# MYSQL parameters
host = config['plantbase']['host']
user = config['plantbase']['user']
password = config['plantbase']['password']
database = config['plantbase']['database']

@app.get("/")
async def hello():
    return "Plantchecker"

@app.get("/checkuserplants")
async def checkUserPlants(login: str = None):
    with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            id = cursor.fetchone()
            if id == None:
                return ("Мы вас не узнали. Укажите ваш логин")
            id = id[0]

            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'plantcheckerDB' AND TABLE_NAME = 'userplants'")
            columnlist = [('').join(x) for x in cursor.fetchall()]

            cursor.execute('select plantname from userplants where user="{id}"'.format(id=id))
            userplants_list = [('').join(x) for x in cursor.fetchall()]
            if len(userplants_list) == 0:
                return('У вас еще нет растений')

    user_plants = {}
    for name in userplants_list:
        plant_card={}
        for x in columnlist:
            with connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute('select {column} from userplants where user={id} and plantname="{name}"'.format(column=x, id=id, name=name))
                    data = cursor.fetchall()[0][0]
            plant_card[x] = data

        user_plants.setdefault(name,plant_card)
    return user_plants

@app.post("/addUserWatering")
def addUserWatering(last_watering: str = None, plant: str = None):

    add_data = {}

    if last_watering == None:
        return ('Неправильная дата')
    elif type(last_watering) == str and len(last_watering) == 10 and last_watering.find('.') == 2:
        add_data['date'] = datetime.datetime.strptime(last_watering, "%d.%m.%Y").date()
    else:
        return ('Неправильный формат даты. Используйте "dd.mm.yyyy".')

    if plant == None:
        return ('Не определили растение, которое вы полили')

    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:

        with connection.cursor() as cursor:

            if plant.isdigit() == True:
                plant_id = int(plant)
                cursor.execute(
                    'select last_watering,water_freq_summer, water_freq_winter from userplants where id = "{id}"'.format(
                        id=plant_id))

                add_data['id'] = plant_id
                add_string = 'update userplants set last_watering = %(date)s, next_water= %(next_date)s where id = %(id)s'

            # надо переписать чтобы работало на строки с включением цифр
            elif plant.isalpha() == True:
                plantname = plant
                cursor.execute(
                    'select last_watering,water_freq_summer, water_freq_winter from userplants where plantname="{plantname}"'.format(
                        plantname=plantname))

                add_data['plantname'] = plant
                add_string = 'update userplants set last_watering = %(date)s, next_water= %(next_date)s where plantname = %(plantname)s'

            plantsql = cursor.fetchall()
            if plantsql[0][0].month in range(3, 10):
                add_data['next_date'] = plantsql[0][0] + datetime.timedelta(days=plantsql[0][1])
            else:
                add_data['next_date'] = plantsql[0][0] + datetime.timedelta(days=plantsql[0][2])

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                return ('Событие зафиксировано, растение {plant} полито'.format(plant = plant))

            except Error as e:
                return e

def addUserFertiling(last_fertiling=None, plant=None):

    add_data = {}

    if last_fertiling == None:
        return ('Неправильная дата')
    elif type(last_fertiling) == str and len(last_fertiling) == 10 and last_fertiling.find('.') == 2:
        add_data['date'] = datetime.datetime.strptime(last_fertiling, "%d.%m.%Y").date()
    else:
        return ('Неправильный формат даты. Используйте "dd.mm.yyyy".')

    if plant == None:
        return ('Не определили растение, которое вы подкормили')

    with connect(
            host=host,
            user=user,
            password=password,
            database=database
    ) as connection:

        with connection.cursor() as cursor:

            if plant.isdigit() == True:
                plant_id = int(plant)
                cursor.execute(
                    'select last_fertiling,fertile_freq_summer, fertile_freq_winter from userplants where id = "{id}"'.format(
                        id=plant_id))

                add_data['id'] = plant_id
                add_string = 'update userplants set last_fertiling = %(date)s, next_fertile= %(next_date)s where id = %(id)s'


            # надо переписать чтобы работало на строки с включением цифр
            elif plant.isalpha() == True:
                plantname = plant
                cursor.execute(
                    'select last_fertiling,fertile_freq_summer, fertile_freq_winter from userplants where plantname="{plantname}"'.format(
                        plantname=plantname))

                add_data['plantname'] = plant
                add_string = 'update userplants set last_fertiling = %(date)s, next_fertile= %(next_date)s where plantname = %(plantname)s'

            plantsql = cursor.fetchall()
            if plantsql[0][0].month in range(3, 10):
                add_data['next_date'] = plantsql[0][0] + datetime.timedelta(days=plantsql[0][1])
            else:
                add_data['next_date'] = plantsql[0][0] + datetime.timedelta(days=plantsql[0][2])

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                return ('Событие зафиксировано, растение {plant} подкормлено'.format(plant = plant))

            except Error as e:
                return e
if __name__ == '__main__':
    uvicorn.run('fastapi_settings:app', host='127.0.0.1', port=5000, reload=True)