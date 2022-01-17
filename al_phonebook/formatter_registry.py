import importlib
import inspect
import sys
from pathlib import Path
from typing import Sequence
from warnings import warn

from .config import Configuration


class FormatterRegistry:
    """
    FormatterRegistry is a simplistic plugin system that can be used to format DictItem
    """

    def __init__(self, folders: Sequence[Path]):
        """Initialize a FormatterRegistry instance. Does not perform any plugin collection.
        To collect plugin in `folders` execute the `collect_plugins` method.

        Alternatively, use the `from_configuration` method to build the correct registry based on a `Configuration`.

        :param folders: A list of folders in which `.py` files can be found. Classes with a `format` method will
        be added to the registry
        """
        self.formatters = {}
        self.folders = folders

    def collect_plugins(self):
        """
        Builds a dictionary, stored in the `formatters` attribute that maps from a class name to a class object. 

        Iterates through every file in every folder in  the attribute `folders`, checks every class in each file and
        if the class isn't private (startswith __), is user defined (has a __module__ attribute) and a `format` method
        adds this class to the the `formatters` map.

        In case of error, emits a standard Python warn and skips the particular class or file.
        """
        for folder in self.folders:
            for pyfile in folder.rglob("*.py"):
                folder = pyfile.parent
                sys.path.append(folder.as_posix())
                module_name = pyfile.stem
                try:
                    module = importlib.import_module(module_name)
                    classes = inspect.getmembers(module)
                    for name, class_object in classes:
                        if name.startswith("__"):
                            continue

                        if not getattr(class_object, "__module__", None):
                            continue

                        if not getattr(class_object, "format", None):
                            warn(
                                f"Plugin class {name} from folder {folder} doesn't have a `format` method. Skipping..."
                            )
                            continue

                        self.formatters[name] = class_object
                except ImportError:
                    warn(
                        f"Failed to import module {module_name} from folder {folder}. This formatter won't be usable."
                    )
                    continue

    @staticmethod
    def from_configuration(configuration: Configuration) -> "FormatterRegistry":
        """Initializes a `FormatterRegistry` based on a `Configuration` instance.
        Calls `collect_plugins`. """
        folders = configuration.plugins_folders
        assert folders

        instance = FormatterRegistry(folders)

        instance.collect_plugins()

        return instance
