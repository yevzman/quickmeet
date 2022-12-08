import pytest
import sqlite3
from db.bot_db import DBStatus, BotDB

GROUP_NUMBER = 4
USER_NUMBER = 8


@pytest.fixture(scope="module")
def get_db():
    yield BotDB(":memory:")


def test_recreate_table(get_db):
    status = get_db.recreate_table()
    assert status == DBStatus.SUCCESS


def test_add_group(get_db):
    for i in range(1, GROUP_NUMBER + 1):
        group_name = f"test{i}"
        group_id, status = get_db.add_group(group_name)
        assert status == DBStatus.SUCCESS
        assert group_id == i


def test_check_access(get_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        assert get_db._check_access(group_id, group_name)
    for bad_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{bad_id - 1}"
        assert not get_db._check_access(bad_id, group_name)
    for group_id in range(1, GROUP_NUMBER + 1):
        bad_name = f"test{group_id + 1}"
        assert not get_db._check_access(group_id, bad_name)


def test_set_group_dates(get_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        flight = f"0{group_id}/01/1488"
        arrival = f"0{group_id}/02/1488"
        status = get_db.set_group_dates(group_id, group_name, flight, arrival)
        assert status == DBStatus.SUCCESS


def test_get_all_groups(get_db):
    all_groups = get_db.get_all_groups()
    assert len(all_groups) == GROUP_NUMBER
    for group_id, group in enumerate(all_groups):
        assert len(group) == 4
        assert group[0] == group_id + 1
        assert group[1] == f"test{group_id + 1}"
        assert group[2] == f"0{group_id + 1}/01/1488"
        assert group[3] == f"0{group_id + 1}/02/1488"


def test_add_user(get_db):
    for user_id in range(USER_NUMBER):
        group_id = user_id // 2 + 1
        group_name = f"test{group_id}"
        user_name = f"name{user_id}"
        city = f"old_city{user_id}"
        status = get_db.add_user(group_id, group_name, user_name, city)
        assert status == DBStatus.SUCCESS

        status = get_db.add_user(group_id, group_name, user_name, city)
        assert status == DBStatus.ALREADY_EXIST


def test_update_user(get_db):
    for user_id in range(USER_NUMBER // 2):
        group_id = user_id // 2 + 1
        group_name = f"test{group_id}"
        user_name = f"name{user_id}"
        city = f"new_city{user_id}"
        status = get_db.update_user(group_id, group_name, user_name, city)
        assert status == DBStatus.SUCCESS


def test_view_group(get_db):
    for group_id in range(1, GROUP_NUMBER + 1):
        group_name = f"test{group_id}"
        group = get_db.view_group(group_id, group_name)
        assert len(group) == 2
        for i, user in enumerate(group):
            user_id = (group_id - 1) * 2 + i
            user_name = f"name{user_id}"
            city = f"new_city{user_id}"
            if user_id // 4:
                city = f"old_city{user_id}"
            assert user[0] == user_name
            assert user[1] == city


def test_get_all_users(get_db):
    all_users = get_db.get_all_users()
    assert len(all_users) == USER_NUMBER
    for user_id, user in enumerate(all_users):
        group_id = user_id // 2 + 1
        user_name = f"name{user_id}"
        city = f"new_city{user_id}"
        if user_id // 4:
            city = f"old_city{user_id}"
        assert user == (user_name, city, group_id)


def test_delete_group(get_db):
    assert len(get_db.get_all_groups()) == 4
    status = get_db.delete_group(4, "test4")
    assert status == DBStatus.SUCCESS
    assert len(get_db.get_all_groups()) == 3
    status = get_db.delete_group(4, "test4")
    assert status == DBStatus.BAD_ACCESS


def test_delete_user(get_db):
    assert len(get_db.get_all_users()) == USER_NUMBER - 2
    status = get_db.delete_user(1, "test1", "name1")
    assert status == DBStatus.SUCCESS
    assert len(get_db.get_all_users()) == USER_NUMBER - 3
