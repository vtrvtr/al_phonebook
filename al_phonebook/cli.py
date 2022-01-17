from numbers import Complex
from typing import Optional
from .lib import Model, Item
from .config import parse_configuration, configuration_file, create_database_model
from .constants import CONSTANTS
import os
import click
from pydantic import schema_of, ValidationError
from rich.table import Table
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel


# TODO: #5 Update UI with rich/textual
CONSOLE = Console()


class CliEnvironment:
    def __init__(self, model: Optional[Model] = None) -> None:
        self.model = model


@click.group(
    no_args_is_help=True,
    invoke_without_command=True,
    help=f"Loading configuration file from {configuration_file()}\nExecute a command followed by --help for more help.",
)
@click.pass_context
def cli(ctx):
    click.secho(
        f"📖 Starting {click.style('AL', fg='bright_blue', bold=True)} Phonebook! 📖\n\n"
    )
    config = parse_configuration(configuration_file())
    model = create_database_model(config)
    ctx.obj = model


@click.command(help="Adds an contact. This is an interactive command.")
@click.option(
    "-w",
    "--workspace",
    required=False,
    type=str,
    help="If given, records the contact to a specific workspace.",
)
@click.pass_obj
def add(model, workspace: Optional[str] = None) -> None:
    click.echo("Adding contact!\n")
    d = {}
    t = Table()
    for data in (
        schema_of(model.ItemSchema)
        .get("definitions")
        .get("Item")
        .get("properties")
        .values()
    ):
        parameter_styled = click.style(
            f"{data['title'].lower()}", bold=True, blink=True, fg="yellow"
        )
        r = click.prompt(f"Enter the contact's {parameter_styled}", default="")
        t.add_column(data["title"])
        if r:
            d[data["title"].lower()] = r

    try:
        item = Item(**d)
        already_exists = model.filter(
            {"name": item.name}, exact=True, workspace=workspace
        )
        if already_exists:
            overwrite = click.prompt(
                "Entry with name {name} already exists, update?", type=bool
            )
            if overwrite:
                model.update(already_exists[0].id, item.dict())
        else:
            model.add_item(d, workspace=workspace)
        t.title = workspace or "Default"
        t.add_row(*[str(i) if i else "" for i in item.dict().values()])

        CONSOLE.print(t)
    except ValidationError as e:
        click.echo(f"Invalid input {e}")


@click.command(help="Lists all contacts separated by workspace.")
@click.pass_obj
def list(model: Model) -> None:
    all_entries = model.all()
    if all_entries:
        for workspace_name, entries in all_entries.items():
            t = Table(title=workspace_name)
            for name in entries[0].dict().keys():
                t.add_column(name.title())

            for entry in entries:
                t.add_row(*[str(i) if i else "" for i in entry.dict().values()])

            CONSOLE.print(t)


@click.command(
    help="""Searches for a particular contact. The pattern is always the name of the field being searched followed by the value to be searched. The search is 'fulltext'. E.g: 

al_phonebook search name Vi

will find any contacts that contain "Vi" in their "name".

"""
)
@click.argument("pattern", nargs=2)
@click.option(
    "-w",
    "--workspace",
    required=False,
    type=str,
    help="If given, records the contact to a specific workspace.",
)
@click.pass_obj
def search(model: Model, pattern: str, workspace: Optional[str]) -> None:
    key, value = pattern
    click.echo(f"Searching for field {key} with value {value}!")
    result = model.filter({key: value}, workspace=workspace)
    if result:
        t = Table(title=workspace or "Default")
        for name in result[0].dict().keys():
            t.add_column(name)
        for entry in result:
            t.add_row(*[str(i) if i else "" for i in entry.dict().values()])

        CONSOLE.print(t)


cli.add_command(add)
cli.add_command(list)
cli.add_command(search)
