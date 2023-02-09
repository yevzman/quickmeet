import pytest
from src.api.solver import Solver

@pytest.fixture
def mock_data():
    # Mock data for external API call
    return {
        'orig_city': 'Moscow',
        'dest_city': 'Kazan',
        'date': '2023-02-07'
    }

def test_get_cheapest_cities_route(mock_data):
    solver = Solver(path='./src/api/data.txt')
    result = solver.get_cheapest_cities_route(mock_data['orig_city'], mock_data['dest_city'], mock_data['date'])
    assert (result is None) or \
           float(result)

if __name__ == '__main__':
    pytest.main()