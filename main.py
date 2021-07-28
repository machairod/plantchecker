from mysql.connector import connect, Error
import json, datetime

def connection():
    connect(
        host="localhost",
        user='admin',
        password='Plantchecker1!',
        database='plantcheckerDB'
    )

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

def addUserPlants(login, plantname, plantspec, lastwatering):
    with connect(
                host="localhost",
                user='admin',
                password='Plantchecker1!',
                database='plantcheckerDB'
        ) as connection:
            with connection.cursor() as cursor:
                        cursor.execute('select id from users where login = "linlynx"')
                        user_id = cursor.fetchone()[0]
    with open ('plantspecies.json','r') as plantspecies:

    print(plantname)
    print(user_id)
    print(plantspec)
    print(lastwatering)



def addUserWater():
    pass

def addUserFertils():
    pass

def addUser():
    pass

# print(str(datetime.date.today()))

addUserPlants('linlynx','Монстера на кухне','Монстера','26.07.2021')
# try:
#     with connect(
#             host="localhost",
#             user='admin',
#             password='Plantchecker1!',
#             database='plantcheckerDB'
#     ) as connection:
#
#         with connection.cursor() as cursor:
#             cursor.execute('select id from users where login = "linlynx"')
#             user_id = cursor.fetchone()[0]
#             print(user_id)
#
# except Error as e:
#     print(e)