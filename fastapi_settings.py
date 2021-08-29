from fastapi import FastAPI
from plantchecker import Plantchecker
import uvicorn
import json, datetime, os, configparser
from pyd_models import Adddata, Adddate


app = FastAPI(title='Plantchecker API')
pch = Plantchecker()

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
async def mainpage():
    return "Plantchecker"

@app.get("/plantlist",
         description='Возвращает список растений, ранее добавленных пользователей, с актуальными характеристиками',
         response_description='Json c перечнем растений')
async def plantlist(login:str = None):
    try:
        plantlist = pch.checkUserPlants(login)
    except IndexError:
        raise HTTPException(404, "Что-то пошло не так")
    return plantlist

@app.put("/addwater",
          description='Добавляет новую дату полива растения и обновляет характеристики',
          response_description="Результат обновления даты полива",
          )
def addwater(data:Adddata):
    try:
        login = data.login
        date = data.date
        plant = data.plant
        water = addUserWatering()
    except IndexError:
        raise HTTPException(404, "Что-то пошло не так")
    return water




if __name__ == '__main__':
    uvicorn.run('fastapi_settings:app', host='127.0.0.1', port=5000, reload=True)