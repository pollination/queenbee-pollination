from datetime import datetime
from uuid import uuid4
import json

from pollination_sdk import Configuration, ApiClient, WorkflowsApi, \
    SimulationsApi, UserApi, ArtifactsApi, ProjectsApi
import pollination_sdk
from pollination_sdk.rest import ApiException
from queenbee.schema.workflow import Workflow


class Client(object):
    """A Pollination client designed to interact with Workflow and Simulation objects

    """

    def __init__(self, api_token=None, access_token=None, host='https://api.pollination.cloud'):
        config = Configuration()
        config.host = host

        auth = UserApi(ApiClient(config))

        if access_token is None:
            api_token = pollination_sdk.LoginDto(
                api_token=api_token
            )

            try:
                auth_response = auth.login(api_token)
            except ApiException as e:
                if e.status == 403:
                    raise ValueError("Failed to log in... </3")
                raise e

            config.access_token = auth_response.access_token
        else:
            config.access_token = access_token

        self.config = config
        self.auth = auth = UserApi(ApiClient(config))
        self.workflows = WorkflowsApi(ApiClient(config))
        self.simulations = SimulationsApi(ApiClient(config))
        self.artifacts = ArtifactsApi(ApiClient(config))
        self.projects = ProjectsApi(ApiClient(config))
