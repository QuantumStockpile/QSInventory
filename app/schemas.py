from datetime import datetime
from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import Equipment, EquipmentType, Location

Tortoise.init_models(["app.models"], "models")

EquipmentSchema = pydantic_model_creator(Equipment)
EquipmentCreate = pydantic_model_creator(
    Equipment,
    name="EquipmentCreate",
    exclude_readonly=True,
)

TypeSchema = pydantic_model_creator(EquipmentType)
TypeCreate = pydantic_model_creator(
    EquipmentType, name="TypeCreate", exclude_readonly=True
)

LocationSchema = pydantic_model_creator(Location)
LocationCreate = pydantic_model_creator(
    Location, name="LocationCreate", exclude_readonly=True
)


class TokenIntrospect(BaseModel):
    role: int | None
    scopes: list[str] = []
    sub: str
    exp: datetime
    token_type: str


class UserSchema(TokenIntrospect):
    role_name: str | None = None
