from mysql.connector import connect, Error
import json


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
    pass
    # try:
    #     with connect(
    #             host="localhost",
    #             user='admin',
    #             password='Plantchecker1!',
    #             database='plantcheckerDB'
    #     ) as connection:
    #         table_query = """
    #             select id from users
    #             where login = login
    #         """
    #
    #         with connection.cursor() as cursor:
    #             user_id = cursor.execute(table_query)
    #             print(user_id)
    # except Error as e:
    #     print(e)


def addUserWater():
    pass

def addUserFertils():
    pass

def addUser():
    pass

# print(addUserPlants('linlynx','Монстера на кухне','Монстера','26.07.2021'))
try:
    with connect(
            host="localhost",
            user='admin',
            password='Plantchecker1!',
            database='plantcheckerDB'
    ) as connection:
        table_query = """ 
                select id from users

            """

        with connection.cursor() as cursor:
            cursor.execute('select id from users where login = "linlynx"')
            print(cursor.fetchone())

except Error as e:
    print(e)
