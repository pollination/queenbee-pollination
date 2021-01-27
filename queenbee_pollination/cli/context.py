from pydantic import Field
from queenbee.base.basemodel import BaseModel
from queenbee.cli.context import Context as QueenbeeContext

from ..config import Config as QueenbeePollinationConfig
from ..client import Client


class Context(BaseModel):

    queenbee: QueenbeeContext = Field(
        None,
        description='The queenbee config object'
    )

    config: QueenbeePollinationConfig = Field(
        default_factory=QueenbeePollinationConfig,
    )

    def get_client(self) -> Client:
        self.queenbee.refresh_tokens()
        auth_header = self.queenbee.config.get_auth_header(
            repository_url=self.config.endpoint
        )

        if auth_header is not None:
            self.config.jwt_token = auth_header.split('Bearer ')[-1]
        return self.config.get_client()
