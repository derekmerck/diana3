import click
from .echo import echo


@click.group()
def cli():
    click.echo("DIANA")


cli.add_command(echo)


def main():
    cli()


if __name__ == "__main__":
    main()
