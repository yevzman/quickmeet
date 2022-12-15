from .data import Data

from amadeus import Client

class Person:
    def __init__(self, city):
        self.city = city

class Solver:
    def __init__(self):
        self.__api_key = "pQzD3NVRAXQjwNFdiQVHMypb96AsxMvL"
        self.__api_secret = "Dj2GZEcwjOumIUYj"
        self.amadeus = Client(
            client_id=str(self.__api_key),
            client_secret=str(self.__api_secret)
        )
        self.data = Data('./api/data.txt')
    
    def _get_flight_offers(self, orig, dest, date):
        response = self.amadeus.shopping.flight_offers_search.get(
            originLocationCode=orig,
            destinationLocationCode=dest,
            departureDate=date,
            adults=1
        )
        return response.data
    
    def _get_cheapest_price(self, orig, dest, date):
        data = self._get_flight_offers(orig, dest, date)
        now = 1000000000.0
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
                try:
                    print(air1[0], air2[0])
                    price = self.get_cheapest_price(air1[0], air2[0], date)
                    if price is not None:
                        any_flights = True
                        print('flight', air1[0], air2[0], date, 'price', price)
                        min_price = min(min_price, price)
                except:
                    continue
        if any_flights:
            return min_price
            #There should be Database update (or should not)
        return None

    def get_cheapest_meeting(self, people: list, date):
#        cities = self.data.get_cities()
        cities = ['Moscow', 'St Petersburg', 'Novosibirsk', 'Ekaterinburg',
                    'Kazan', 'Nizhniy Novgorod', 'Chelyabinsk', 'Krasnojarsk',
                    'Samara', 'Ufa', 'Omsk', 'Krasnodar', 'Voronezh', 'Perm', 'Volgograd']
        result = []
        suitable_city = True
        for city in cities[:2]:
            sum = 0.0
            print('City:', city)
            for person in people:
                min_price = self.get_cheapest_cities_route(person.city, city, date)
                if min_price is not None:
                    sum += min_price
                else:
                    suitable_city = False
            if suitable_city:
                result.append([sum, city])
        result.sort()
        if len(result) > 0:
            return result[0][0], result[0][1]
        return None
