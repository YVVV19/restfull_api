from aiohttp.client import ClientSession
from asyncio import run


base_url = "http://localhost:8000/"
endpoints = {
    "cars": base_url + "car/list",
    "car": base_url + "car/{name}",
    "car_create": base_url + "car/create",
    "car_edit": base_url + "car/edit",
    "car_delete": base_url + "car/delete",
}

async def create_car():
    name = input("Enter the name:\t")
    model = input("Enter the model:\t")
    money = input("Enter the money amount:\t")
    url = endpoints.get("car_create", "")
    async with ClientSession() as session:
        async with session.post(
            url=url,
            json={
                "name": name,
                "model": model,
                "money": money,
            },
        ) as req:
            result = await req.json()
            print(f"{result=}")


def main():
    run(create_car(), debug=True)


main()