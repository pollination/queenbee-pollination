from datetime import datetime
from uuid import uuid4
import json

from pollination_sdk import Configuration, ApiClient, WorkflowsApi, \
    SimulationsApi, AuthenticationApi, Token, ArtifactsApi
import pollination_sdk
from pollination_sdk.rest import ApiException
from queenbee.schema.workflow import Workflow

class Client(object):
    """A Pollination client designed to interact with Workflow and Simulation objects

    """

    def __init__(self, api_key_id=None, api_key_secret=None, access_token=None, host='https://api.pollination.cloud'):
        config = Configuration()
        config.host = host

        auth = AuthenticationApi()
        if access_token is None:
            api_token = Token(
                id=api_key_id,
                secret=api_key_secret
                )

            try:
                auth_response = auth.login(api_token)
            except ApiException as e:
                if e.status == 403:
                    raise ValueError("Failed to log in... </3")
                raise e

            config.access_token = auth_response.access_token
            auth = AuthenticationApi(ApiClient(config))
        else:
            config.access_token = access_token
            # auth = AuthenticationApi(ApiClient(config))
            # auth.get_api_token()
            # try:
            #     auth.get_api_token()
            # except ApiException as e:
            #     if e.status == 403:
            #         raise ValueError("Expired or incorrect Access Token")
            #     else:
            #         raise e

        self.config = config
        self.auth = auth
        self.workflows = WorkflowsApi(ApiClient(config))
        self.simulations = SimulationsApi(ApiClient(config))
        self.artifacts = ArtifactsApi(ApiClient(config))
