"""
Command Line Interface (CLI) entry point for queenbee and queenbee extensions.

Use this file only to add command related to queenbee. For adding extra commands
from each extention see below.

Note:

    Do not import this module in your code directly unless you are extending the command
    line interface. For running the commands execute them from the command line or as a
    subprocess (e.g. ``subprocess.call(['queenbee', 'viz'])``)

Queenbee is using click (https://click.palletsprojects.com/en/7.x/) for creating the CLI.
You can extend the command line interface from inside each extention by following these
steps:

1. Create a ``cli.py`` file in your extension.
2. Import the ``pollination`` function from this ``queenbee.cli``.
3. Add your commands and command groups to pollination using add_command method.
4. Add ``import [your-extention].cli`` to ``__init__.py`` file to the commands are added
   to the cli when the module is loaded.

The good practice is to group all your extention commands in a command group named after
the extension. This will make the commands organized under extension namespace. For
instance commands for `queenbee-workerbee` will be called like ``queenbee workerbee [workerbee-command]``. 


.. code-block:: python

    import click
    from queenbee.cli import pollination

    @click.group()
    def workerbee():
        pass

    # add commands to workerbee group
    @workerbee.command('run')
    # ...
    def run():
        pass


    # finally add the newly created commands to queenbee cli
    pollination.add_command(workerbee)

    # do not forget to import this module in __init__.py otherwise it will not be added
    # to queenbee commands.

Note:

    For extension with several commands you can use a folder structure instead of a single
    file. Refer to ``queenbee-workerbee`` for an example.

"""

try:
    import click
except ImportError:
    raise ImportError(
        'click module is not installed. Try `pip install queenbee[cli]` command.'
    )

import configparser
from pathlib import Path
import os
import json
import yaml
import tarfile

import requests
from tabulate import tabulate
from queenbee.cli import Context
from queenbee.schema.workflow import Workflow
from queenbee.schema.arguments import Arguments
from queenbee_pollination.client import Client
from pollination_sdk.rest import ApiException
from pollination_sdk.models import SubmitSimulation


# TODO: Comment out and use for logging once we are adding commands to this file.
# import logging
# logger = logging.getLogger(__name__)

# class Context():

#     @staticmethod
#     def parse_workflow(filepath):
#         try:
#             return Workflow.from_file(filepath)
#         except AssertionError as e:
#             raise click.UsageError(e)
#         except Exception as e:
#             raise click.ClickException(e)
CONFIG_ROOT_FILE_NAME = ".queenbee"
CONFIG_NAMESPACE = "Pollination"
DEFAULT_SERVER_ENDPOINT = "https://api.pollination.cloud"


def login_with_api_token(config, config_path):
    api_server = config[CONFIG_NAMESPACE]['api_server']
    api_token_id = config[CONFIG_NAMESPACE]['api_token_id']
    api_token_secret = config[CONFIG_NAMESPACE]['api_token_secret']
    try:
        click.echo("Logging in using api tokens...")
        client = Client(api_key_id=api_token_id, 
            api_key_secret=api_token_secret, host=api_server)

        config[CONFIG_NAMESPACE]["api_access_token"] = client.config.access_token
        with open(config_path, 'w') as config_file:
            config.write(config_file)

        click.echo("Success!")

        return client

    except Exception as e:
        raise click.UsageError(e)

def login_with_access_token(config, config_path):
    api_server = config[CONFIG_NAMESPACE]['api_server']
    access_token = config[CONFIG_NAMESPACE]['api_access_token']
    try:
        return Client(access_token=access_token, host=api_server)
    except ValueError as e:
        click.echo("Invalid or Stale access token in config.")

        return login_with_api_token(config, config_path)
        
def login_user(ctx):
    config_path = ctx.obj.get("config_path")
    config = ctx.obj.get("config")
    api_server = config[CONFIG_NAMESPACE]['api_server']
    api_token_id = config[CONFIG_NAMESPACE]['api_token_id']
    api_token_secret = config[CONFIG_NAMESPACE]['api_token_secret']
    api_access_token = config[CONFIG_NAMESPACE]['api_access_token']

    if api_access_token == "":
        client = login_with_api_token(config, config_path)
    else:
        client = login_with_access_token(config, config_path)

    ctx.obj['client'] = client

def handle_api_error(ctx, error):
    if error.status == 401:
        click.echo("Access token has expired or is incorrect.")
        click.echo("Fetching a new access token for you now...")
        config_path = ctx.obj.get("config_path")
        config = ctx.obj.get("config")
        login_with_api_token(config, config_path)
        click.echo("Please retry the your command now")
    else:
        raise click.UsageError(error.body)


@click.group()
@click.version_option()
@click.pass_context
def pollination(ctx):
    """
    queenbee pollination plugin
    """
    ctx.obj = {}

    home = str(Path.home())
    config_path = os.path.join(home, CONFIG_ROOT_FILE_NAME)
    
    ctx.obj['config_path'] = config_path

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        namespace_config = config.options(CONFIG_NAMESPACE)
    except configparser.NoSectionError as e:
        click.echo(f"""
Looks like this is your first time logging in.

To interract with Pollination you need to save authentication credentials in {config_path}

This tool will walk you through this process:
        """)

        api_server = DEFAULT_SERVER_ENDPOINT
        api_token_id = click.prompt("Enter your API Token ID")
        api_token_secret = click.prompt("Enter your API Token Secret", hide_input=True)
        api_access_token = None

        config[CONFIG_NAMESPACE] = {}
        config[CONFIG_NAMESPACE]["api_server"] = api_server
        config[CONFIG_NAMESPACE]["api_token_id"] = api_token_id
        config[CONFIG_NAMESPACE]["api_token_secret"] = api_token_secret
        config[CONFIG_NAMESPACE]["api_access_token"] = ""
        
        ctx.obj['config'] = config
        
        login_user(ctx)

        click.echo("")

        click.echo("You can now run queenbee pollination commands as an authenticated user!")

        click.echo(f"Check the and modify the config file at your own risk: {ctx.obj.get('config_path')}")
        exit(0)


    ctx.obj['config'] = config


@pollination.group()
@click.version_option()
@click.pass_context
def workflows(ctx):
    """
    pollination workflows plugin
    """

@workflows.command('list')
@click.pass_context
def list(ctx):
    """list workflows"""
    login_user(ctx)
    client = ctx.obj.get('client')

    try:
        wfs = client.workflows.list()
        table = [[wf.id, wf.name] for wf in wfs]
        print(tabulate(table, headers=['ID', 'Name']))
    except ApiException as e:
        handle_api_error(ctx, e)


        
@workflows.command('get')
@click.option('-i', '--id', help='ID of the workflow you want to retrieve', required=True)
@click.option('-f', '--file', help='File path to save the workflow to')
@click.pass_context
def get(ctx, id, file):
    """retrieve a workflow by id"""
    login_user(ctx)
    client = ctx.obj.get('client')

    try:
        response = client.workflows.get(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    workflow = Workflow.parse_obj(response.to_dict())

    if file is not None:
        workflow.to_yaml(file)
    else:
        print(workflow.yaml())

@workflows.command('create')
@click.option('-f', '--file', help='File path to load the workflow from', required=True)
@click.pass_context
def create(ctx, file):
    """create a workflow from a yaml file"""
    login_user(ctx)

    client = ctx.obj.get('client')

    wf = Workflow.from_file(file)
    try:
        response = client.workflows.create(wf.dict())
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully created workflow {wf.name}")
    click.echo(f"New ID: {response.get('id')}")


@workflows.command('update')
@click.option('-i', '--id', help='ID of the workflow you want to retrieve', required=True)
@click.option('-f', '--file', help='File path to load the workflow from', required=True)
@click.pass_context
def update(ctx, id, file):
    """update a workflow from a yaml file"""
    login_user(ctx)

    client = ctx.obj.get('client')

    wf = Workflow.from_file(file)
    try:
        response = client.workflows.update(id, wf.dict())
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully updated workflow {wf.name}")
    click.echo(f"ID: {wf.id}")

@workflows.command('delete')
@click.option('-i', '--id', help='ID of the workflow you want to retrieve', required=True)
@click.pass_context
def delete(ctx, id):
    """delete a workflow from a yaml file"""
    login_user(ctx)

    client = ctx.obj.get('client')

    try:
        response = client.workflows.delete(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully deleted workflow {id}")

@pollination.group()
@click.version_option()
@click.pass_context
def simulations(ctx):
    """
    pollination simulations plugin
    """

@simulations.command('list')
@click.pass_context
def list(ctx):
    """list simulations"""
    login_user(ctx)
    client = ctx.obj.get('client')

    try:
        sims = client.simulations.list()
        table = [[sim.id, sim.workflow_ref.name, sim.status, sim.started_at, sim.finished_at] for sim in sims]


        table.sort(key=lambda r: r[4], reverse=True)


        print(tabulate(table, headers=['ID', 'Workflow', 'Status', 'Stated At', 'Finished At']))
    except ApiException as e:
        handle_api_error(ctx, e)


        
@simulations.command('get')
@click.option('-i', '--id', help='ID of the simulation you want to retrieve', required=True)
@click.option('-f', '--file', help='File path to save the simulation to')
@click.pass_context
def get(ctx, id, file):
    """retrieve a simulation by id"""
    login_user(ctx)
    client = ctx.obj.get('client')

    try:
        response = client.simulations.get(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    # simulation = simulation.parse_obj(response.to_dict())
    simulation = client.simulations.api_client.sanitize_for_serialization(response.to_dict())

    if file is not None:
        with open(file, 'w') as f:
            json.dump(simulation, f, indent=2)
    else:
        print(json.dumps(simulation, indent=2))

@simulations.command('schedule')
@click.option('-w', '--workflow', help='ID of the workflow you want to submit for simulation', required=True)
@click.option('-f', '--file', help='File path to load the simulation from', required=False)
@click.pass_context
def schedule(ctx, workflow, file):
    """create a simulation from a yaml file"""
    login_user(ctx)

    client = ctx.obj.get('client')

    if file is not None:
        args = Arguments.from_file(file)
    else:
        args = Arguments()

    submit_payload = SubmitSimulation(workflow=workflow, inputs=args.dict())

    try:
        response = client.simulations.create(submit_payload)
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully created simulation: {response.id}")


@simulations.command('suspend')
@click.option('-i', '--id', help='ID of the simulation', required=True)
@click.pass_context
def suspend(ctx, id):
    """suspend a running simulation"""
    login_user(ctx)

    client = ctx.obj.get('client')

    try:
        response = client.simulations.suspend(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully suspended simulation: {id}")

@simulations.command('resume')
@click.option('-i', '--id', help='ID of the simulation', required=True)
@click.pass_context
def resume(ctx, id):
    """resume a suspended simulation"""
    login_user(ctx)

    client = ctx.obj.get('client')

    try:
        response = client.simulations.resume(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully resumed simulation: {id}")

@simulations.command('resubmit')
@click.option('-i', '--id', help='ID of the simulation', required=True)
@click.pass_context
def resubmit(ctx, id):
    """resubmit a simulation"""
    login_user(ctx)

    client = ctx.obj.get('client')

    try:
        response = client.simulations.resubmit(id)
    except ApiException as e:
        handle_api_error(ctx, e)

    click.echo(f"Succesfully created simulation: {response.id}")

@simulations.command('download')
@click.option('-i', '--id', help='ID of the simulation your want to retrieve artifacts from', required=True)
@click.option('-f', '--folder', help='Folder path to save simulation artifacts to', required=True)
@click.option('-a', '--artifact', help='Choose which artifacts to download. Will download all if not specified.', type=click.Choice(['inputs', 'outputs', 'logs'], case_sensitive=False))
@click.pass_context
def download(ctx, id, folder, artifact):
    """download simulation artifacts"""
    login_user(ctx)

    client = ctx.obj.get('client')

    if artifact is None:
        artifacts = ['inputs', 'outputs', 'logs']
    else:
        artifacts = [artifact]

    for a in artifacts:

        if a == 'inputs':
            try:
                response = client.simulations.get_simulation_inputs(id, _preload_content=False)
            except ApiException as e:
                handle_api_error(ctx, e)

        elif a == 'outputs':
            try:
                response = client.simulations.get_simulation_outputs(id, _preload_content=False)
            except ApiException as e:
                handle_api_error(ctx, e)

        elif a == 'logs':
            try:
                response = client.simulations.get_simulation_logs(id, _preload_content=False)
            except ApiException as e:
                handle_api_error(ctx, e)

        CHUNK = 16 * 1024
        with open(f'{folder}.tar.gz', 'wb') as f:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)

        tar = tarfile.open(name=f'{folder}.tar.gz')
        tar.extractall(f'{folder}')
        os.remove(f'{folder}.tar.gz')


@pollination.group()
@click.version_option()
@click.pass_context
def artifacts(ctx):
    """
    pollination artifacts plugin
    """

@artifacts.command('list')
@click.pass_context
def list(ctx):
    """list artifacts"""
    login_user(ctx)
    client = ctx.obj.get('client')

    try:
        artifacts = client.artifacts.list()

        table = []

        for artifact in artifacts:

            if artifact.file_name != "":
                table.append([artifact.file_name, artifact.key, artifact.size/1000000, artifact.last_modified])


        table.sort(key=lambda r: r[1], reverse=False)


        print(tabulate(table, headers=['Name', 'Path', 'Size (Mb)', 'Last Modified']))
    except ApiException as e:
        handle_api_error(ctx, e)



@artifacts.command('upload')
@click.option('-f', '--folder', help='Folder path to save simulation artifacts to', required=True)
@click.option('-p', '--prefix', help='A prefix to use when uploading this folder to pollination storage')
@click.pass_context
def download(ctx, folder, prefix):
    """upload artifacts"""
    login_user(ctx)
    client = ctx.obj.get('client')

    if prefix is None:
        prefix = ""

    for root, subdirs, files in os.walk(folder):
        for file in files:
            if prefix is not None:
                key = os.path.join(prefix, root, file)
            else:
                key = os.path.join(root, file)
            
            res = client.artifacts.create({'key': key})


            # Demonstrate how another Python program can use the presigned URL to upload a file
            with open(key, 'rb') as f:
                files = {'file': (key, f)}
                http_response = requests.post(res.url, data=res.fields, files=files)

                if http_response.status_code == 204:
                    print(f"Uploaded {key}")

if __name__ == "__main__":
    pollination()
