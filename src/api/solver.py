from data import Data

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
    
    def get_flight_offers(self, orig, dest, date):
        response = self.amadeus.shopping.flight_offers_search.get(
            originLocationCode=orig,
            destinationLocationCode=dest,
            departureDate=date,
            adults=1
        )
        return response.data
    
    def get_cheapest_price(self, orig, dest, date):
        data = self.get_flight_offers(orig, dest, date)
        now = 1000000000.0
        for item in data:
            price = float(item['price']['total'])
            now = min(now, price)
        return now

    def get_cheapest_meeting(self, people, date):
        d = Data('data.txt')
#        cities = d.get_cities()
        cities = ['Moscow', 'St Petersburg', 'Novosibirsk', 'Ekaterinburg',
                    'Kazan', 'Nizhniy Novgorod', 'Chelyabinsk', 'Krasnojarsk',
                    'Samara', 'Ufa', 'Omsk', 'Krasnodar', 'Voronezh', 'Perm', 'Volgograd']
        result = []
        for city in cities[:2]:
            sum = 0.0
            for person in people:
                if person.city == city:
                    continue
                airports1 = d.get_airports(person.city)
                airports2 = d.get_airports(city)
                min_price = 1000000000.0
                for air1 in airports1:
                    for air2 in airports2:
                        try:
                            print(air1[0], air2[0])
                            price = self.get_cheapest_price(air1[0], air2[0], date)
                            min_price = min(min_price, price)
                        except:
                            continue
                sum += min_price
            result.append([sum, city])
        result.sort()
        if len(result) > 0:
            return result[0][1]
        return None
