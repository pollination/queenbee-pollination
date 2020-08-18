from pydantic import ValidationError

from queenbee.recipe import Recipe
from queenbee.operator import Operator
from queenbee.repository.package import RecipeVersion, OperatorVersion

from pollination_sdk.exceptions import ApiException
from pollination_sdk.models import NewRepositoryDto

from ..client import Client

try:
    import click
except ImportError:
    raise ImportError(
        'click modules not installed. Try `pip install queenbee-pollination[cli]` command.'
    )


def handle_repository(client: Client, repo_type: str, owner: str, name: str, create_repo: bool = False):

    if repo_type not in ['recipe', 'operator']:
        raise click.ClickException('Repository type should be one of ["recipe", "operator"]')

    try:
        if repo_type == 'recipe':
            client.recipes.get_recipe(
                owner=owner,
                name=name,
            )
        elif repo_type == 'operator':
            client.operators.get_operator(
                owner=owner,
                name=name,
            )
    except ApiException as error:
        if error.status != 404:
            raise click.ClickException(error)

        if create_repo:
            new_repo = NewRepositoryDto(
                public=True,
                name=name,
            )

        else:
            if click.confirm(
                f'{repo_type} repository not found. Do you want to create a new repository at {owner}/{name}',
                abort=True
            ):
                private = click.confirm(
                    'Do you want to create a private repository?'),

                public = True

                if private is True:
                    public = False

                new_repo = NewRepositoryDto(
                    public=public,
                    name=name,
                )

        try:
            if repo_type == 'recipe':
                client.recipes.create_recipe(
                    owner=owner,
                    new_repository_dto=new_repo,
                )
            elif repo_type == 'operator':
                client.operators.create_operator(
                    owner=owner,
                    new_repository_dto=new_repo,
                )
        except ApiException as error:
            raise click.ClickException(error)

        click.echo('Successfully created repository!')


@click.group('push')
def push():
    pass


@push.command('recipe')
@click.argument('path', type=click.Path(exists=True))
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-t', '--tag', help='tag to apply to the recipe')
@click.option('--create-repo', help='create the recipe repository if it does not exist (defaults to a public repo)', type=bool, default=False, is_flag=True)
def recipe(path, owner, tag, create_repo):
    """push a queenbee recipe to the pollination registry

    This subcommand pushes a packaged queenbee recipe to a registry on
    pollination cloud
    """
    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    try:
        manifest = Recipe.from_folder(path)
    except ValidationError as error:
        raise click.ClickException(error)
    except FileNotFoundError as error:
        raise click.ClickException(error)
    except Exception as error:
        raise error

    handle_repository(
        client=client,
        repo_type='recipe',
        owner=owner,
        name=manifest.metadata.name,
        create_repo=create_repo
    )

    if tag is not None:
        manifest.metadata.tag = tag

    readme_string = RecipeVersion.read_readme(path)
    license_string = RecipeVersion.read_license(path)

    if readme_string is None:
        readme_string = ''

    if license_string is None:
        license_string = ''

    new_package = {
        'manifest': manifest.to_dict(),
        'readme': readme_string,
        'license': license_string
    }

    try:
        client.recipes.create_recipe_package(
            owner=owner,
            name=manifest.metadata.name,
            new_recipe_package=new_package,
        )
    except ApiException as error:
        raise click.ClickException(error)

    click.echo(f'Successfully created new recipe package {owner}/{manifest.metadata.name}:{manifest.metadata.tag}')


@push.command('operator')
@click.argument('path', type=click.Path(exists=True))
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-t', '--tag', help='tag to apply to the operator')
@click.option('--create-repo', help='create the operator repository if it does not exist (defaults to a public repo)', type=bool, default=False, is_flag=True)
def operator(path, owner, tag, create_repo):
    """push a queenbee operator to the pollination registry

    This subcommand pushes a packaged queenbee operator to a registry on
    pollination cloud
    """
    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    try:
        manifest = Operator.from_folder(path)
    except ValidationError as error:
        raise click.ClickException(error)
    except FileNotFoundError as error:
        raise click.ClickException(error)
    except Exception as error:
        raise error

    handle_repository(
        client=client,
        repo_type='operator',
        owner=owner,
        name=manifest.metadata.name,
        create_repo=create_repo
    )

    if tag is not None:
        manifest.metadata.tag = tag

    readme_string = RecipeVersion.read_readme(path)
    license_string = RecipeVersion.read_license(path)

    if readme_string is None:
        readme_string = ''

    if license_string is None:
        license_string = ''

    new_package = {
        'manifest': manifest.to_dict(),
        'readme': readme_string,
        'license': license_string
    }

    try:
        client.operators.create_operator_package(
            owner=owner,
            name=manifest.metadata.name,
            new_operator_package=new_package,
        )
    except ApiException as error:
        raise click.ClickException(error)

    click.echo(
        f'Successfully created new operator package {owner}/{manifest.metadata.name}:{manifest.metadata.tag}')
