"""
python -m diana.cli.cli blah
"""
import click
from diana import __version__
from .echo import echo


@click.group()
@click.version_option(version=__version__, prog_name="diana-cli")
def cli():
    """
    Run and chain DIANA library functions from the command-line interface.
    """
    click.echo("DIANA")


cli.add_command(echo)


def main():
    cli()


if __name__ == "__main__":
    main()
