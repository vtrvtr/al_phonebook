import pytest
from click.testing import CliRunner
from al_phonebook.cli import search
from al_phonebook.lib import Model
import click


def test_search(models_with_data) -> None:
    runner = CliRunner()
    for model in models_with_data:
        result = runner.invoke(search, ["name", "Clarisse"], obj=model)
        assert result.exit_code == 0 
        assert "Clarisse" in result.output
