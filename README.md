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

You will need your Pollination API token `Key` and `ID` which can be found on your [account page](https://pollination.cloud/pollination-ui/#/profile).

You will be prompted to do so by the CLI as demonstrated below:

```console
> queenbee pollination workflows

Looks like this is your first time logging in.

To interract with Pollination you need to save authentication credentials in C:\Users\me\.queenbee

This tool will walk you through this process:
        
Enter your API Token ID: f15be412fe6f41dc01440f2363a13fed
Enter your API Token Secret: 
Logging in using api tokens...
Success!

You can now run queenbee pollination commands as an authenticated user!
Check the and modify the config file at your own risk: C:\Users\me\.queenbee
```

You can now check the configuration file saved at the path indicated in you command line. in the case of the example above the path to the config file is: `C:\Users\me\.queenbee`.

## Hello World!

We have compiled a quick demo workflow for you to test out the queenbee-pollination plugin.

Copy and save the text below into a file called `hello.yaml`.

```yaml
type: workflow
name: hello-world

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

Succesfully updated workflow hello-world
ID: 7ceff0de-2ed9-4e89-b943-9d3f2754ad0f
```

2. List your existing workflows

```console
> queenbee pollination workflows list

  ID                                    Name
------------------------------------  ------------------------------
2444c12f-06f3-47c9-9566-e71860017961  hello-world
```

3. Schedule a simulation to run using the hello-world workflow template 

```console
> queenbee pollination simulations schedule -w 2444c12f-06f3-47c9-9566-e71860017961

Succesfully created simulation: f01b6926-c953-4b4d-be7f-945aafa1ec5c
```

4. Resubmit the simulation a couple of times to create multiple simulations.
   
```console
> queenbee pollination simulations resubmit -i f01b6926-c953-4b4d-be7f-945aafa1ec5c

Succesfully created simulation: 7b78543f-e929-4876-bb23-88775f69ffc9
```

5. List all running simulations

```console
> queenbee pollination simulations list

ID                                    Workflow                        Phase      Completed    Stated At                  Finished At
------------------------------------  ------------------------------  ---------  -----------  -------------------------  -------------------------
f01b6926-c953-4b4d-be7f-945aafa1ec5c  hello-world                     Succeeded  True         2019-12-11 07:59:05+00:00  2019-12-11 07:59:23+00:00
c7a681d2-2b1c-414e-bc9e-88cf0bfcaf84  hello-world                     Succeeded  True         2019-12-11 07:57:50+00:00  2019-12-11 07:57:50+00:00
e5fa5b0b-7253-47cd-a6a0-63b2f5249cf4  hello-world                     Succeeded  True         2019-12-11 07:54:46+00:00  2019-12-11 07:54:46+00:00
e556c46e-f71e-4bd5-927b-f4ce6a1d1e73  hello-world                     Succeeded  True         2019-12-11 07:49:39+00:00  2019-12-11 07:49:39+00:00
```

6. Retrieve the logs from the latest ran workflow. The command below will download all logs into the `dump/logs/` folder.

```console
> queenbee pollination simulations download -i f01b6926-c953-4b4d-be7f-945aafa1ec5c -f dump -a logs

```

7. Retrieve all persisted simulation data to a local folder called `sim-data`.

```console
> queenbee pollination simulations download -i f01b6926-c953-4b4d-be7f-945aafa1ec5c -f sim-data

```

8. Inpect simulation metadata in detail. Get and save the simulation object into a file called `dump.json`

```console
> queenbee pollination simulations get -i f01b6926-c953-4b4d-be7f-945aafa1ec5c -f dump.json
```

## Artifacts

You can also upload raw files to the Pollination storage bucket. These files will then be accessible to any simulation you run thereafter.

Create a folder called `test` and place some files in it. You can then upload these files using the following command:

```console
> queenbee pollination artifacts upload -f test

Uploaded test/file1.txt
Uploaded test/file2.txt
Uploaded test/file3.txt

```