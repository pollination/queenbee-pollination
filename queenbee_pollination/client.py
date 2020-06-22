import pollination_sdk as sdk


class Client(object):
    """A Pollination client designed to interact with Workflow and Simulation objects

    """

    def __init__(self, api_token=None, access_token=None, host='https://api.pollination.cloud'):
        config = sdk.Configuration()
        config.host = host

        auth = sdk.UserApi(sdk.ApiClient(config))

        if access_token is None:
            api_token = sdk.LoginDto(
                api_token=api_token
            )

            try:
                auth_response = auth.login(api_token)
            except sdk.rest.ApiException as error:
                if error.status == 403:
                    raise ValueError("Failed to log in... </3")
                raise error

            config.access_token = auth_response.access_token
        else:
            config.access_token = access_token

        self.config = config
        self.auth = sdk.UserApi(sdk.ApiClient(config))
        self.recipes = sdk.RecipesApi(sdk.ApiClient(config))
        self.operators = sdk.OperatorsApi(sdk.ApiClient(config))
        self.simulations = sdk.SimulationsApi(sdk.ApiClient(config))
        self.artifacts = sdk.ArtifactsApi(sdk.ApiClient(config))
        self.projects = sdk.ProjectsApi(sdk.ApiClient(config))

    def get_account(self) -> sdk.models.PrivateUserDto:
        return self.auth.get_me()
