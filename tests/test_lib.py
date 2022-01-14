import os
import tempfile
from pathlib import Path

import pytest
from al_phonebook.lib import (
    DatabasePathError,
    Item,
    TinyDBDatabase,
    get_database,
    Model,
)
from hypothesis import strategies as st, given


def model() -> Model:
    db = TinyDBDatabase(in_memory=True)
    m = Model(db)
    return m


@pytest.fixture
def data():
    return (
        Item(name="Adam", email="adam@al.com"),
        Item(name="Bruce", email="bruce@al.com"),
        Item(name="Clarisse", email="clarisse@al.com"),
        Item(name="Doug", email="doug@al.com"),
    )


@pytest.fixture
def model_with_data(data):
    db = TinyDBDatabase(in_memory=True)
    m = Model(db)
    m.database.add_items(data)
    return m


def test_start_db() -> None:
    db = get_database(in_memory=True)
    assert db is not None


def test_start_db_from_custom_path() -> None:
    some_path = tempfile.mkdtemp()
    os.environ["ALPB_DB_PATH"] = some_path
    db = get_database()
    assert Path(db.storage._handle.name).parent.as_posix().replace(
        "\\", "/"
    ) == some_path.replace("\\", "/")
    os.environ["ALPB_DB_PATH"] = ""


def test_start_db_invalid_custom_path() -> None:
    os.environ["ALPB_DB_PATH"] = "foo"
    with pytest.raises(DatabasePathError):
        db = get_database()


@given(name=st.text(min_size=5, max_size=100))
def test_add_one_item(name) -> None:
    m = model()
    item = Item(name=name)
    r = m.add_item(item)
    search = m.get(id=r)
    assert search == item


@given(name=st.text(min_size=5, max_size=100), email=st.emails())
def test_filter_item_single_parms(name, email) -> None:
    m = model()
    i = Item(name=name, email=email)
    m.add_item(i)
    assert i.dict() in m.database.filter({"email": email})


@given(name=st.text(min_size=5, max_size=100), email=st.emails())
def test_filter_item_multiple_parms(name, email) -> None:
    m = model()
    i = Item(name=name, email=email.upper())
    m.database.add_item(i)
    assert i.dict() in m.database.filter({"email": email, "name": name})


def test_add_items() -> None:
    m = model()
    names = ["a", "b", "c", "d", "e"]
    items = [Item(name=n) for n in names]
    r = m.add_items(items)
    assert r == [1, 2, 3, 4, 5]


def test_list_item(model_with_data) -> None:
    assert model_with_data.get(id=1) == {
        "name": "Adam",
        "email": "adam@al.com",
        "phone_number": None,
    }

def test_list_all_items(model_with_data, data) -> None:
    data = (
        Item(name="Adam", email="adam@al.com"),
        Item(name="Bruce", email="bruce@al.com"),
        Item(name="Clarisse", email="clarisse@al.com"),
        Item(name="Doug", email="doug@al.com"),
    )
    assert model_with_data.all() == [i.dict() for i in data]


def test_add_custom_field() -> None:
    assert False


def test_add_custom_formatter() -> None:
    assert False
