import os
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from multiprocessing import cpu_count
import tarfile
from urllib3.exceptions import ProtocolError
from typing import List

import requests
from tabulate import tabulate

from queenbee.job import Job

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

            new_project = models.ProjectCreate(
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

@folder.command('download')
@click.option('-p', '--project', help='project name', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('--path', help='the subpath/subfolder to download')
@click.option('-l', '--local-path', help='the path to save the files at on the local machine')
def download_artifacts(project, owner, path, local_path):
    """download project files"""
    if path is not None:
        path = [path]

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

    if local_path is None:
        local_path = os.getcwd()

    if path is not None:
        path = [path]

    def recusrive_download(owner: str, name: str, local_path: str, path: List[str] = None):

        files = client.artifacts.list_artifacts(owner=owner, name=name, path=path)

        for file in files:
            if file.type == 'folder':
                recusrive_download(
                    owner=owner,
                    name=name,
                    path=[file.key],
                    local_path=os.path.join(local_path, file.file_name)
                )
            else:
                download_link = client.artifacts.download_artifact(owner=owner, name=project, path=file.key)

                response = requests.get(url=download_link)

                file_path = os.path.join(local_path, file.file_name)
                file_dir = os.path.dirname(file_path)
                if not os.path.exists(file_dir):
                    os.makedirs(os.path.dirname(file_path))
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)

    
    recusrive_download(
        owner=owner,
        name=project,
        path=path,
        local_path=local_path
    )
 

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


@project.group('run')
def run():
    pass


@run.command('submit')
@click.argument('job_file', type=click.Path(exists=True))
@click.option('-p', '--project', help='project name', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
def submit(project, owner, job_file):
    """Schedule a job to be run"""

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

    job = Job.from_file(job_file)

    try:
        res = client.runs.create_run(
            owner=owner,
            name=project,
            job=job.dict(),
        )
    except ApiException as error:
        raise click.ClickException(error)

    click.echo(f'Successfully scheduled job: {res.id}')



@run.command('list')
@click.option('-p', '--project', type=str, required=True)
@click.option('-o', '--owner', help='a pollination account name')
@click.option('--page', type=int, default=1, show_default=True)
def list_runs(project, owner, page):
    """List runs for a given project"""

    ctx = click.get_current_context()
    client = ctx.obj.get_client()

    if owner is None:
        account = client.get_account()
        owner = account.username

    try:
        res = client.runs.list_runs(
            owner=owner,
            name=project,
            page=page,
        )
    except ApiException as error:
        raise click.ClickException(error)

    table = [[run.status.id, run.status.status, run.status.started_at, run.status.finished_at] for run in res.resources]

    table.sort(key=lambda r: r[2], reverse=True)

    print(tabulate(table, headers=['ID', 'Status', 'Stated At', 'Finished At']))

