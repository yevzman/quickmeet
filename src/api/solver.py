from .data import Data

from amadeus import Client
import logging
import os

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Person:
    def __init__(self, city):
        self.city = city

    def __str__(self):
        return f'[City: {self.city}]'


class Solver:
    def __init__(self, path='./api/data.txt'):
        self.__api_key = os.getenv('API_KEY') # "pQzD3NVRAXQjwNFdiQVHMypb96AsxMvL"
        self.__api_secret = os.getenv('API_SECRET') # "Dj2GZEcwjOumIUYj"
        self.amadeus = Client(
            client_id=str(self.__api_key),
            client_secret=str(self.__api_secret)
        )
        self.data = Data(path)
    
    def _get_flight_offers(self, orig, dest, date):
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=orig,
                destinationLocationCode=dest,
                departureDate=date,
                adults=1
            )
            return response.data
        except:
            return None
    
    def _get_cheapest_price(self, orig, dest, date):
        data = self._get_flight_offers(orig, dest, date)
        now = 1000000000.0
        if data is not None:
            for item in data:
                price = float(item['price']['total'])
                now = min(now, price)
            if len(data) == 0:
                return None
        return now

    def get_cheapest_cities_route(self, orig_city, dest_city, date):
        if orig_city == dest_city:
            return 0.0
        airports1 = self.data.get_airports(orig_city)
        airports2 = self.data.get_airports(dest_city)
        min_price = 1000000000.0
        any_flights = False
        for air1 in airports1:
            for air2 in airports2:
                price = self._get_cheapest_price(air1[0], air2[0], date)
                logger.debug(f'From Airport: {str(air1[0])} To Airport: {str(air2[0])} Price: {price}')
                if price is not None:
                    any_flights = True
                    min_price = min(min_price, price)
        if any_flights:
            return min_price
            #There should be Database update (or should not)
        return None

    def get_cheapest_meeting(self, people: list, date):
#        cities = self.data.get_cities()
        logger.info(f'Find cheapest flight for { " ".join(map(lambda x: str(x), people)) } in date {date}')
        cities = ['Moscow', 'St Petersburg', 'Novosibirsk', 'Ekaterinburg',
                    'Kazan', 'Nizhniy Novgorod', 'Chelyabinsk', 'Krasnojarsk',
                    'Samara', 'Ufa', 'Omsk', 'Krasnodar', 'Voronezh', 'Perm', 'Volgograd']
        result = []
        suitable_city = True
        for city in cities:
            sum = 0.0
            for person in people:
                min_price = self.get_cheapest_cities_route(person.city, city, date)
                if min_price is not None:
                    logger.debug(f'From {str(person.city)}  To {str(city)}  Price: {str(min_price)}')
                    sum += min_price
                else:
                    suitable_city = False
            if suitable_city:
                result.append([sum, city])
        result.sort()
        if len(result) > 0:
            return result[0][0], result[0][1]
        return None
