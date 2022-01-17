from collections import defaultdict
import os
from abc import ABC, abstractmethod, abstractproperty
from functools import reduce
from pathlib import Path
from typing import Any, Optional, Sequence, Type
import inspect

from pydantic import (
    BaseModel,
    EmailStr,
    constr,
    PositiveInt,
    ValidationError,
    create_model,
)
from tinydb import TinyDB, where
from tinydb.queries import QueryInstance
from tinydb.storages import MemoryStorage
from .constants import CONSTANTS
from .types import DictItem, PathLike, OptionalDictItem


class Item(BaseModel):
    name: constr(max_length=100, strip_whitespace=True)  # type: ignore
    address: Optional[constr(max_length=100, strip_whitespace=False)]  # type: ignore
    email: Optional[EmailStr]
    phone_number: Optional[constr(max_length=15, strip_whitespace=True, min_length=8)]  # type: ignore
    age: Optional[PositiveInt]

def convert_fields_to_optional(parent_class: Type[BaseModel]):
    """Given a parent Pydantic model, create a new one with all the fields being optionals
    This only works for models that are not nested."""
    child_class = create_model("InItem", __base__=parent_class)
    for key in child_class.__fields__:
        child_class.__fields__.get(key).required = False
    return child_class


def create_out_item(item_schema: Type[Item]) -> Type[Item]:
    """Given a `item_schema` Pydantic model, creates a new one with an additional field `id`"""
    return create_model("OutItem", id=(PositiveInt, ...), __base__=item_schema)


class SchemaDefitinionError(Exception):
    def __init__(self, path: PathLike) -> None:
        super().__init__(
            f"Couldn't load `Item` from {path}. Pydantic model must be named `Item`. Aborting..."
        )


class SchemaLoadingError(Exception):
    def __init__(self, path: PathLike) -> None:
        super().__init__(
            f"Couldn't load `Item` from {path}. Supported extensions are: .py, .yaml. Aborting..."
        )


class DatabasePathError(Exception):
    def __init__(self, path: PathLike) -> None:
        super().__init__(f"The path {path} is invalid.")


class AbcDatabase(ABC):

    @abstractproperty
    def id_field_name(self) -> str:
        raise NotImplementedError()

    #TODO: #7 All should return a generator
    @abstractmethod
    def all(self) -> Sequence[DictItem]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, id: int) -> OptionalDictItem:
        raise NotImplementedError()

    @abstractmethod
    def add_item(self, item: Item) -> int:
        raise NotImplementedError()

    @abstractmethod
    def add_items(self, items: Sequence[Item]) -> Sequence[int]:
        raise NotImplementedError()

    @abstractmethod
    def filter(self, filters: DictItem, **kwargs) -> Sequence[DictItem]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, id: int, update: DictItem) -> Optional[int]:
        raise NotImplementedError()


def poorman_fulltext_filter(key: str, value: Any) -> QueryInstance:
    return where(key).test(
        lambda entry: str(value).lower().strip() in str(entry).lower()
        if entry
        else False
    )


def case_insensitive_filter(key: str, value: Any) -> QueryInstance:
    return where(key).test(
        lambda entry: str(value).lower().strip() == str(entry).lower()
        if entry
        else False
    )


class TinyDBDatabase(AbcDatabase):
    def __init__(self, path: PathLike) -> None:
        self.db = TinyDBDatabase.get_database(path, False)
        self.path = Path(path)
        super().__init__()

    @property
    def id_field_name(self) -> str:
        return "doc_id"

    def all(self) -> Sequence[DictItem]:
        r: Sequence[DictItem] = self.db.all()
        r: dict[str, Any] = defaultdict(list)
        for table_name in self.db.tables():
            for entry in self.db.table(table_name):
                r[table_name].append(entry)
        return r

    def get(self, id: int, workspace: Optional[str] = None) -> OptionalDictItem:
        if workspace:
            r: OptionalDictItem = self.db.table(workspace).get(doc_id=id)
        else:
            r: OptionalDictItem = self.db.get(doc_id=id)
        return r

    def add_item(self, item: DictItem, workspace: Optional[str] = None) -> int:
        if workspace:
            result: int = self.db.table(workspace).insert(item.dict())
        else:
            result: int = self.db.insert(item.dict())
        return result

    def add_items(
        self, items: Sequence[DictItem], workspace: Optional[str] = None
    ) -> Sequence[int]:
        ids = []
        for item in items:
            ids.append(self.add_item(item, workspace=workspace))
        return ids

    def filter(
        self, filters: DictItem, exact: bool = False, workspace: Optional[str] = None
    ) -> Sequence[DictItem]:
        """Returns a subset of the items in the phonebook. If exact is True
        only returns exact matches. By default checks if the values of `filters` are in the
        entries."""
        # TODO: #8 Add better search support for various types

        items: Sequence[DictItem] = filters.items()

        if exact:
            query = [
                where(field_name) == field_value for field_name, field_value in items
            ]
        else:
            query = [
                poorman_fulltext_filter(field_name, field_value)
                for field_name, field_value in items
            ]
        if workspace:
            table = self.db.table(workspace)
        else:
            table = self.db

        # TinyDB accepts multiple queries separated by the boolean operator (__and__)
        # we use reduce to combine multiple queries into one
        r: Sequence[dict] = table.search(reduce(lambda a, b: a & b, query))
        return r

    def update(
        self, id: int, update: DictItem, workspace: Optional[str] = None
    ) -> Optional[int]:
        if workspace:
            table = self.db.table(workspace)
        else:
            table = self.db
        result = table.update(update, doc_ids=[id])
        return result[0]

    @staticmethod
    def get_database(path: Optional[PathLike], in_memory: bool = False) -> TinyDB:
        TinyDB.default_table_name = "personal"
        if in_memory:
            return TinyDB(storage=MemoryStorage)
        try:
            db = TinyDB(path)
        except OSError as e:
            raise DatabasePathError(path)
        return db


class Model:
    def __init__(
        self,
        database: Optional[AbcDatabase] = None,
        custom_item_schema: Optional[Type[BaseModel]] = None,
    ) -> None:
        if not database:
            database = TinyDBDatabase()
        assert database is not None
        self.database = database
        self.ItemSchema = custom_item_schema or Item

    def all(self) -> dict[str, Sequence[Item]]:
        """Returns all entries in the phonebook"""
        r: dict[str, Any] = defaultdict(list)

        for workspace, entries in self.database.all().items():
            for entry in entries:
                r[workspace].append(self.ItemSchema(**entry))
        return r

    def get(self, id: int, workspace: Optional[str] = None) -> Item:
        """Gets a single entry from the phonebook"""
        r: DictItem = self.database.get(id, workspace)
        return self.ItemSchema(**r)

    def add_item(
        self, item: DictItem, workspace: Optional[str] = None
    ) -> Optional[int]:
        """Adds a single entry to the phonebook.Returns an id for the added item.
        :raises ValidationError if the input doesn't conform to the schema."""
        item = self.ItemSchema(**item)
        result: Optional[int] = self.database.add_item(item, workspace=workspace)
        return result

    def add_items(self, items: Sequence[DictItem], workspace: Optional[str] = None) -> Sequence[int] | Sequence[None]:
        """Adds multiple items. Returns a list of ids for the added items.
        :raises ValidationError if the input doesn't conform to the schema."""
        items = [self.ItemSchema(**item) for item in items]
        ids: Sequence[int] = self.database.add_items(items, workspace=workspace)
        return ids

    def filter(self, filters: DictItem, workspace: Optional[str] = None, **kwargs) -> Sequence[Item]:
        """Returns a subset of the items in the phonebook. Additional options can be passed with keyword
        arguments depending on the database being used."""
        result: Sequence[DictItem] = self.database.filter(filters, workspace=workspace, **kwargs)
        OutSchema = create_out_item(self.ItemSchema)
        output = []
        for entry in result:
            entry["id"] = entry.get(self.database.id_field_name, getattr(entry, self.database.id_field_name))
            output.append(OutSchema(**entry))
        return output

    def update(self, id: int, update: DictItem, workspace: str = None) -> Optional[int]:
        """Updated a single document by `id`.
        :raises ValidationError In case the update values are not valid."""
        InSchema = convert_fields_to_optional(self.ItemSchema)
        update = InSchema(**update)
        update_data = update.dict(exclude_unset=True)
        return self.database.update(id=id, update=update_data, workspace=workspace)

    def update_item_schema(self, new_schema: BaseModel) -> None:
        """Updates the item schema being used. If the database layout changes,
        you can call this to update the Item

        :param new_schema: [description]
        """
        self.ItemSchema = new_schema
