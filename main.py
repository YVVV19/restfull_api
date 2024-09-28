from typing import Optional
from decimal import Decimal
from sqlmodel import(
    SQLModel,
    Field,
    create_engine,
    Session,
    ForeignKey,
    select,
)
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException
from uvicorn import run

class AutoId(SQLModel):
    id: [int] = Field(
        primary_key=True,
        default=None
    )


class Model(SQLModel, table=True):
    name:str


class Car(AutoId, table=True):
    name: str
    model_id: Optional[int] = Field()
    model: str
    money: Decimal = Field(default=0, max_digits=15)


class CarCreate(AutoId):
    name: str
    model: str
    money: Decimal = Field(default=0, max_digits=15)


engine = create_engine("sqlite:///my_db.db", echo=True)
session = Session(bind=engine)
SESSION = sessionmaker(bind=engine)
app = FastAPI(debug=True)


@app.get("/car/list", response_model=list[Car])
def car_list():
    response = session.scalars(select(Car).where(Car.name == name)).one_or_none
    return response


@app.get("/car/{name}", response_model=list[Car])
def car_get(name:str):
    response = session.scalars(select(Car).where(Car.name == name)).one_or_none
    return response

@app.put("/car/edit", response_model=list[dict])
def car_put(car:Car):
    with SESSION.begin() as session:
        query = select(Car).where(Car.id == car.id)
        car_item = session.scalars(query).one_or_none()
        if car_item:
            car_item.name = car.name
            car_item.model = car.model
            car_item.money = car.money
            return{"ok":True}
        else:
            raise HTTPException(status_code=404, detail="Car not found")


@app.delete("/car/delete", response_model=list[dict])
def car_delete(car:Car):
    with SESSION.begin() as session:
        query = select(Car).where(Car.id == car.id)
        car_item = session.scalars(query).one_or_none()
        if car_item:
            car_item.name = car.name
            car_item.model = car.model
            car_item.money = car.money
            return{"ok":True}
        else:
            raise HTTPException(status_code=404, detail="Car not found")


def migrate():
    volkswagen = Model(name="Volkswagen")
    nissan = Model(name="Nissan")
    opel = Model(name="Opel")
    models = [volkswagen, nissan, opel]
    session.add_all(models)
    session.commit()


def main():
    migrate()
    run(
        app=app
    )

main()