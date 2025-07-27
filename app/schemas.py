from datetime import datetime
from pydantic import BaseModel, Field
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

# Create a search-specific schema that excludes the history field
EquipmentSearchSchema = pydantic_model_creator(
    Equipment,
    name="EquipmentSearchSchema",
    exclude=("history",)  # Exclude the history field for search results
)

TypeSchema = pydantic_model_creator(EquipmentType)
TypeCreate = pydantic_model_creator(
    EquipmentType, name="TypeCreate", exclude_readonly=True
)

LocationSchema = pydantic_model_creator(Location)
LocationCreate = pydantic_model_creator(
    Location, name="LocationCreate", exclude_readonly=True
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=255, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    status: str | None = Field(None, description="Filter by equipment status")
    condition_min: int | None = Field(None, ge=0, le=10, description="Minimum condition rating")
    condition_max: int | None = Field(None, ge=0, le=10, description="Maximum condition rating")
    search_fields: list[str] | None = Field(None, description="Specific fields to search in")


class AdvancedSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=255, description="Search query")
    search_fields: list[str] | None = Field(
        default=["name", "serial_number", "search_vector"],
        description="Fields to search in"
    )
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class SearchResponse(BaseModel):
    results: list[EquipmentSearchSchema]
    total_count: int
    query: str
    limit: int
    offset: int


class EquipmentStats(BaseModel):
    total_equipment: int
    status_distribution: dict[str, int]
    average_condition: float


class TokenIntrospect(BaseModel):
    role: int | None
    scopes: list[str] = []
    sub: str
    exp: datetime
    token_type: str


class UserSchema(TokenIntrospect):
    role_name: str | None = None
