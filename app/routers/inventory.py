from typing import Annotated

from fastapi import Depends, HTTPException, Path
from ms_core import BaseCRUDRouter, DefaultEndpoint, EndpointConfig

from app import EquipmentCRUD, EquipmentSchema
from app.dependencies import require_role
from app.models import EquipmentHistoryEntry
from app.schemas import EquipmentCreate, EquipmentSchema, TokenIntrospect

router = BaseCRUDRouter(
    EquipmentCRUD,
    EquipmentSchema,
    EquipmentCreate,
    exclude_endpoints=[DefaultEndpoint.UPDATE],
    endpoint_configs={
        DefaultEndpoint.CREATE: EndpointConfig(
            path="/",
            methods=["POST"],
            dependencies=[require_role("admin")],
        ),
        DefaultEndpoint.DELETE: EndpointConfig(
            path="/{item_id}", methods=["DELETE"], dependencies=[require_role("admin")]
        ),
    },
    tags=["inventory"],
    prefix="/inventory",
    dependencies=[Depends(require_role("user"))],
)


async def audit_save(
    sub: str, old: EquipmentSchema, new: EquipmentSchema, is_created: bool
):
    await EquipmentHistoryEntry.create(
        equipment_id=new.id,
        action="create" if is_created else "update",
        old=old.model_dump_json(exclude=["history"]),
        new=new.model_dump_json(exclude=["history"]),
        email=sub,
    )


@router.patch("/{item_id}/patch")
async def patch_equipment(
    user: Annotated[TokenIntrospect, Depends(require_role("admin"))],
    payload: EquipmentCreate,
    item_id: int = Path(),
) -> EquipmentSchema:
    old = await EquipmentCRUD.get_by(id=item_id)

    if not old:
        raise HTTPException(404, detail="Item not found")

    new = await router._update(payload, item_id)

    await audit_save(user.sub, old, new, False)

    return new
