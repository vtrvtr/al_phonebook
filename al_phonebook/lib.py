from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Optional, Sequence, Type
from pydantic import BaseModel, EmailStr, constr
DictItem = dict[str, Any]
OptionalDictItem = DictItem | None
class Item(BaseModel):
    name: constr(max_length=100, strip_whitespace=True)  # type: ignore
    email: Optional[EmailStr]
    phone_number: Optional[constr(max_length=15, strip_whitespace=True, min_length=8)]  # type: ignore


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
