# queenbee-pollination

queenbee-pollination extends [queenbee](https://github.com/pollination/queenbee) in order to interact with the [Pollination API](https://api.pollination.solutions).

## Installation

You can install this as a cli tool using the following command:

```console
pip install queenbee-pollination[cli]
```

## CLI QuickStart


### Authentication

The CLI tool will authenticate to the Pollination API in one of two ways:

#### Env Vars

Set the following environment variable as your API token before running commands `POLLINATION_TOKEN`.

Example for a bash shell:

```console
> export POLLINATION_TOKEN=<some-long-token-string>

> queenbee pollination project simulations list --project test-project --owner ladybug-tools
```

#### Queenbee Config

Re-use pollination auth set in your queenbee config. You can do so by using this command:

```console
> queenbee config auth add pollination YOUR_POLLINATION_API_KEY
```

### Push

You can push recipes and operators to the Pollination platform to share them with others or use them within simulations.

To push a recipe called `my-cool-recipe` to Pollination platform use:

```console
> queenbee pollination push recipe path/to/my-cool-recipe
```

You can push a recipe or operator too a specific pollination account by specifying the `--owner` flag. You can overwrite the resource's tag by using the `--tag` flag. Here is an example of pushing the `honeybee-radiance` operator to the `ladybug-tools` account and specifying a tag of `v0.0.0`.

```console
> queenbee pollination push operator ../garden/operators/honeybee-radiance --tag v0.0.0 --owner ladybug-tools
```

### Pull

You can pull recipes and operators from Pollination onto your machine by using the `pull` commands.

You can pull the latest version of `my-cool-recipe` from your pollination account by running:

```console
> queenbee pollination pull recipe my-cool-recipe
```

You can pull the `honeybee-radiance` operator from the `ladybug-tools` account and tag `v0.0.0` by running:

```console
> queenbee pollination pull operator honeybee-radiance --owner ladybug-tools --tag v0.0.0
```

**Note:** You can specify a folder to download the recipe/operator to by specifying the `--path` option flag.


### Projects

The project section of the CLI lets users upload files to a project and schedule simulations.

#### Folder

A user can upload or delete files in a project folder. To do so use the following commands:

##### Upload

You can upload artifacts to a project called `test-projectect` by using this command:

```console
> queenbee pollination project upload path/to/file/or/folder --project test-projectect
```

You can upload artifacts to a project belonging to another user or org:

```console
> queenbee pollination project upload path/to/file/or/folder --project test-projectect --owner ladybug-tools
```

##### Delete

You can delete all files in a project folder:

```console
> queenbee pollination project delete --project test-projectect
```

You can delete specific files in a project folder:

```console
> queenbee pollination project delete --project test-projectect --path some/subpath/to/a/file
```


#### Simulations

For a given project you can list, submit or download simulations.

##### List

```console
> queenbee pollination project simulation list -p test-projectect
```

##### Submit

You can submit a simulation without needing to specify any inputs (if the simulation does not require any!). The recipe to be used is specified in the following format `{owner}/{recipe-name}:{tag}`:

```console
> queenbee pollination project simulation submit chuck/first-test:0.0.1 -p demo
```

If you want to specify inputs you can point to an inputs file (`json` or `yaml`) which must represent a [Queenbee Workflow Argument](https://www.ladybug.tools/queenbee/_static/redoc-workflow.html#tag/arguments_model) object.

```console
> queenbee pollination project simulation submit ladybug-tools/daylight-factor:latest --project demo --inputs path/to/inputs.yml
```

##### Download

Once a simulation is complete you can download all inputs, outputs and logs to you machine. Here is an example downloading data from a simulation with an ID of `22c75263-c8ba-42d0-a1b8-bd3107eb6b51` from a project with name `demo` by using the following command:

```console
> queenbee pollination project simulation download --project demo  --id 22c75263-c8ba-42d0-a1b8-bd3107eb6b51
```

