import os
import shutil

from queenbee.recipe import Recipe
from queenbee.plugin import Plugin
from queenbee.repository.package import PackageVersion

from pollination_sdk.exceptions import ApiException

try:
    import click
except ImportError:
    raise ImportError(
        'click modules not installed. Try `pip install queenbee-pollination[cli]` command.'
    )


@click.group('pull')
def pull():
    pass


@pull.command('recipe')
@click.argument('name')
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-t', '--tag', help='specific recipe tag to pull')
@click.option('-p', '--path', help='path to download the recipe to', type=click.Path(exists=True), default='.')
@click.option('-f', '--force', help='overwrite local files', type=bool, default=False, is_flag=True)
def recipe(name, owner, tag, path, force):
    """download a recipe from a pollination registry"""
    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    path = os.path.abspath(path)
    path = os.path.join(path, name)

    if owner is None:
        account = client.get_account()
        owner = account.username

    if tag is None:
        try:
            res = client.recipes.get_recipe(
                owner=owner,
                name=name,
            )
        except ApiException as error:
            if error.status == 404:
                raise click.ClickException(f'Recipe not found: {owner}/{name}')
            raise click.ClickException(error)

        tag = res['latest_tag']

    try:
        res = client.recipes.get_recipe_tag(
            owner=owner,
            name=name,
            tag=tag
        )
    except ApiException as error:
        if error.status == 404:
            raise click.ClickException(f'Recipe not found: {owner}/{name}:{tag}')
        raise click.ClickException(error)

    manifest = Recipe.parse_obj(res['manifest'])

    try:
        manifest.to_folder(
            folder_path=path,
            readme_string=res['readme'],
        )
    except FileExistsError as error:
        if not force:
            raise click.ClickException(f'Folder already exists at path {path}. Use "--force" to overwrite it.')

        shutil.rmtree(path)

        manifest.to_folder(
            folder_path=path,
            readme_string=res['readme'],
        )

    click.echo(f'Recipe {owner}/{name}:{tag} saved to {path}')


@pull.command('plugin')
@click.argument('name')
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-t', '--tag', help='specific recipe tag to pull')
@click.option('-p', '--path', help='path to download the plugin to', type=click.Path(exists=True), default='.')
@click.option('-f', '--force', help='overwrite local files', type=bool, default=False, is_flag=True)
def plugin(name, owner, tag, path, force):
    """download an plugin from a pollination registry"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    path = os.path.abspath(path)
    path = os.path.join(path, name)

    if owner is None:
        account = client.get_account()
        owner = account.username

    if tag is None:
        try:
            res = client.plugins.get_plugin(
                owner=owner,
                name=name,
            )
        except ApiException as error:
            if error.status == 404:
                raise click.ClickException(f'Plugin not found: {owner}/{name}')
            raise click.ClickException(error)

        tag = res['latest_tag']

    try:
        res = client.plugins.get_plugin_tag(
            owner=owner,
            name=name,
            tag=tag
        )
    except ApiException as error:
        if error.status == 404:
            raise click.ClickException(
                f'Plugin not found: {owner}/{name}:{tag}')
        raise click.ClickException(error)

    manifest = Plugin.parse_obj(res['manifest'])

    try:
        manifest.to_folder(
            folder_path=path,
            readme_string=res['readme'],
        )
    except FileExistsError:
        if not force:
            raise click.ClickException(f'Folder already exists at path {path}')

        shutil.rmtree(path)

        manifest.to_folder(
            folder_path=path,
            readme_string=res['readme'],
        )

    click.echo(f'Plugin {owner}/{name}:{tag} saved to {path}')
