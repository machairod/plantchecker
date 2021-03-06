import configparser
import datetime
import json
import os

from mysql.connector import connect, Error

path = os.path.dirname(__file__)
configfile = os.path.join(path, 'settings.ini')

config = configparser.ConfigParser()
config.read(configfile)
connection = connect(
    host=config['plantbase']['host'],
    user=config['plantbase']['user'],
    password=config['plantbase']['password'],
    database=config['plantbase']['database']
)


class Plantchecker():
    def get_user_id(login: str = None):
        if login is None:
            return "Мы вас не узнали. Укажите ваш логин"
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            user_id = cursor.fetchall()
        cursor.close()
        if len(user_id) == 0:
            return 'Error, no id'
        else:
            return user_id[0][0]

    def get_plantspec(login: str = None):
        global connection
        global path
        user_id = Plantchecker.get_user_id(login)
        if type(user_id) == str:
            return user_id

        plantspec_json = os.path.join(path, 'plantspecies.json')
        with open(plantspec_json, 'r') as plantspecies:
            plantspec = json.load(plantspecies)
            plantspec = json.dumps(plantspec, ensure_ascii=False)

        return plantspec

    def check_user_plants(login: str = None):
        global connection
        user_id = Plantchecker.get_user_id(login)
        if type(user_id) == str:
            return user_id
        with connection.cursor() as cursor:
            cursor.execute("""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE 
        TABLE_SCHEMA = 'plantcheckerDB' AND TABLE_NAME = 'userplants'""")
            columnlist = [('').join(x) for x in cursor.fetchall()]

            cursor.execute('select plantname from userplants where user="{id}"'.format(id=user_id))
            userplants_list = [('').join(x) for x in cursor.fetchall()]
            if len(userplants_list) == 0:
                return ("У вас еще нет растений")

        user_plants = {}
        for name in userplants_list:
            plant_card = {}
            for x in columnlist:
                columns = ['id', 'user', 'plantname', 'plantspec']
                if x in columns:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            'select {column} from userplants where user={id} and plantname="{name}"'.format(column=x,
                                                                                                            id=user_id,
                                                                                                            name=name))
                        data = cursor.fetchall()[0][0]
                        plant_card[x] = data

            user_plants.setdefault(name, plant_card)
        cursor.close()
        user_plants = json.dumps(user_plants, ensure_ascii=False)
        return user_plants

    def user_plantcard(login: str = None, **kwargs):
        global connection
        user_id = Plantchecker.get_user_id(login)
        if type(user_id) == str:
            return user_id

        plant_id = kwargs.get('plant_id', 0)
        plantname = kwargs.get('plantname', None)
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'plantcheckerDB' AND "
                    "TABLE_NAME = 'userplants';")
                columnlist = [''.join(x) for x in cursor.fetchall()]
                plant_card = {}
                for x in columnlist:
                    cursor.execute(
                        'select {column} from userplants where (id="{id}" or plantname="{plantname}") and user={'
                        'user_id}'.format(
                            column=x,
                            id=plant_id,
                            user_id=user_id, plantname=plantname))
                    plant_card[x] = cursor.fetchall()[0][0]
            except Error as e:
                return e
        cursor.close()
        plant_card = json.dumps(plant_card, ensure_ascii=False)

        return plant_card

    def add_user_plant(plantjson: json):
        global connection
        global path

        # словарь для итогового запроса на добавление в базу
        plant_data = {}

        # подтягиваем данные растения из тела запроса
        plantdata = json.loads(plantjson)
        if 'last_watering' in plantdata:
            last_watering = plantdata['last_watering']
            if type(last_watering) == str and last_watering.count('-') == 2:
                last_watering = datetime.datetime.strptime(last_watering, "%d-%m-%Y").date()
            elif last_watering is None:
                last_watering = datetime.date.today()
                plant_data['last_watering'] = last_watering.strftime("%d-%m-%Y")
        else:
            return 'Неправильный формат даты. Используйте строку "dd-mm-yyyy".\n'

            # проверяем что мы знакомы с пользователем
        if 'user_id' in plantdata and plantdata['user_id'] is not None:
            user_id = plantdata['user_id']
        elif 'login' in plantdata:
            login = plantdata['login']
            user_id = Plantchecker.get_user_id(login)
            if type(user_id) == str:
                return 'Не нашли такого пользователя'
        else:
            return 'Не смогли опознать пользователя'

        plantname = plantdata['plantname'] if plantdata['plantname'] is not None else ''
        plantspec = plantdata['plantspec'] if plantdata['plantspec'] is not None else ''

        # достаем словарь видов растениий
        plantspec_json = os.path.join(path, 'plantspecies.json')
        with open(plantspec_json, 'r') as plantspecies:
            plant_dict = json.load(plantspecies)
        plantspec = plantspec.lower()
        if plantspec not in plant_dict:
            return 'Не опознали вид растения'
        if plantname == '' or plantspec == '':
            return 'Не определили растение, которое вы хотите добавить'

        plant_data['water_freq_summer'] = plant_dict[plantspec]['water_summer']
        plant_data['water_freq_winter'] = plant_dict[plantspec]['water_winter']
        plant_data["fertile_freq_summer"] = plant_dict[plantspec]['fertile_summer']
        plant_data["fertile_freq_winter"] = plant_dict[plantspec]['fertile_winter']

        water_gap = plant_data['water_freq_summer'] if last_watering.month in range(3, 10) else plant_data[
            'water_freq_winter']
        fertile_gap = plant_data['fertile_freq_summer'] if last_watering.month in range(3, 10) else plant_data[
            'fertile_freq_winter']
        next_water = last_watering + datetime.timedelta(days=water_gap)
        next_fertile = last_watering + datetime.timedelta(days=fertile_gap)

        plant_data['next_water'] = next_water.strftime("%d-%m-%Y")
        plant_data['next_fertile'] = next_fertile.strftime("%d-%m-%Y")
        plant_data['plantspec'] = plantspec
        plant_data["last_watering"] = last_watering.strftime("%d-%m-%Y")
        plant_data["last_fertiling"] = last_watering.strftime("%d-%m-%Y")
        plant_data['light'] = plant_dict[plantspec]['light']
        plant_data["spraying"] = plant_dict[plantspec]['spraying']
        plant_data["plantname"] = plantname
        plant_data['user'] = user_id

        add_plant = '''insert into userplants (user, plantname, plantspec, last_watering, last_fertiling, 
        water_freq_summer, water_freq_winter, fertile_freq_summer, fertile_freq_winter, spraying, light, next_water, 
        next_fertile) values (%(user)s, %(plantname)s, %(plantspec)s, %(last_watering)s, %(last_fertiling)s, 
        %(water_freq_summer)s, %(water_freq_winter)s, %(fertile_freq_summer)s, %(fertile_freq_winter)s, %(spraying)s, 
        %(light)s,  %(next_water)s, %(next_fertile)s)'''

        with connection.cursor() as cursor:
            try:
                cursor.execute('select * from userplants where id = {id} and plantname = "{plantname}"'.format(
                    id=user_id, plantname=plantname))
                checkdata = cursor.fetchall()
                if len(checkdata) != 0:
                    return "Похоже, растение с таким названием вы уже добавили\n"
                cursor.execute(add_plant, plant_data)
                connection.commit()
                return 'Растение добавлено в ваш список'
            except Error as e:
                return f'Something wrong - {e}'

    def add_plant_water(plantdata: json):
        global connection
        add_data = {}
        plantdata = json.loads(plantdata)
        if 'date' in plantdata:
            date = plantdata['date']
            if type(date) == str and len(date) == 10 and date.find('-') == 2:
                date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            elif date is None:
                date = datetime.date.today()
        else:
            return 'Неправильный формат даты. Используйте строку "dd-mm-yyyy".\n'

        plant = plantdata['name'] if plantdata['name'] is not None else ''
        plant_id = plantdata['id'] if plantdata['id'] is not None else 0
        if 'user_id' in plantdata and plantdata['user_id'] is not None:
            user_id = plantdata['user_id']
        elif 'login' in plantdata:
            login = plantdata['login']
            user_id = Plantchecker.get_user_id(login)
            if type(user_id) == str:
                return 'Не нашли такого пользователя'

        if plant == '' and plant_id == 0:
            return 'Не определили растение, которое вы полили\n'

        with connection.cursor() as cursor:
            cursor.execute(
                '''select last_watering,water_freq_summer, water_freq_winter from userplants 
                         where (id = "{id}" or plantname = "{name}") and user ={user_id}'''.format(id=plant_id,
                                                                                                   name=plant,
                                                                                                   user_id=user_id))
            add_data['id'] = plant_id
            add_data['name'] = plant
            add_data['date'] = date.strftime("%d-%m-%Y")
            add_data['user'] = user_id
            add_string = '''update userplants set last_watering = %(date)s, next_water= %(next_date)s 
            where (id = %(id)s or plantname = %(name)s) and user = %(user)s'''

            plantsql = cursor.fetchall()
            this_month = date.month
            gap = plantsql[0][1] if this_month in range(3, 10) else plantsql[0][2]
            next_date = date + datetime.timedelta(days=gap)
            add_data['next_date'] = next_date.strftime("%d-%m-%Y")

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                cursor.execute(
                    'select plantname from userplants where id={id} and user={user}'.format(id=plant_id, user=user_id))
                plant = cursor.fetchall()
                cursor.close()
                return 'Событие зафиксировано, растение {plant} полито {date}\n'.format(plant=plant[0][0],
                                                                                        date=str(date))

            except Error as e:
                return 'Произошла ошибка - ' + str(e) + '\n'

    def add_plant_fertile(plantdata: json):
        global connection
        add_data = {}
        plantdata = json.loads(plantdata)
        if 'date' in plantdata:
            date = plantdata['date']
            if type(date) == str and len(date) == 10 and date.find('-') == 2:
                date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            elif date is None:
                date = datetime.date.today()
            else:
                return 'Неправильный формат даты. Используйте строку "dd-mm-yyyy".\n'

        plant = plantdata['name'] if plantdata['name'] is not None else ''
        plant_id = plantdata['id'] if plantdata['id'] is not None else 0
        if 'user_id' in plantdata and plantdata['user_id'] is not None:
            user_id = plantdata['user_id']
        elif 'login' in plantdata:
            login = plantdata['login']
            user_id = Plantchecker.get_user_id(login)
            if type(user_id) == str:
                return 'Не нашли такого пользователя'

        if plant == '' and plant_id == 0:
            return 'Не определили растение, которое вы удобрили\n'

        with connection.cursor() as cursor:
            cursor.execute(
                '''select last_fertiling,fertile_freq_summer, fertile_freq_winter from userplants 
                         where (id = "{id}" or plantname = "{name}") and user ={user_id}'''.format(id=plant_id,
                                                                                                   name=plant,
                                                                                                   user_id=user_id))
            add_data['id'] = plant_id
            add_data['name'] = plant
            add_data['date'] = date.strftime("%d-%m-%Y")
            add_data['user'] = user_id
            add_string = '''update userplants set last_fertiling = %(date)s, 
                                    next_fertile= %(next_date)s where (id = %(id)s 
                                    or plantname = %(name)s) and user = %(user)s'''

            plantsql = cursor.fetchall()
            this_month = date.month
            gap = plantsql[0][1] if this_month in range(3, 10) else plantsql[0][2]
            next_date = date + datetime.timedelta(days=gap)
            add_data['next_date'] = next_date.strftime("%d-%m-%Y")

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                cursor.execute('select plantname from userplants where id={id} and user={user}'.format(id=plant_id,
                                                                                                       user=user_id))
                plant = cursor.fetchall()
                cursor.close()
                return 'Событие зафиксировано, растение {plant} удобрено {date}\n'.format(plant=plant[0][0],
                                                                                          date=str(date))

            except Error as e:
                return 'Произошла ошибка - ' + str(e) + '\n'

    def memento_list(login: str = None):
        global connection
        user_id = Plantchecker.get_user_id(login)
        if type(user_id) == str:
            return 'Не нашли такого пользователя'
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'select id, plantname, next_water, next_fertile from userplants where user={id}'.format(id=user_id))
                plantlist = cursor.fetchall()
            cursor.close()
            if len(plantlist) != 0:
                memento_list = json.dumps(plantlist, ensure_ascii=False)
                return memento_list
            else:
                return 'У вас нет растений'

        except Error as e:
            return 'Произошла ошибка - ' + str(e) + '\n'

    def delete_plant(datajson: json):
        global connection

        # подтягиваем данные растения из тела запроса
        plantdata = json.loads(datajson)

        # проверяем что мы знакомы с пользователем
        if 'user_id' in plantdata and plantdata['user_id'] is not None:
            user_id = plantdata['user_id']
        elif 'login' in plantdata:
            login = plantdata['login']
            user_id = Plantchecker.get_user_id(login)
            if type(user_id) == str:
                return 'Не нашли такого пользователя'
        else:
            return 'Не смогли опознать пользователя'

        plantname = plantdata['plantname'] if plantdata['plantname'] is not None else ''
        plant_id = plantdata['plant_id'] if plantdata['plant_id'] is not None else 0

        with connection.cursor() as cursor:
            cursor.execute(
                'select plantname from userplants where user="{id}" and (plantname="{plantname}" '
                'or id={plant_id})'.format(plantname=plantname, id=user_id, plant_id=plant_id))
            plantlist = [''.join(x) for x in cursor.fetchall()]

            if len(plantlist) == 0:
                return "Растение не существует"

            cursor.execute(
                'delete from userplants where user="{id}" and (plantname="{plantname}" or id="{plant_id}")'.format(
                    plantname=plantname, id=user_id, plant_id=plant_id))
            connection.commit()
            cursor.execute(
                'select plantname from userplants where user="{id}" and (plantname="{plantname}" '
                'or id={plant_id})'.format(plantname=plantname, id=user_id, plant_id=plant_id))

            plantlist = [''.join(x) for x in cursor.fetchall()]
        cursor.close()
        return 'Растение удалено' if len(plantlist) == 0 else 'Что-то случилось, повторите запрос'

    def add_user(login: str = None, name: str = None):
        global connection
        if name is None and login is None:
            return "100 - not enough parameters"
        with connection.cursor() as cursor:
            cursor.execute('select * from users where login="{login}"'.format(login=login))
            users = [''.join(str(x)) for x in cursor.fetchall()]
            if len(users) == 0:
                cursor.execute('insert into users values (Null,"{login}", "{name}")'.format(login=login, name=name))
                connection.commit()
                return "200 - user added"

            elif len(users) == 1:
                return "201 - user is already added"

            else:
                return "400 - error"

        cursor.close()


if __name__ == '__main__':
    pass

    # path = os.path.abspath('test.json')
    # with open(path) as file:
    #     print(Plantchecker.add_plant_fertile(file))

    # column = ['last_watering', "last_fertiling", "next_water", "next_fertile"]
    # with connection.cursor() as cursor:
    #     cursor.execute('select {column} from userplants where id=6'.format(column=column[0]))
    #     datelist = cursor.fetchall()
    #     print(type((datelist[0][0])))
    #     # connection.commit()
    # cursor.close()
