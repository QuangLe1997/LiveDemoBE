"""Base model"""
# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
from datetime import datetime, timezone

from pydantic import BaseConfig, BaseModel


class MyModel(BaseModel):
    """base model"""

    class Config(BaseConfig):
        """config"""

        allow_population_by_alias = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }
