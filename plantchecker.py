from mysql.connector import connect, Error
import os, json, datetime, configparser

path = os.path.dirname(__file__)
configfile = os.path.join(path, 'mysql-settings.ini')

config = configparser.ConfigParser()
config.read(configfile)
connection = connect(
    host=config['plantbase']['host'],
    user=config['plantbase']['user'],
    password=config['plantbase']['password'],
    database=config['plantbase']['database']
)


# connection = connect(option_files=configfile)

class Plantchecker():
    def checkUserPlants(login: str):
        global connection
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            id = cursor.fetchone()
            if id == None:
                return ("Мы вас не узнали. Укажите ваш логин")
            id = id[0]

            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'plantcheckerDB' AND TABLE_NAME = 'userplants'")
            columnlist = [('').join(x) for x in cursor.fetchall()]

            cursor.execute('select plantname from userplants where user="{id}"'.format(id=id))
            userplants_list = [('').join(x) for x in cursor.fetchall()]
            if len(userplants_list) == 0:
                return ('У вас еще нет растений')

        user_plants = {}
        for name in userplants_list:
            plant_card = {}
            for x in columnlist:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'select {column} from userplants where user={id} and plantname="{name}"'.format(column=x, id=id,
                                                                                                        name=name))
                    data = cursor.fetchall()[0][0]
                plant_card[x] = data

            user_plants.setdefault(name, plant_card)
        cursor.close()
        return user_plants

    def userPlantCard(plant_id: int = None, plantname: str = ''):
        global connection
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'plantcheckerDB' AND TABLE_NAME = 'userplants';")
                columnlist = [('').join(x) for x in cursor.fetchall()]
                plant_card = {}
                for x in columnlist:
                    cursor.execute(
                        'select {column} from userplants where id="{id}" or plantname="{name}"'.format(column=x,
                                                                                                       id=plant_id,
                                                                                                       name=plantname))
                    plant_card[x] = cursor.fetchone()[0]

                return plant_card
            except Error as e:
                print(e)

    def addUserPlant(login: str, plantname: str, plantspec: str, last_watering: str = None):
        global connection
        plant_data = {}
        with open('plantspecies.json', 'r') as plantspecies:
            plant_dict = json.load(plantspecies)
        plantspec = plantspec.lower()
        if plantspec not in plant_dict:
            return 'Не опознали вид растения'

        if type(last_watering) == str and (len(last_watering) == 10) and last_watering.find('.') == 2:
            plant_data["last_watering"] = datetime.datetime.strptime(last_watering, "%d.%m.%Y").date()
        elif last_watering == None:
            plant_data['last_watering'] = datetime.date.today()
        else:
            return ('Неправильный формат даты. Используйте "dd.mm.yyyy".')

        plant_data["last_fertiling"] = plant_data["last_watering"]
        plant_data['plantspec'] = plantspec
        plant_data['light'] = plant_dict[plantspec]['light']
        plant_data['water_freq_summer'] = plant_dict[plantspec]['water_summer']
        plant_data['water_freq_winter'] = plant_dict[plantspec]['water_winter']
        plant_data["fertile_freq_summer"] = plant_dict[plantspec]['fertile_summer']
        plant_data["fertile_freq_winter"] = plant_dict[plantspec]['fertile_winter']
        plant_data["spraying"] = plant_dict[plantspec]['spraying']
        plant_data["plantname"] = plantname

        add_plant = "insert into userplants (user, plantname, plantspec, last_watering, last_fertiling, water_freq_summer, water_freq_winter, fertile_freq_summer, fertile_freq_winter, spraying, light) values (%(user)s, %(plantname)s, %(plantspec)s, %(last_watering)s, %(last_fertiling)s, %(water_freq_summer)s, %(water_freq_winter)s, %(fertile_freq_summer)s, %(fertile_freq_winter)s, %(spraying)s, %(light)s)"

        with connection.cursor() as cursor:
            cursor.execute('select id from users where login="{user}"'.format(user=login))
            user = cursor.fetchall()
            if len(user) == 0:
                return 'Не нашли такого пользователя'
            plant_data['user'] = user[0][0]

            try:
                cursor.execute(
                    'select * from userplants where id = {id} and plantname = "{plantname}" and plantspec = "{plantspec}"'.format(
                        id=user[0][0], plantname=plantname, plantspec=plantspec))
                checkdata = cursor.fetchall()
                print(checkdata)
                if len(checkdata) != 0:
                    print(checkdata)
                    return ("Похоже, это растение вы уже вносили")
                cursor.execute(add_plant, plant_data)
                connection.commit()
                return ('Растение добавлено в ваш список')
            except Error as e:
                print(e)

    def add_plant_water(plantdata: json, **kwargs):
        global connection
        add_data = {}
        if 'date' in plantdata:
            date = plantdata['date']
            if type(date) == str and len(date) == 10 and date.find('.') == 2:
                add_data['date'] = datetime.datetime.strptime(date, "%d.%m.%Y").date()
            else:
                return 'Неправильный формат даты. Используйте строку "dd.mm.yyyy".'
        else:
            date = datetime.date.today()

        if 'name' in plantdata:
            plant = plantdata['name']
        else:
            plant = None

        plant_id = kwargs.get('id', None)

        if plant is None and plant_id is None:
            return 'Не определили растение, которое вы полили'

        with connection.cursor() as cursor:
            cursor.execute(
                '''select last_watering,water_freq_summer, water_freq_winter from userplants 
                         where id = "{id}" or plantname = "{name}"'''.format(id=plant_id, name=plant))
            add_data['id'] = plant_id
            add_data['name'] = plant
            add_data['date'] = date
            add_string = '''update userplants set last_watering = %(date)s, 
                                    next_water= %(next_date)s where id = %(id)s or plantname = %(name)s'''

            plantsql = cursor.fetchall()
            this_month = date.month
            if this_month in range(3, 10):
                gap = plantsql[0][1]
            else:
                gap = plantsql[0][2]
            add_data['next_date'] = date + datetime.timedelta(days=gap)

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                cursor.close()
                return 'Событие зафиксировано, растение {plant} полито\n'.format(plant=plant)

            except Error as e:
                return 'Произошла ошибка - '+str(e)


    def add_user_fertiling(last_fertiling: str = None, plant: str = None):
        global connection
        add_data = {}

        if last_fertiling == None:
            return ('Неправильная дата')
        elif type(last_fertiling) == str and len(last_fertiling) == 10 and last_fertiling.find('.') == 2:
            add_data['date'] = datetime.datetime.strptime(last_fertiling, "%d.%m.%Y").date()
        else:
            return ('Неправильный формат даты. Используйте "dd.mm.yyyy".')

        if plant == None:
            return ('Не определили растение, которое вы подкормили')

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
                return ('Событие зафиксировано, растение {plant} подкормлено'.format(plant=plant))

            except Error as e:
                print(e)

    def deletePlant(login: str = None, plantname: str = None):
        global connection
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            id = cursor.fetchone()
            if id is None:
                return "Мы вас не узнали. Укажите ваш логин"
            id = id[0]
            cursor.execute('select * from userplants where user="{id}"'.format(id=id))
            deleting_userplant = cursor.fetchall()
            if len(deleting_userplant) == 0:
                return 'У вас еще нет растений'
            cursor.execute('delete from userplants where plantname = "{plantname}"'.format(plantname=plantname))
            connection.commit()

    def addUser(login: str = None, platform: str = None):
        pass

    def deleteUser(login: str):
        pass
