from mysql.connector import connect, Error
import json, datetime

def userLogin():
    pass

def checkUserPlants(user):
    userid = user
    try:
        with connect(
                host="localhost",
                user='admin',
                password='Plantchecker1!',
                database='plantcheckerDB'
        ) as connection:
            table_query = """ 
                select * from userplants
                where user = userid
            """

            with connection.cursor() as cursor:
                cursor.execute(table_query)
                connection.commit()


    except Error as e:
        print(e)

def addUserPlants(login, plant_name, plant_spec, last_water):
    plant_data={}
    with open('plantspecies.json', 'r') as plantspecies:
        plant_dict = json.load(plantspecies)
    plant_spec = plant_spec.lower()
    if plant_spec not in plant_dict:
        return 'Не опознали вид растения'
    last_water = [int(x) for x in last_water.split('.')]
    if int(last_water[0])>31 or int(last_water[1])>12 or len(last_water)>3:
        return 'Некорректная дата'
    last_water.reverse()
    plant_data["last_water"] = datetime.date(last_water[0],last_water[1],last_water[2])
    plant_data["last_fertile"] = plant_data["last_water"]
    plant_data['plantspec'] = plant_spec
    plant_data['light'] = plant_dict[plant_spec]['light']
    plant_data['water_freq_summer'] = plant_dict[plant_spec]['water_summer']
    plant_data['water_freq_winter'] = plant_dict[plant_spec]['water_winter']
    plant_data["fertile_freq_summer"] = plant_dict[plant_spec]['fertile_summer']
    plant_data["fertile_freq_winter"] = plant_dict[plant_spec]['fertile_winter']
    plant_data["spraying"] = plant_dict[plant_spec]['spraying']
    plant_data["plantname"] = plant_name

    add_plant = "insert into userplants (user, plantname, plantspec, last_water, last_fertile, water_freq_summer, water_freq_winter, fertile_freq_summer, fertile_freq_winter, spraying, light) values (%(user)s, %(plantname)s, %(plantspec)s, %(last_water)s, %(last_fertile)s, %(water_freq_summer)s, %(water_freq_winter)s, %(fertile_freq_summer)s, %(fertile_freq_winter)s, %(spraying)s, %(light)s)"

    with connect(
            host="localhost",
            user='admin',
            password='Plantchecker1!',
            database='plantcheckerDB'
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute('select id from users where login="{user}"'.format(user = login))
            user = cursor.fetchall()
            if len(user) == 0:
                return 'Не нашли такого пользователя'
            plant_data['user'] = user[0][0]

            try:
                cursor.execute(add_plant,plant_data)
                connection.commit()
                return('Растение добавлено в ваш список')
            except Error as e: print(e)

def addUserWater():
    pass

def addUserFertils():
    pass

def addUser():
    pass

print(addUserPlants('linlynx','Большая монстера','Монстера','26.07.2021'))

#
# try:
#     with connect(
#             host="localhost",
#             user='admin',
#             password='Plantchecker1!',
#             database='plantcheckerDB'
#     ) as connection:
#
#         with connection.cursor() as cursor:
#             cursor.execute('alter table userplants modify column last_fertile date')
#             connection.commit()
#
# except Error as e: print(e)