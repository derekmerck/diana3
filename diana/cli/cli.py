"""
python -m diana.cli.cli blah
"""
import click
from diana import __version__
from .click_ptypes import ClickServiceManager
from service.endpoint import ServiceManager
from .echo import echo
from .do import do
from .status import status


@click.group()
@click.version_option(version=__version__, prog_name="diana-cli")
@click.option("-S", "services", type=ClickServiceManager(),
              help="Pass in a service description as a yaml-formatted string or file")
@click.pass_context
def cli(ctx, services):
    """
    Run and chain DIANA library functions from the command-line interface.
    """
    if not services:
        services = ServiceManager()
    ctx.obj["services"] = services


def add_commands(group, commands):
    for c in commands:
        group.add_command(c)


add_commands(cli, [echo, do, status])


def main():
    cli(auto_envvar_prefix='DIANA', obj={})


if __name__ == "__main__":
    main()
