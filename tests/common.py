from al_phonebook.lib import Item, Model, TinyDBDatabase
from typing import Sequence


class TinyDBTest(TinyDBDatabase):
    def __init__(self) -> None:
        self.db = super().get_database(path=None, in_memory=True)

def test_tiny_db():
    return TinyDBTest()

def models() -> Sequence[Model]:
    db = TinyDBTest()
    m = Model(db)
    return [m]
