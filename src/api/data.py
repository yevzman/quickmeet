f = open('./api/data.txt')

class Data:
    def __init__(self, filename):
        self.data = {}
        f = open(filename)
        for i in range(143):
            arr = f.readline().split("\n")[0].split('\t')
            iata = arr[0]
            airport = arr[1]
            city = arr[2]
            if self.data.get(city) is None:
                self.data[city] = []
            self.data[city].append([iata, airport])
        f.close()
    
    def get_airports(self, city):
        return self.data.get(city)

    def get_cities(self):
        return self.data.keys()
