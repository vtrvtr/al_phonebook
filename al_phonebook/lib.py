import os
from abc import ABC, abstractclassmethod, abstractmethod
from functools import reduce
from pathlib import Path
from typing import Any, Optional, Sequence, Type

from pydantic import BaseModel, EmailStr, constr
from tinydb import TinyDB, where
from tinydb.queries import QueryInstance
from tinydb.storages import MemoryStorage

DictItem = dict[str, Any]
OptionalDictItem = DictItem | None

class Item(BaseModel):
    name: constr(max_length=100, strip_whitespace=True)  # type: ignore
    email: Optional[EmailStr]
    phone_number: Optional[constr(max_length=15, strip_whitespace=True, min_length=8)]  # type: ignore


class DatabasePathError(Exception):
    def __init__(self, path: Path) -> None:
        super().__init__(f"The path {path} is invalid")


def get_database(in_memory: bool = False) -> TinyDB:
    if in_memory:
        return TinyDB(storage=MemoryStorage)

    env_path = os.environ.get("ALPB_DB_PATH")
    if not env_path:
        path = Path(".")
    else:
        path = Path(env_path)
        if not path.is_dir():
            raise DatabasePathError(path)
    return TinyDB(path / ".aldb.json")


class AbcDatabase(ABC):
    @abstractmethod
    def all(self) -> list[DictItem]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, id: int) -> OptionalDictItem:
        raise NotImplementedError()

    @abstractmethod
    def add_item(self, item: Item) -> int:
        raise NotImplementedError()

    @abstractmethod
    def add_items(self, items: Sequence[Item]) -> list[int]:
        raise NotImplementedError()

    @abstractmethod
    def filter(self, filters: DictItem) -> list[DictItem]:
        raise NotImplementedError()


class TinyDBDatabase(AbcDatabase):
    def __init__(self, in_memory: bool = False) -> None:
        self.db = get_database(in_memory)
        super().__init__()

    def all(self) -> list[DictItem]:
        r: list[DictItem] = self.db.all()
        return r

    def get(self, id: int) -> OptionalDictItem: 
        r: OptionalDictItem = self.db.get(doc_id=id)
        return r

    def add_item(self, item: Item) -> int:
        result: int = self.db.insert(item.dict())
        return result

    def add_items(self, items: Sequence[Item]) -> list[int]:
        ids: list[int] = self.db.insert_multiple((i.dict() for i in items))
        return ids

    def filter(self, filters: DictItem) -> list[DictItem]:
        def case_insensitive_query(key: str, value: Any) -> QueryInstance:
            return where(key).test(lambda entry: value.lower())

        query = [
            case_insensitive_query(field_name, field_value)
            for field_name, field_value in filters.items()
        ]

        # TinyDB accepts multiple queries separated by the boolean operator (__and__)
        # we use reduce to combine multiple queries into one
        r: list[dict] = self.db.search(reduce(lambda a, b: a & b, query))
        return r


class Model:
    def __init__(self, database: Type[AbcDatabase] = TinyDBDatabase()) -> None:
        self.database = database

    def all(self) -> list[DictItem]:
        return self.database.all()

    def get(self, id: int) -> DictItem:
        r: DictItem = self.database.get(id=id)
        return r

    def add_item(self, item: Item) -> int:
        result: int = self.database.add_item(item)
        return result

    def add_items(self, items: Sequence[Item]) -> list[int]:
        ids: list[int] = self.database.add_items(items)
        return ids

    def filter(self, filters: DictItem) -> list[DictItem]:
        result: list[DictItem] = self.database.filter(filters)
        return result
