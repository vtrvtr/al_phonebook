from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Type, cast, Sequence
import sys
import importlib
from warnings import warn
import inspect

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

SUPPORTED_TYPES = {"integer": int, "string": str, "email": EmailStr, "float": float}


class Configuration(BaseModel):
    custom_fields: OptionalDictItem
    custom_model_path: Path = Field(
        None, description="Path to the custom model to be used."
    )
    database_path: Optional[Path]
    plugins_folders: Optional[Sequence[Path]]
    formatters: Optional[list[str]]

    @validator("custom_model_path")
    def is_valid_model_path(cls, v):
        if not v:
            return None

        if not v.exists():
            raise ConfigurationError(FileNotFoundError(f"Path {v} doesn't exist"))
        if v.suffix != ".py":
            raise ConfigurationError("Custom model path must be a .py file.")
        return v

    @validator("plugins_folders")
    def is_valid_plugins_folders(cls, v):
        for p in v:
            if not p.exists():
                raise ConfigurationError(FileNotFoundError(f"Path {p} doesn't exist"))
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
    """
    Builds `Configuration` object from reading `path`, which points to an yaml file.

    :raises FileNotFoundError: If `path` doesn't exist
    :raises ConfigurationError: If an error occurs in the validation of the configuration
    """
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
            plugins_folders = config_dict.get("display", {}).get("paths", [])
            if default_plugin_folder() not in plugins_folders:
                plugins_folders.append(default_plugin_folder())
            formatters = config_dict.get("display", {}).get("formatters")
            config = Configuration(
                custom_model_path=custom_model_path,
                database_path=database_path,
                custom_fields=custom_fields,
                plugins_folders=plugins_folders,
                formatters=formatters,
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


def default_plugin_folder() -> Path:
    path = configuration_folder() / "plugins"
    if not path.exists():
        path.mkdir(parents=True)
    return path


# TODO: #6 Add validation for custom pydantic model
def load_schema_py(path: PathLike) -> BaseModel:
    """Loads a pydantic model from `path` to be used as the main Item for the
    database.

    :raises ConfigurationError: If there's a problem loading `Item` from file in `path`.
    """
    p = Path(path)
    sys.path.append(p.parent.as_posix())
    module_name = p.stem
    try:
        module = importlib.import_module(module_name)
        model_schema: Item = module.Item
        return model_schema
    except:
        raise ConfigurationError(
            f"Couldn't import Item from {p}. Make sure there's a Item pydantic model in it."
        )


def augment_schema(fields: DictItem) -> Type[Item]:
    """Adds fields from `fields` to the default pydantic model `Item`.
    Only a subset of field types are supported. They listed in `config.SUPPORTED_TYPES`. If
    the type described isn't included there, it defaults to `str`.

    :raises SchemaFieldError: In case there's a field configuration error.
    """
    parsed_fields = {}
    for field_name, properties in fields.items():
        field_type = properties.get("type", str)
        is_required = properties.get("required")
        if is_required:
            default_value = properties.get("default")
            if not default_value:
                raise SchemaFieldError(field_name)
            parsed_fields[field_name] = (
                SUPPORTED_TYPES.get(field_type),
                default_value,
            )
        else:
            parsed_fields[field_name] = (SUPPORTED_TYPES.get(field_type), None)
    schema: Type[Item] = create_model("Item", **parsed_fields, __base__=Item)
    return schema


def create_item_model(config: Configuration) -> Type[Item]:
    if config.custom_model_path:
        schema = cast(Type[Item], load_schema_py(config.custom_model_path))
        return schema

    if config.custom_fields:
        schema = augment_schema(config.custom_fields)
        return schema

    return Item


def create_database_model(config: Configuration) -> Model:
    """
    Creates a Model using TinyDB as a database. `config` configures the database as needed.
    """
    assert config.database_path
    db = TinyDBDatabase(path=config.database_path)
    item_schema = create_item_model(config)
    return Model(database=db, custom_item_schema=item_schema)


class ConfigurationError(Exception):
    def __init__(self, message: Union[Exception, str]) -> None:
        super().__init__(f"Couldn't load current configuration. {message}")


class SchemaLoadingError(Exception):
    def __init__(self, path: PathLike) -> None:
        super().__init__(
            f"Couldn't load `Item` from {path}. File must exist. Supported extensions are: .py, .yaml. Aborting..."
        )


class SchemaFieldError(Exception):
    def __init__(self, field: str) -> None:
        super().__init__(
            f"The field `{field}` must have a default value because it's required."
        )
