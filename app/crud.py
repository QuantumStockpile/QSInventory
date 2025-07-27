from app import (
    Equipment,
    EquipmentSchema,
    EquipmentType,
    TypeSchema,
    Location,
    LocationSchema,
)
from ms_core import BaseCRUD

from app.models import EquipmentType


class EquipmentCRUD(BaseCRUD[Equipment, EquipmentSchema]):
    model = Equipment  # type: ignore
    schema = EquipmentSchema  # type: ignore


class TypeCRUD(BaseCRUD[EquipmentType, TypeSchema]):
    model = EquipmentType  # type: ignore
    schema = TypeSchema  # type: ignore


class LocationCRUD(BaseCRUD[Location, LocationSchema]):
    model = Location  # type: ignore
    schema = LocationSchema  # type: ignore
