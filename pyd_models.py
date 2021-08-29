from pydantic import BaseModel
import datetime

class Adddate(BaseModel):
    strdate: str

class Adddata(BaseModel):
    login: str
    date: datetime.datetime.strptime(Adddate.strdate, "%d.%m.%Y").date() = datetime.date.today()
    plant: str