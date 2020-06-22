import os
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from multiprocessing import cpu_count
import tarfile
from urllib3.exceptions import ProtocolError

import requests
from pydantic import ValidationError
from tabulate import tabulate

from queenbee.workflow import Arguments
from queenbee.workflow.status import WorkflowStatus

from pollination_sdk.exceptions import ApiException
from pollination_sdk import models

from ..client import Client

try:
    import click
except ImportError:
    raise ImportError(
        'click modules not installed. Try `pip install queenbee-pollination[cli]` command.'
    )


def handle_project(client: Client, owner: str, name: str):

    try:
        client.projects.get_project(
            owner=owner,
            name=name,
        )
    except ApiException as error:
        if error.status != 404:
            raise click.ClickException(error)

        if click.confirm(
            f'Project not found. Do you want to create a new project at {owner}/{name}',
            abort=True
        ):
            private = click.confirm('Do you want to create a private project?'),

            public = True

            if private is True:
                public = False

            new_project = models.PatchProjectDto(
                name=name,
                public=public,
                description=''
            )

            try:
                client.projects.create_project(
                    owner=owner,
                    patch_project_dto=new_project,
                )
            except ApiException as error:
                raise click.ClickException(error)

            click.echo('Successfully created project!')


@click.group('project')
def project():
    pass


@project.group('folder')
def folder():
    pass

@folder.command('upload')
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('-p', '--project', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
def upload_folder(path, owner, project):
    """upload project files"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    handle_project(
        client=client,
        owner=owner,
        name=project,
    )


    def _upload_artifact(key: str):
        res = client.artifacts.create_artifact(
            owner=owner,
            name=project,
            key_request={'key': key.replace('\\', '/')}
        )

        # Demonstrate how another Python program can use the presigned URL to upload a file
        with open(key, 'rb') as f:
            files = {'file': (key, f)}
            http_response = requests.post(
                res.url, data=res.fields, files=files)

            if http_response.status_code == 204:
                click.echo(f"Uploaded {key}")


    keys = []
    for root, subdirs, files in os.walk(path):
        for fi in files:
            key = os.path.join(root, fi)
            keys.append(key)

    worker_count = max(cpu_count() - 1, 1)
    with PoolExecutor(max_workers=worker_count) as executor:
        for _ in executor.map(_upload_artifact, keys):
            pass


@folder.command('delete')
@click.option('-p', '--project', help='project name', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('--path', help='the subpath/subfolder to delete')
def delete_artifacts(project, owner, path):
    """delete project files"""

    if path is not None:
        path = [path]

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    client.artifacts.delete_artifact(
        owner=owner,
        name=project,
        path=path
    )

    print("Poof... All gone!")


@project.group('simulation')
def simulation():
    pass


@simulation.command('submit')
@click.argument('recipe', type=str)
@click.option('-p', '--project', help='project name', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-i', '--inputs', help='path to an inputs file', type=click.Path(exists=True))
def submit(project, recipe, owner, inputs):
    """Schedule a simulation to be run"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    handle_project(
        client=client,
        owner=owner,
        name=project,
    )

    try:
        rec_owner, rec_name = recipe.split('/')
        rec_name, rec_tag = rec_name.split(':')
    except ValueError as error:
        click.ClickException(f'Expected recipe reference in format "owner/name:tag" not: {recipe}')

    recipe_ref = models.RecipeSelection(
        owner=rec_owner,
        name=rec_name,
        tag=rec_tag,
    )

    arguments = Arguments()
    
    if inputs is not None:
        arguments = Arguments.from_file(inputs)

    submit = models.SubmitSimulationDto(
        recipe=recipe_ref,
        inputs=arguments.to_dict()
    )

    try:
        res = client.simulations.create_simulation(
            owner=owner,
            name=project,
            submit_simulation_dto=submit,
        )
    except ApiException as error:
        raise click.ClickException(error)

    click.echo(f'Successfully scheduled simulation: {res.id}')



@simulation.command('list')
@click.option('-p', '--project', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('--page', type=int, default=1, show_default=True)
def list_simulations(project, owner, page):
    """List simulations for a given project"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    try:
        res = client.simulations.list_simulations(
            owner=owner,
            name=project,
            page=page,
        )
    except ApiException as error:
        raise click.ClickException(error)

    table = [[sim.id, sim.status, sim.started_at, sim.finished_at] for sim in res.resources]

    table.sort(key=lambda r: r[2], reverse=True)

    print(tabulate(table, headers=['ID', 'Status', 'Stated At', 'Finished At']))


@simulation.command('download')
@click.option('-p', '--project', help='Name of a project', required=True)
@click.option('-i', '--id', help='ID of the simulation your want to retrieve artifacts from', required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('-f', '--folder', help='Folder path to save simulation artifacts to', default='.', show_default=True)
@click.option('-a', '--artifact', help='Choose which artifacts to download. Will download all if not specified.', type=click.Choice(['inputs', 'outputs', 'logs'], case_sensitive=False))
def download_simulation_artifacts(owner, project, id, folder, artifact):
    """download simulation artifacts"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    folder = os.path.join(folder, id)

    if artifact is None:
        artifacts = ['inputs', 'outputs', 'logs']
    else:
        artifacts = [artifact]

    try:
        simulation = client.simulations.get_simulation(
            owner=owner,
            name=project,
            simulation_id=id,
        )
    except ApiException as error:
        if error.status == 404:
            raise click.ClickException(
                f'Simulation not found: {owner}/{project}/{id}')
        raise click.ClickException(error)

    for a in artifacts:

        if a == 'inputs':
            try:
                fetch_url = client.simulations.get_simulation_inputs(
                    owner=owner,
                    name=project,
                    simulation_id=id,
                )
            except ApiException as error:
                raise click.ClickException(error)

        elif a == 'outputs':
            try:
                fetch_url = client.simulations.get_simulation_outputs(
                    owner=owner,
                    name=project,
                    simulation_id=id,
                )
            except ApiException as error:
                raise click.ClickException(error)

        elif a == 'logs':
            try:
                fetch_url = client.simulations.get_simulation_logs(
                    owner=owner,
                    name=project,
                    simulation_id=id,
                )
            except ApiException as error:
                raise click.ClickException(error)

        response = requests.get(url=fetch_url)

        try:
            with open(f'{folder}.tar.gz', 'wb') as f:
                f.write(response.content)

            try:
                tar = tarfile.open(name=f'{folder}.tar.gz')
                tar.extractall(f'{folder}')
                click.echo(f'Saved {a} files to {folder}/{a}')
            except tarfile.ReadError as error:
                click.echo(f'Failed to read {a}')
            os.remove(f'{folder}.tar.gz')


        except ProtocolError as e:
            click.echo(f'No {a}  files found')

    status = WorkflowStatus.parse_obj(simulation.to_dict())

    status.to_yaml(
        filepath=os.path.join(folder, 'simulation.yml')
    )
    
