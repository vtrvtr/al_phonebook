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


def parse_configuration(path: PathLike) -> Configuration:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("File {p} doesn't exist.")

    with p.open(mode="r") as f:
        config_dict = yaml.safe_load(f)
        try:
            database_path = config_dict.get("database", {}).get(
                "path", configuration_folder() / ".alpb.json"
            )
            custom_model_path = (
                config_dict.get("model", {}).get("custom_model", {}).get("path")
            )
            custom_fields = config_dict.get("model", {}).get("custom_fields")
            config = Configuration(
                custom_model_path=custom_model_path,
                database_path=database_path,
                custom_fields=custom_fields,
            )
            return config
        except ValidationError as e:
            raise ConfigurationError(e)



def configuration_folder() -> Path:
    """Default configuration folder. Both the yaml file to configure the application
    and the database are saved here by default. The latter can be changed in the configuration file
    itself.
    """
    path = Path.home() / CONSTANTS.CONFIG_FOLDER_NAME.value
    if not path.exists():
        path.mkdir(parents=True)
    return path


def configuration_file() -> Path:
    path = configuration_folder() / "settings.yaml"
    if not path.exists():
        with path.open("w") as f:
            yaml.dump({"model": {}, "database": {}}, f)
    return path
