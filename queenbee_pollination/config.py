from pydantic import BaseSettings, Field

from .client import Client


class Config(BaseSettings):

    endpoint: str = Field(
        'https://api.pollination.cloud',
        description='The API endpoint to use when making API calls',
        env='QB_POLLINATION_ENDPOINT',
    )

    token: str = Field(
        None,
        description='The API token used to login to the API',
        env='QB_POLLINATION_TOKEN'
    )

    jwt_token: str = Field(
        None,
        description='The JWT token used too authenticate to the API',
    )

    def get_client(self) -> Client:
        try:
            return Client(
                api_token=self.token,
                access_token=self.jwt_token,
                host=self.endpoint,
            )
        except ValueError as error:
            # Catch stale JWT error
            return Client(
                api_token=self.token,
                host=self.endpoint,
            )
