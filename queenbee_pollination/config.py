from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

from .client import Client


class Config(BaseSettings):

    endpoint: str = Field(
        default='https://api.pollination.solutions',
        description='The API endpoint to use when making API calls',
        validation_alias='POLLINATION_ENDPOINT',
    )

    token: Optional[str] = Field(
        default=None,
        description='The API token used to login to the API',
        validation_alias='POLLINATION_TOKEN'
    )

    jwt_token: Optional[str] = Field(
        default=None,
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
