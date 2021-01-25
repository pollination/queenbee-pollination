import pollination_sdk as sdk


class Client(object):
    """A Pollination client designed to interact with Workflow and Simulation objects."""

    def __init__(self, api_token=None, access_token=None, host='https://api.pollination.cloud'):
        config = sdk.Configuration(
            api_key={'APIKeyAuth': api_token}
        )
        config.access_token = access_token
        config.host = host

        self.config = config
        self.auth = sdk.UserApi(sdk.ApiClient(config))
        self.recipes = sdk.RecipesApi(sdk.ApiClient(config))
        self.plugins = sdk.PluginsApi(sdk.ApiClient(config))
        self.runs = sdk.RunsApi(sdk.ApiClient(config))
        self.artifacts = sdk.ArtifactsApi(sdk.ApiClient(config))
        self.projects = sdk.ProjectsApi(sdk.ApiClient(config))

    def get_account(self) -> sdk.models.UserPrivate:
        return self.auth.get_me()
