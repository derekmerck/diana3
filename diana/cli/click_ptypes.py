"""
Click parameter types with converters for cli
"""

import typing as typ
import yaml
import click
from libsvc.endpoint import ServiceManager, Endpoint
from libsvc.utils import smart_yaml_loader


# Argument type parsers
class ClickServiceManager(click.ParamType):
    name = "service_manager"

    def convert(self, value, param, ctx) -> ServiceManager:
        if not value:
            return
        try:
            return ServiceManager.from_descs(data=value)
        except KeyError:
            self.fail(f"{value!r} some object ctypes are unregistered", param, ctx)
        except yaml.parser.ParserError:
            self.fail(f"{value!r} should be a string or file path parsable by yaml", param, ctx)
        except Exception:
            self.fail(f"{value!r} threw an exception", param, ctx)


class ClickService(click.ParamType):
    name = "service"

    def convert(self, value, param, ctx) -> Endpoint:
        if not value:
            return None

        services = ctx.obj.get("services")
        if not services:
            raise RuntimeError

        service = services.get(value)
        if not service:
            raise KeyError

        return service


class ClickYAML(click.ParamType):
    name = "yaml"

    def convert(self, value, param, ctx) -> typ.Any:
        # May be [] or {} depending on default type, return as is
        if not value:
            return value
        try:
            return smart_yaml_loader(value)
        except yaml.parser.ParserError:
            self.fail(f"{value!r} should be a string or file path parsable by yaml", param, ctx)
        except Exception:
            self.fail(f"{value!r} threw an exception", param, ctx)
