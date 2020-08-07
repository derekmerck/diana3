import click
from libsvc.endpoint import ServiceManager


@click.command(name="status")
@click.pass_context
def status(ctx):
    """
    Check status of all known services.
    """

    services: ServiceManager = ctx.obj.get("services")
    status = services.status()

    for k, v in status.items():
        if not v:
            text = click.style(f"{k}: Down", fg="red")
        else:
            text = click.style(f"{k}: Up", fg="green")
        click.echo( text )
