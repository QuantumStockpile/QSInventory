from fastapi import Depends
from ms_core import BaseCRUDRouter, DefaultEndpoint, EndpointConfig

from app.crud import TypeCRUD
from app.dependencies import require_role
from app.schemas import TypeCreate, TypeSchema

router = BaseCRUDRouter(
    TypeCRUD,
    TypeSchema,
    TypeCreate,
    prefix="/types",
    tags=["equipment_types"],
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
