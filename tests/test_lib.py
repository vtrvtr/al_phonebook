from configparser import ConfigParser
from json import load
import os
import tempfile
from pathlib import Path
from .common import models

import pytest
from al_phonebook.lib import DatabasePathError, Item, TinyDBDatabase
from al_phonebook.config import (
    Configuration,
    ConfigurationError,
    parse_configuration,
    load_schema_py,
    augment_schema,
    create_item_model,
)
from al_phonebook.formatter_registry import FormatterRegistry
from hypothesis import strategies as st, given


def test_start_tinydb_from_custom_path() -> None:
    _, some_path = tempfile.mkstemp(suffix=".json")
    db = TinyDBDatabase(path=some_path)
    assert Path(some_path) == db.path


def test_start_tinydb_invalid_custom_path() -> None:
    some_path = 12099  # invalid path
    with pytest.raises(DatabasePathError):
        db = TinyDBDatabase(path=some_path)


@given(name=st.text(min_size=5, max_size=100))
def test_add_one_item(name) -> None:
    for m in models():
        item = Item(name=name)
        r = m.add_item(item.dict())
        search = m.get(id=r)
        assert search == item


def test_filter(models_with_data, data) -> None:
    for model in models_with_data:
        r = model.filter({"name": "Bruce"})
        assert r[0] == data[1]


@given(name=st.text(min_size=5, max_size=100), email=st.emails())
def test_filter_item_single_email(name, email) -> None:
    for m in models():
        i = Item(name=name, email=email)
        m.add_item(i.dict())
        r = m.filter({"email": email})
        assert i.email in r[0].email


@given(name=st.text(min_size=5, max_size=100), email=st.emails())
def test_filter_item_multiple_parms(name, email) -> None:
    for m in models():
        i = Item(name=name, email=email)
        m.database.add_item(i)
        r = m.filter({"email": email, "name": name})
        assert i.dict() in r


def test_add_items() -> None:
    names = ["a", "b", "c", "d", "e"]
    items = [{"name": n} for n in names]

    for m in models():
        r = m.add_items(items)
        assert r == [1, 2, 3, 4, 5]


def test_list_item(models_with_data, data) -> None:
    for model in models_with_data:
        assert model.get(id=1) == data[0]


def test_list_all_items(models_with_data, data) -> None:
    for model in models_with_data:
        assert model.all().get("personal") == [i.dict() for i in data]


def test_add_custom_fields() -> None:
    custom_fields = {
        "age": {"type": "integer"},
        "secondary_email": {
            "type": "email",
            "required": True,
            "default": "foo@bar.com",
        },
    }
    s = augment_schema(custom_fields)
    assert s.__fields__["secondary_email"].default == "foo@bar.com"
    assert s.__fields__["age"].required == False


def test_add_custom_fields_to_model() -> None:
    custom_fields = {
        "age": {"type": "integer"},
        "secondary_email": {
            "type": "email",
            "required": True,
            "default": "foo@bar.com",
        },
    }
    s = augment_schema(custom_fields)
    for m in models():
        m.update_item_schema(s)
        some_email = "daz@bar.com"
        i = s(name="foo", secondary_email=some_email, asd=123)
        id = m.add_item(i.dict())
        assert m.get(id=id).secondary_email == some_email


def test_add_custom_fields_pydantic() -> None:
    custom_model_def = Path(__file__).parent / "resources" / "custom_model.py"
    s = load_schema_py(custom_model_def)
    assert s.__fields__["secondary_email"].default == "foo@bar.com"
    assert s.__fields__["age"].required == False


def test_parse_config() -> None:
    config_file = Path(__file__).parent / "resources" / "test_config.yaml"
    db_path = Path(__file__).parent / "resources" / ".test_db.json"
    model_path = Path(__file__).parent / "resources" / "custom_model.py"
    p = parse_configuration(config_file)

    custom_fields = {
        "age": {"type": "integer"},
        "secondary_email": {
            "type": "email",
            "required": True,
            "default": "foo@bar.com",
        },
    }

    assert p.database_path.absolute() == db_path
    assert p.custom_model_path.absolute() == model_path
    assert p.custom_fields == custom_fields


def test_parse_config_invalid_file() -> None:
    no_config_file = Path(__file__).parent / "resources" / "not_test_config.yaml"
    wrong_config_file = Path(__file__).parent / "resources" / "test_config_wrong.yaml"

    with pytest.raises(FileNotFoundError):
        p = parse_configuration(no_config_file)

    with pytest.raises(ConfigurationError):
        p = parse_configuration(wrong_config_file)


def test_custom_fields_from_config() -> None:
    config_file = Path(__file__).parent / "resources" / "test_config.yaml"
    db_path = Path(__file__).parent / "resources" / ".test_db.json"
    model_path = Path(__file__).parent / "resources" / "custom_model.py"

    custom_fields = {
        "age": {"type": "integer"},
        "secondary_email": {
            "type": "email",
            "required": True,
            "default": "foo@bar.com",
        },
    }

    config_model_path = Configuration(custom_model_path=model_path)

    model = create_item_model(config_model_path)
    assert model.__fields__.get("secondary_email")
    assert model.__fields__.get("age")

    config_custom_fields = Configuration(custom_fields=custom_fields)
    model = create_item_model(config_custom_fields)
    assert model.__fields__.get("age")
    assert model.__fields__.get("secondary_email")


def test_add_custom_formatter() -> None:
    assert False


def test_add_to_different_datasets(models_with_data) -> None:
    for model in models_with_data:
        i = Item(name="WorkOnlyPerson")
        r = model.add_item(i.dict(), workspace="Work")
        assert model.get(r, workspace="Work") == i


def test_filter_different_datasets(models_with_data_multiple_workspaces, data) -> None:
    for model in models_with_data_multiple_workspaces:
        r = model.filter({"age": 33})
        r2 = model.filter({"age": 33}, workspace="secondary")
        assert data[3] in r2
        assert r == []


def test_filter_non_string_fields(data, models_with_data) -> None:
    for model in models_with_data:
        r = model.filter({"age": 33})
        assert r[0] == data[3]


@pytest.mark.skip("Feature not necessary for now, nice to have in the future.")
def test_add_with_overwrite(data, models_with_data) -> None:
    assert False


def test_update(data) -> None:
    for m in models():
        i = Item(name=data[0].name)
        id = m.add_item(i.dict())
        r = m.update(id, {"email": data[0].email})
        assert m.get(id).email == data[0].email


def test_exact_filter(models_with_data, data) -> None:
    for model in models_with_data:
        r = model.filter({"name": "Bruce"}, exact=True)
        r2 = model.filter({"name": "bruce"}, exact=True)
        assert r[0] == data[1]
        assert r2 == []


def test_discover_plugin_files() -> None:
    temp_plugin_folder1 = tempfile.mkdtemp()
    temp_plugin_folder2 = tempfile.mkdtemp()

    config_dict = {
        "display": {
            "paths": [temp_plugin_folder1, temp_plugin_folder2],
            "formatters": ["myPlugin.JsonFormatter"],
        }
    }

    config = Configuration(
        formatters=config_dict.get("display").get("formatters"),
        plugins_folders=config_dict.get("display").get("paths"),
    )

    files = []
    for i in range(2):
        files.append(tempfile.TemporaryFile(dir=temp_plugin_folder1, suffix=".py"))
    for i in range(2):
        files.append(tempfile.TemporaryFile(dir=temp_plugin_folder2, suffix=".py"))

    discovered_files = []
    for folder in config.plugins_folders:
        for file in folder.iterdir():
            discovered_files.append(file)

    assert sorted(discovered_files) == sorted([Path(f.name) for f in files])


def test_load_plugin() -> None:
    temp_plugin_folder1 = tempfile.mkdtemp()
    temp_plugin_folder2 = tempfile.mkdtemp()

    config = {
        "display": {
            "paths": [temp_plugin_folder1, temp_plugin_folder2],
            "formatters": ["JsonFormatter"],
        }
    }

    config = Configuration(
        formatters=config.get("display").get("formatters"),
        plugins_folders=config.get("display").get("paths"),
    )

    class_name = config.formatters[0]
    code = f"""
import json

class {class_name}:

    def format(d):
        json.dumps(s)
    
    """

    with tempfile.NamedTemporaryFile(
        dir=temp_plugin_folder1, suffix=".py", mode="w", delete=False
    ) as f:
        f.write(code)

    registry = FormatterRegistry.from_configuration(config)

    formatter = registry.formatters[class_name]

    assert getattr(formatter, "format")


def test_format_with_plugin(models_with_data) -> None:
    temp_plugin_folder1 = tempfile.mkdtemp()

    config = {
        "display": {
            "paths": [temp_plugin_folder1],
            "formatters": ["PrintOneMore"],
        }
    }

    config = Configuration(
        formatters=config.get("display").get("formatters"),
        plugins_folders=config.get("display").get("paths"),
    )

    class_name = config.formatters[0]
    code = f"""
class {class_name}:

    def format(d) -> str:
        return str(d) + " 1"
    
    """

    with tempfile.NamedTemporaryFile(
        dir=temp_plugin_folder1, suffix=".py", mode="w", delete=False
    ) as f:
        f.write(code)

    registry = FormatterRegistry.from_configuration(config)

    formatter = registry.formatters[class_name]


    expected = "name='Adam' address=None email='adam@al.com' phone_number='999999999' age=30 1"
    for model in models_with_data:
        assert expected == formatter.format(model.all().get("personal")[0])



def test_plugin_wrong_def() -> None:
    temp_plugin_folder1 = tempfile.mkdtemp()

    config = {
        "display": {
            "paths": [temp_plugin_folder1],
            "formatters": ["PrintOneMore"],
        }
    }

    config = Configuration(
        formatters=config.get("display").get("formatters"),
        plugins_folders=config.get("display").get("paths"),
    )

    class_name = config.formatters[0]
    # All classes must have a `format` method. This one here will not be added
    # to the registry
    code = f"""
class {class_name}:

    def not_format(d) -> str:
        return str(d) + " 1"
    
    """

    with tempfile.NamedTemporaryFile(
        dir=temp_plugin_folder1, suffix=".py", mode="w", delete=False
    ) as f:
        f.write(code)

    registry = FormatterRegistry.from_configuration(config)

    assert class_name not in registry.formatters
