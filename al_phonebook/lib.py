from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Optional, Sequence, Type
DictItem = dict[str, Any]
OptionalDictItem = DictItem | None
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
