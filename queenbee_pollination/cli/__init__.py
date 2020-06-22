try:
    import click
except ImportError:
    raise ImportError(
        'click modules is not installed. Try `pip install queenbee[cli]` command.'
    )

from .context import Context
from .pull import pull
from .push import push
from .project import project

@click.group(invoke_without_command=True)
@click.version_option()
def pollination():
    """
    pollination cloud plugin
    """
    ctx = click.get_current_context()
    queenbee_config = ctx.obj

    ctx.ensure_object(Context)
    ctx.obj.queenbee = queenbee_config

    if ctx.invoked_subcommand is None:
        click.echo(ctx.command.get_help(ctx))


pollination.add_command(pull)
pollination.add_command(push)
pollination.add_command(project)