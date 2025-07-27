from fastapi import Depends
from ms_core import BaseCRUDRouter, DefaultEndpoint, EndpointConfig

from app.crud import LocationCRUD
from app.dependencies import require_role
from app.schemas import LocationCreate, LocationSchema

router = BaseCRUDRouter(
    LocationCRUD,
    LocationSchema,
    LocationCreate,
    prefix="/locations",
    tags=["locations"],
    endpoint_configs={
        DefaultEndpoint.CREATE: EndpointConfig(
            path="/",
            methods=["POST"],
            dependencies=[require_role("admin")],
        ),
        DefaultEndpoint.DELETE: EndpointConfig(
            path="/{item_id}", methods=["DELETE"], dependencies=[require_role("admin")]
        ),
        DefaultEndpoint.UPDATE: EndpointConfig(
            path="/{item_id}", methods=["PATCH"], dependencies=[require_role("admin")]
        ),
    },
    dependencies=[Depends(require_role("user"))],
)
