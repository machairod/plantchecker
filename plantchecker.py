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
    def get_user_id(login:str = None):
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

    def check_user_plants(login: str = None):
        global connection
        if login is None:
            return ("Мы вас не узнали. Укажите ваш логин")
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            user_id = cursor.fetchone()
            user_id = user_id[0]
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
                columns = ['id','user','plantname','plantspec']
                if x in columns:
                    with connection.cursor() as cursor:
                        cursor.execute('select {column} from userplants where user={id} and plantname="{name}"'.format(column=x, id=user_id, name=name))
                        data = cursor.fetchall()[0][0]
                        plant_card[x] = data

            user_plants.setdefault(name, plant_card)
        cursor.close()
        user_plants = json.dumps(user_plants, ensure_ascii=False)
        return user_plants

    def user_plantcard(plant_id: int = 0, login: str = None):
        global connection
        if login is None:
            return ("Мы вас не узнали. Укажите ваш логин")
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "{login}"'.format(login=login))
            user_id = cursor.fetchone()
            user_id = user_id[0]

        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'plantcheckerDB' AND TABLE_NAME = 'userplants';")
                columnlist = [''.join(x) for x in cursor.fetchall()]
                plant_card = {}
                for x in columnlist:
                    cursor.execute(
                        'select {column} from userplants where id="{id}" and user={user_id}'.format(column=x,
                                                                                                    id=plant_id,
                                                                                                    user_id=user_id))
                    plant_card[x] = cursor.fetchall()[0][0]
            except Error as e:
                print(e)
        cursor.close()
        plant_card = json.dumps(plant_card, ensure_ascii=False)

        return plant_card

    def add_user_plant(login: str, plantname: str, plantspec: str, last_watering: str = None):
        global connection
        plant_data = {}
        with open('plantspecies.json', 'r') as plantspecies:
            plant_dict = json.load(plantspecies)
        plantspec = plantspec.lower()
        if plantspec not in plant_dict:
            return 'Не опознали вид растения'

        if type(last_watering) == str and (len(last_watering) == 10) and last_watering.find('-') == 2:
            plant_data["last_watering"] = last_watering
        elif last_watering is None:
            date = datetime.date.today()
            plant_data['last_watering'] = date.strftime("%d-%m-%Y")
        else:
            return 'Неправильный формат даты. Используйте "dd-mm-yyyy".\n'

        plant_data["last_fertiling"] = plant_data["last_watering"]
        plant_data['plantspec'] = plantspec
        plant_data['light'] = plant_dict[plantspec]['light']
        plant_data['water_freq_summer'] = plant_dict[plantspec]['water_summer']
        plant_data['water_freq_winter'] = plant_dict[plantspec]['water_winter']
        plant_data["fertile_freq_summer"] = plant_dict[plantspec]['fertile_summer']
        plant_data["fertile_freq_winter"] = plant_dict[plantspec]['fertile_winter']
        plant_data["spraying"] = plant_dict[plantspec]['spraying']
        plant_data["plantname"] = plantname

        add_plant = '''insert into userplants (user, plantname, plantspec, last_watering, 
        last_fertiling, water_freq_summer, water_freq_winter, fertile_freq_summer,
         fertile_freq_winter, spraying, light) values (%(user)s, %(plantname)s, %(plantspec)s,
          %(last_watering)s, %(last_fertiling)s, %(water_freq_summer)s, %(water_freq_winter)s,
           %(fertile_freq_summer)s, %(fertile_freq_winter)s, %(spraying)s, %(light)s)'''

        with connection.cursor() as cursor:
            cursor.execute('select id from users where login="{user}"'.format(user=login))
            user = cursor.fetchall()
            if len(user) == 0:
                return 'Не нашли такого пользователя'
            plant_data['user'] = user[0][0]

            try:
                cursor.execute(
                    'select * from userplants where id = {id} and plantname = "{plantname}"'
                    ' and plantspec = "{plantspec}"'.format(
                        id=user[0][0], plantname=plantname, plantspec=plantspec))
                checkdata = cursor.fetchall()
                if len(checkdata) != 0:
                    return "Похоже, это растение вы уже добавили\n"
                cursor.execute(add_plant, plant_data)
                connection.commit()
                return 'Растение добавлено в ваш список'
            except Error as e:
                print(e)

    def add_plant_water(plantdata: json):
        global connection
        add_data = {}
        plantdata = json.load(plantdata)
        if 'date' in plantdata:
            date = plantdata['date']
            if type(date) == str and len(date) == 10 and date.find('-') == 2:
                date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            else:
                return 'Неправильный формат даты. Используйте строку "dd-mm-yyyy".\n'
        else:
            date = datetime.date.today()

        plant = plantdata['name'] if 'name' in plantdata else None
        plant_id = plantdata['id'] if 'id' in plantdata else None

        if plant is None and plant_id is None:
            return 'Не определили растение, которое вы полили\n'

        with connection.cursor() as cursor:
            cursor.execute(
                '''select last_watering,water_freq_summer, water_freq_winter from userplants 
                         where id = "{id}" or plantname = "{name}"'''.format(id=plant_id, name=plant))
            add_data['id'] = plant_id
            add_data['name'] = plant
            add_data['date'] = date.strftime("%d-%m-%Y")
            add_string = '''update userplants set last_watering = %(date)s, 
                                    next_water= %(next_date)s where id = %(id)s or plantname = %(name)s'''

            plantsql = cursor.fetchall()
            this_month = date.month
            gap = plantsql[0][1] if this_month in range(3, 10) else plantsql[0][2]
            next_date = date + datetime.timedelta(days=gap)
            add_data['next_date'] = next_date.strftime("%d-%m-%Y")

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                cursor.close()
                if plant is None:
                    return 'Событие зафиксировано, растение id:{id} полито {date}\n'.format(id=plant_id, date=str(date))
                return 'Событие зафиксировано, растение {plant} полито {date}\n'.format(plant=plant, date=str(date))

            except Error as e:
                return 'Произошла ошибка - ' + str(e) + '\n'

    def add_plant_fertile(plantdata: json):
        global connection
        add_data = {}
        plantdata = json.load(plantdata)
        if 'date' in plantdata:
            date = plantdata['date']
            if type(date) == str and len(date) == 10 and date.find('-') == 2:
                date = datetime.datetime.strptime(date, "%d-%m-%Y").date()

            else:
                return 'Неправильный формат даты. Используйте строку "dd-mm-yyyy".\n'
        else:
            date = datetime.date.today()

        plant = plantdata['name'] if 'name' in plantdata else None
        plant_id = plantdata['id'] if 'id' in plantdata else None

        if plant is None and plant_id is None:
            return 'Не определили растение, которое вы удобрили.\n'

        with connection.cursor() as cursor:
            cursor.execute(
                '''select last_fertiling,fertile_freq_summer, fertile_freq_winter from userplants 
                         where id = "{id}" or plantname = "{name}"'''.format(id=plant_id, name=plant))
            add_data['id'] = plant_id
            add_data['name'] = plant
            add_data['date'] = date.strftime("%d-%m-%Y")
            add_string = '''update userplants set last_fertiling = %(date)s, 
                                    next_fertile= %(next_date)s where id = %(id)s or plantname = %(name)s'''

            plantsql = cursor.fetchall()
            this_month = date.month
            gap = plantsql[0][1] if this_month in range(3, 10) else plantsql[0][2]
            next_date = date + datetime.timedelta(days=gap)
            add_data['next_date'] = next_date.strftime("%d-%m-%Y")

            try:
                cursor.execute(add_string, add_data)
                connection.commit()
                cursor.close()
                if plant is None:
                    return 'Событие зафиксировано, растение id:{id} удобрено {date}\n'.format(id=plant_id,
                                                                                              date=str(date))
                return 'Событие зафиксировано, растение {plant} удобрено {date}\n'.format(plant=plant, date=str(date))

            except Error as e:
                return 'Произошла ошибка - ' + str(e) + '\n'

    def delete_plant(login: str = None, plantname: str = None, **kwargs):
        global connection
        if login is None:
            return "Мы вас не узнали. Укажите ваш логин"
        user_id = Plantchecker.get_user_id(login)
        if type(user_id) == str:
            user_id = 0

        plant_id = kwargs.get("plant_id", default=None) if len(kwargs) !=0 else 0

        with connection.cursor() as cursor:
            cursor.execute('select plantname from userplants where user="{id}" and (plantname="{plantname}" or id={plant_id})'.format(plantname=plantname, id=user_id, plant_id=plant_id))
            plantlist = [''.join(x) for x in cursor.fetchall()]

            if len(plantlist) == 0:
                return "Растение не существует"

            cursor.execute('delete from userplants where user="{id}" and (plantname="{plantname}" or id="{plant_id}")'.format(plantname=plantname, id=user_id, plant_id=plant_id))
            connection.commit()
            cursor.execute('select plantname from userplants where user="{id}" and (plantname="{plantname}" or id={plant_id})'.format(plantname=plantname, id=user_id, plant_id=plant_id))

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

    def delete_user(login: str):
        pass


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
