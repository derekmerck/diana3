from pprint import pformat
import click
from .click_ptypes import ClickYAML, ClickService
from diana.endpoint import ServiceManager


@click.command(name="do")
@click.argument("service", type=ClickService())
@click.argument("method")
@click.option("-a", "--args", type=ClickYAML(), default=[],
              help="String or file in yaml format resulting in an array of [ARGS]")
@click.option("-k", "--kwargs", type=ClickYAML(), default={},
              help="String or file in yaml format resulting in a dict of {KWARGS}")
@click.pass_context
def do(ctx, service, method, args, kwargs):
    """Invoke an arbitrary function METHOD on SERVICE_NAME with optional
    parameters given in [ARGS] and {KWARGS}"""

    if not hasattr(service, method):
        raise RuntimeError(f"Unknown method {method} on service {service}")

    out = getattr(service, method)(*args, **kwargs)

    click.echo( pformat(out) )