from datetime import datetime
import os
import time

from db.flights_db import FlightsDB
from api.solver import Person, Solver

database: FlightsDB = None
solver: Solver = None

def is_update_need() -> bool:
    global database

    assert database is not None
    flights = database.get_all_flights()
    if len(flights) == 0:
        return True

    timestamp = datetime.timestamp(datetime.now())
    print(flights)
    if timestamp - round(flights[0][-1]) > 2400:
        return True
    return False


def run_update():
    global database
    cities = ['Moscow', 'St Petersburg', 'Novosibirsk', 'Ekaterinburg',
              'Kazan', 'Nizhniy Novgorod', 'Chelyabinsk', 'Krasnojarsk',
              'Samara', 'Ufa', 'Omsk', 'Krasnodar', 'Voronezh', 'Perm', 'Volgograd']
    n = len(cities)
    timestamp = datetime.timestamp(datetime.now())

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            print('Update flight: ', cities[i], '-', cities[j])
            airs1 = solver.data.get_airports(cities[i])
            airs2 = solver.data.get_airports(cities[j])
            try:
                for air1 in airs1:
                    for air2 in airs2:
                        print('UPD airports:', air1, air2)
                        price = solver.get_cheapest_price(air1[0], air2[0], '2022-12-23')
                        if price is not None:
                            print('Success')
                            database.add_or_update_flight(air1[0], air2[0], '2022-12-23', price, str(timestamp))
            except:
                continue


if __name__ == '__main__':
    # Note: updater should be run from ./src directory
    recreate = False
    if not os.path.exists('./db/flights_data.db'):
        recreate = True
    database = FlightsDB('./db/flights_data.db')
    solver = Solver()

    # database.recreate_table()

    if recreate:
        database.recreate_table()

    while True:
        if is_update_need():
            run_update()
        time.sleep(2400)
