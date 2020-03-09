# queenbee-pollination

queenbee-pollination extends [queenbee](https://github.com/ladybug-tools/queenbee) in order to interact with the [Pollination API](https://api.pollination.cloud).

## Installation

You can install this as a cli tool using the following command:

```console
pip install queenbee-pollination[cli]
```

## CLI QuickStart


### Authentication

When you first run any queenbee-pollination command through the CLI you will be required to enter some authentication details so that the tool can interact with the Pollination API using your account.

You will need a Pollination API token. You can generate a new one from your user profile setting: `https://app.pollination.cloud/{your-user-name}/settings`.

In this example we will use the `ladybugbot` user. If you were ladybugbot you would access your API tokens at this page: `https://app.pollination.cloud/ladybugbot/settings`.

You will be prompted to do provide your API token by the CLI as demonstrated below:

```console
> queenbee pollination workflows list

Looks like this is your first time logging in.

To interract with Pollination you need to save authentication credentials in C:\Users\ladybugbot\.queenbee

This tool will walk you through this process:
        
Enter your API Token:
Logging in using api tokens...
Success!

Hi ladybugbot@ladybugtools.com! Welcome to Queenbee Pollination!

You can now run queenbee pollination commands as an authenticated user!
Check the and modify the config file at your own risk: C:\Users\ladybugbot\.queenbee

```

You can now check the configuration file saved at the path indicated in you command line. in the case of the example above the path to the config file is: `C:\Users\ladybugbot\.queenbee`.

## Hello World!

We have compiled a quick demo workflow for you to test out the queenbee-pollination plugin.

Copy and save the text below into a file called `hello.yaml`.

```yaml
type: workflow
name: hello-world

artifact_locations: []

operators:
- name: whalesay
  image: docker/whalesay

templates:
- type: function
  name: cowsay
  operator: whalesay
  inputs:
    parameters:
    - name: word
  command: cowsay {{inputs.parameters.word}}

flow:
  name: say-hello-world
  tasks:
  - name: say-hello
    template: cowsay
    arguments:
      parameters:
      - name: word
        value: hello
  - name: say-world
    template: cowsay
    dependencies: ['say-hello']
    arguments:
      parameters:
      - name: word
        value: world
  - name: exclamate
    template: cowsay
    dependencies: ['say-world']
    arguments:
      parameters:
      - name: word
        value: '!'

```

1. Save the workflow to the Pollination platform

```console
> queenbee pollination workflows create -f hello.yaml

Successfully created workflow ladybugbot/hello-world
```

2. List your existing workflows

```console
> queenbee pollination workflows list

Owner       Name             Public
----------  ---------------  --------
ladybugbot  hello-world      True

```

3. Simulations can only be run within the context of a project. To create a new project, run the following command:
```console
> queenbee pollination projects create -n hello-world

Successfully created project ladybugtools/hello-world
```

4. Submit a simulation to run using the hello-world workflow template 

```console
> queenbee pollination simulations submit --project hello-world --workflow ladybugtools/hello-world

Successfully created simulation: 15a558e3-5978-40cc-ba2f-aeeef1874600
```

5. List all running simulations

```console
> queenbee pollination simulations list --project hello-world
ID                                    Status     Stated At                  Finished At
------------------------------------  ---------  -------------------------  -------------------------
15a558e3-5978-40cc-ba2f-aeeef1874600  Succeeded  2020-03-09 02:00:23+00:00  2020-03-09 02:01:01+00:00

```

1. Retrieve all persisted simulation data to a local folder called `sim-data`.

```console
> queenbee pollination simulations download --project hello-world -i 15a558e3-5978-40cc-ba2f-aeeef1874600 --folder sim-data

No inputs  files found
No outputs  files found
Saved logs files to sim-data/logs
```

8. Inspect simulation metadata in detail. Get and save the simulation object into a file called `simulation.json` inside the `sim-data` folder.

```console
> queenbee pollination simulations get --project hello-world -i 15a558e3-5978-40cc-ba2f-aeeef1874600 -f sim-data/simulation.json
```

## Artifacts

You can also upload raw files to a project's folder. We call these `artifacts`. These artifacts will then be accessible to any simulation you run in this project.

In the following example we will upload a radiance folder and then run a daylight-factor simulation on top of it.

1. Clone the github project and move your terminal into the repository

```console
> git clone https://github.com/ladybug-tools/radiance-folder-structure/

Cloning into 'radiance-folder-structure'...
remote: Enumerating objects: 311, done.
remote: Total 311 (delta 0), reused 0 (delta 0), pack-reused 311
Receiving objects: 100% (311/311), 1.07 MiB | 989.00 KiB/s, done.
Resolving deltas: 100% (87/87), done.

> cd radiance-folder-structure
```

2. Upload the files to your `hello-world` project. You should be able to check them out at `https://app.pollination.cloud/projects/{your-username}/hello-world`

```
> queenbee pollination artifacts upload --project hello-world -f project_folder
```

3. Run a daylight-factor simulation using another user's workflow (it's all about sharing!)

```console
> queenbee pollination simulations submit -p hello-world -w antoinedao/daylight-factor

Successfully created simulation: 5cbdcb5f-fec9-4048-8b59-5e37f8182d8e

```

4. Check the status of your simulation. Once the simulation you created is marked as "Succeeded" you can carry onto the next step.

```console
> queenbee pollination simulations list --project hello-world
ID                                    Status     Stated At                  Finished At
------------------------------------  ---------  -------------------------  -------------------------
5cbdcb5f-fec9-4048-8b59-5e37f8182d8e  Running  2020-03-09 02:10:23+00:00  2020-03-09 02:12:01+00:00
15a558e3-5978-40cc-ba2f-aeeef1874600  Succeeded  2020-03-09 02:00:23+00:00  2020-03-09 02:01:01+00:00
```

5. Download your results and start analysing them using whatever tool you like!

```console
> queenbee pollination simulations download --project hello-world -i 5cbdcb5f-fec9-4048-8b59-5e37f8182d8e --folder daylight-factor-data

Saved inputs files to daylight-factor-data/logs
Saved outputs files to daylight-factor-data/logs
Saved logs files to daylight-factor-data/logs

> queenbee pollination simulations get --project hello-world -i 5cbdcb5f-fec9-4048-8b59-5e37f8182d8e -f daylight-factor-data/simulation.json
```
