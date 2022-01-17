import pytest
from al_phonebook.lib import Item, Model
from typing import Sequence
from .common import test_tiny_db


@pytest.fixture(scope="session")
def data() -> Sequence[Item]:
    return (
        Item(name="Adam", email="adam@al.com", phone_number=999999999, age=30),
        Item(name="Bruce", email="bruce@al.com", phone_number=123456789, age=40),
        Item(name="Clarisse", email="clarisse@al.com", phone_number=888888888, age=60),
        Item(name="Doug", email="doug@al.com", phone_number=7777777777, age=33),
    )


@pytest.fixture(scope="session")
def models_with_data(data: Sequence[Item]) -> Sequence[Model]:
    """
    Returns a sequence of `Model`s. In case a new Database is added, instantiate it here
    and add to the list. All tests that use `Model` will be tested against each of these databases.
    """
    m = Model(test_tiny_db())
    m.add_items((d.dict() for d in data))
    return [m]

@pytest.fixture(scope="session")
def models_with_data_multiple_workspaces(data: Sequence[Item]) -> Sequence[Model]:
    """
    Returns a sequence of `Model`s. In case a new Database is added, instantiate it here
    and add to the list. All tests that use `Model` will be tested against each of these databases.
    """
    m = Model(test_tiny_db())
    m.add_items((d.dict() for d in data[:3]))
    m.add_items((d.dict() for d in data[2:]), workspace="secondary")
    return [m]
