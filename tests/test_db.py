import pytest
from src.db.bot_db import DBStatus, UserGroupDB
from src.db.flights_db import FlightsDB

GROUP_NUMBER = 4
USER_NUMBER = 8


@pytest.fixture(scope="module")
def get_user_group_db():
    yield UserGroupDB(":memory:")


def test_recreate_table_user_group(get_user_group_db):
    status = get_user_group_db.recreate_table()
    assert status == DBStatus.SUCCESS


def test_add_group(get_user_group_db):
    for i in range(1, GROUP_NUMBER + 1):
        group_name = f"test{i}"
        group_id, status = get_user_group_db.add_group(group_name)
        assert status == DBStatus.SUCCESS
        assert group_id == i


def test_check_access(get_user_group_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        assert get_user_group_db._check_access(group_id, group_name)
    for bad_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{bad_id - 1}"
        assert not get_user_group_db._check_access(bad_id, group_name)
    for group_id in range(1, GROUP_NUMBER + 1):
        bad_name = f"test{group_id + 1}"
        assert not get_user_group_db._check_access(group_id, bad_name)


def test_set_group_dates(get_user_group_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        flight = f"0{group_id}/01/1488"
        arrival = f"0{group_id}/02/1488"
        status = get_user_group_db.set_group_dates(group_id, group_name, flight, arrival)
        assert status == DBStatus.SUCCESS


def test_get_all_groups(get_user_group_db):
    all_groups = get_user_group_db.get_all_groups()
    assert len(all_groups) == GROUP_NUMBER
    for group_id, group in enumerate(all_groups):
        assert len(group) == 4
        assert group[0] == group_id + 1
        assert group[1] == f"test{group_id + 1}"
        assert group[2] == f"0{group_id + 1}/01/1488"
        assert group[3] == f"0{group_id + 1}/02/1488"


def test_add_user(get_user_group_db):
    for user_id in range(USER_NUMBER):
        group_id = user_id // 2 + 1
        group_name = f"test{group_id}"
        user_name = f"name{user_id}"
        city = f"old_city{user_id}"
        status = get_user_group_db.add_user(group_id, group_name, user_name, city)
        assert status == DBStatus.SUCCESS

        status = get_user_group_db.add_user(group_id, group_name, user_name, city)
        assert status == DBStatus.ALREADY_EXIST


def test_update_user(get_user_group_db):
    for user_id in range(USER_NUMBER // 2):
        group_id = user_id // 2 + 1
        group_name = f"test{group_id}"
        user_name = f"name{user_id}"
        city = f"new_city{user_id}"
        status = get_user_group_db.update_user(group_id, group_name, user_name, city)
        assert status == DBStatus.SUCCESS


def test_view_group(get_user_group_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        group = get_user_group_db.view_group(group_id, group_name)
        assert len(group) == 2
        for i, user in enumerate(group):
            user_id = (group_id - 1) * 2 + i
            user_name = f"name{user_id}"
            city = f"new_city{user_id}"
            if user_id // 4:
                city = f"old_city{user_id}"
            assert user[0] == user_name
            assert user[1] == city


def test_get_all_users(get_user_group_db):
    all_users = get_user_group_db.get_all_users()
    assert len(all_users) == USER_NUMBER
    for user_id, user in enumerate(all_users):
        group_id = user_id // 2 + 1
        user_name = f"name{user_id}"
        city = f"new_city{user_id}"
        if user_id // 4:
            city = f"old_city{user_id}"
        assert user == (user_name, city, group_id)


def test_delete_group(get_user_group_db):
    assert len(get_user_group_db.get_all_groups()) == 4
    status = get_user_group_db.delete_group(4, "test4")
    assert status == DBStatus.SUCCESS
    assert len(get_user_group_db.get_all_groups()) == 3
    status = get_user_group_db.delete_group(4, "test4")
    assert status == DBStatus.BAD_ACCESS


def test_delete_user(get_user_group_db):
    assert len(get_user_group_db.get_all_users()) == USER_NUMBER - 2
    status = get_user_group_db.delete_user(1, "test1", "name1")
    assert status == DBStatus.SUCCESS
    assert len(get_user_group_db.get_all_users()) == USER_NUMBER - 3


@pytest.fixture(scope="module")
def get_flight_db():
    yield FlightsDB(":memory:")


def test_recreate_table_flight(get_flight_db):
    status = get_flight_db.recreate_table()
    assert status == DBStatus.SUCCESS


def test_add_flight(get_flight_db):
    status = get_flight_db.add_or_update_flight("test_orig", "test_dest", "test_flight_date", 228, "test_last_upd")
    assert status == DBStatus.SUCCESS
    assert get_flight_db.get_flight_price("test_orig", "test_dest") == 228
    assert get_flight_db.get_flight_date("test_orig", "test_dest") == "test_flight_date"
    assert get_flight_db.get_flight_last_upd("test_orig", "test_dest") == "test_last_upd"
    assert len(get_flight_db.get_all_flights()) == 1

    status = get_flight_db.add_or_update_flight("test_orig2", "test_dest2", "test_flight_date2", 322, "test_last_upd2")
    assert status == DBStatus.SUCCESS
    assert get_flight_db.get_flight_price("test_orig2", "test_dest2") == 322
    assert get_flight_db.get_flight_date("test_orig2", "test_dest2") == "test_flight_date2"
    assert get_flight_db.get_flight_last_upd("test_orig2", "test_dest2") == "test_last_upd2"
    assert len(get_flight_db.get_all_flights()) == 2


def test_update_flight(get_flight_db):
    status = get_flight_db.add_or_update_flight("test_orig", "test_dest", "test_flight_date_c", 1488, "test_last_upd_c")
    assert status == DBStatus.SUCCESS
    assert get_flight_db.get_flight_price("test_orig", "test_dest") == 1488
    assert get_flight_db.get_flight_date("test_orig", "test_dest") == "test_flight_date_c"
    assert get_flight_db.get_flight_last_upd("test_orig", "test_dest") == "test_last_upd_c"
    assert len(get_flight_db.get_all_flights()) == 2


def test_bad_query(get_flight_db):
    assert get_flight_db.get_flight_price("non exist", "non exist") is None
    assert get_flight_db.get_flight_date("non exist", "non exist") is None
    assert get_flight_db.get_flight_last_upd("non exist", "non exist") is None
