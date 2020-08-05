"""
python -m diana.cli.cli blah
"""

import click

@click.command()
@click.argument("text")
@click.option("--color", "-c", type=click.Choice(["red", "green", "blue"]))
def echo(text, color):
    if color:
        text = click.style(text, fg=color)
    click.echo(text)


def main():
    echo()


if __name__ == "__main__":
    main()