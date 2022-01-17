from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Type, cast
import sys
import importlib

import yaml
from pydantic import (
    BaseModel,
    ValidationError,
    validator,
    EmailStr,
    create_model,
    Field,
)

from .types import OptionalDictItem, PathLike, DictItem
from .lib import Item, TinyDBDatabase, Model
from .constants import CONSTANTS


class Configuration(BaseModel):
    custom_fields: OptionalDictItem
    custom_model_path: Path = Field(
        None, description="Path to the custom model to be used."
    )
    database_path: Optional[Path]

    @validator("custom_model_path")
    def is_valid_model_path(cls, v):
        if not v:
            return None

        if not v.exists():
            raise ConfigurationError(FileNotFoundError(f"Path {v} doesn't exist"))
        if v.suffix != ".py":
            raise ConfigurationError("Custom model path must be a .py file.")
        return v

    @validator("database_path")
    def is_valid_db_path(cls, v):
        if not v:
            return True
        if v.suffix != ".json":
            raise ConfigurationError("Database path must be .json file.")
        return v

    class Config:
        extra = "forbid"
