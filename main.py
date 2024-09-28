from typing import Optional
from decimal import Decimal
from sqlmodel import(
    Relationship,
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
    id: Optional[int] = Field(
        primary_key=True,
        default=None
    )


class Model(SQLModel, table=True):
    name:str


class Car(AutoId, table=True):
    name: str
    model_id: Optional[int] = Field(
        default=None,
        foreign_key=f"{Model.__name__.lower()}.id"
    )
    model: Model = Relationship()
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
    response = session.scalars(select(Car))
    return response


@app.get("/car/{name}", response_model=list[Car])
def car_get(name:str):
    response = session.scalars(select(Car).where(Car.name == name)).one_or_none
    return response


@app.post("/car/create")
def car_create(car: CarCreate):
    with SESSION.begin() as session:
        query = select(Model).where(Model.name == car.name)
        model = (
            session.scalars(query).one_or_none()
            or session.scalars(select(Model)).first()
        )
        if not model:
            raise HTTPException(status_code=404, detail="Name not found")
        session.add(
            Car(
                name=car.name,
                model=car.model,
                money=car.money,
            )
        )
        return{"ok":True}


@app.put("/car/edit", response_model=list[dict])
def car_edit(car:Car):
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
            session.delete(car_item)
            return{"ok":True}
        else:
            raise HTTPException(status_code=404, detail="Car not found")


def migrate():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    volkswagen1 = Model(name="Volkswagen")
    nissan2 = Model(name="Nissan")
    opel3 = Model(name="Opel")
    toyota4 = Model(name="Toyota")
    models = [volkswagen1, nissan2, opel3, toyota4]
    with SESSION.begin()as session:
        session.add_all(models)
        session.flush()
        car1 = Model(
            name="Volkswagen",
            model=volkswagen1,
            money=Decimal("200.00")
        )
        car2 = Model(
            name="Nissan",
            model=nissan2,
            money=Decimal("300.00")
        )
        Car.model_validate(car2)
        session.add_all(
            (
                car1,
                car2,
            )
        )





def main():
    migrate()
    run(
        app=app,
    )

main()