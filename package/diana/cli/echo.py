"""
Minimal test command
"""

import click


@click.command()
@click.argument("text")
@click.option("--color", "-c", type=click.Choice(["red", "green", "blue"]))
def echo(text, color):
    """Echo TEXT argument to the terminal, optionally colored by COLOR"""
    if color:
        text = click.style(text, fg=color)
    click.echo(text)


def main():
    echo()


if __name__ == "__main__":
    main()
