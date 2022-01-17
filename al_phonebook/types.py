from typing import Any, Union
import os

DictItem = dict[str, Any]
OptionalDictItem = DictItem | None
PathLike = Union[os.PathLike, str]