from typing import Annotated

from fastapi import Depends, HTTPException, Path, Query
from ms_core import BaseCRUDRouter, DefaultEndpoint, EndpointConfig

from app import EquipmentCRUD, EquipmentSchema
from app.dependencies import require_role
from app.models import EquipmentHistoryEntry
from app.schemas import (
    EquipmentCreate, 
    EquipmentSchema,
    EquipmentSearchSchema,
    TokenIntrospect,
    SearchRequest,
    AdvancedSearchRequest,
    SearchResponse,
    EquipmentStats
)
from app.utils.search_utils import (
    search_suggestions,
    get_search_analytics,
    optimize_search_performance,
    bulk_update_search_vectors
)

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


@router.post("/search", response_model=SearchResponse)
async def search_equipment(
    search_request: SearchRequest,
    user: Annotated[TokenIntrospect, Depends(require_role("user"))]
) -> SearchResponse:
    """
    Full text search for equipment with optional filters
    """
    results = await EquipmentCRUD.search_equipment(
        query=search_request.query,
        limit=search_request.limit,
        offset=search_request.offset,
        status=search_request.status,
        condition_min=search_request.condition_min,
        condition_max=search_request.condition_max
    )
    
    # Get total count for pagination
    from app.models import Equipment
    from tortoise.expressions import Q
    
    count_query = Q(
        Q(name__icontains=search_request.query) |
        Q(serial_number__icontains=search_request.query) |
        Q(search_vector__icontains=search_request.query)
    )
    
    if search_request.status:
        count_query &= Q(status=search_request.status)
    if search_request.condition_min is not None:
        count_query &= Q(condition__gte=search_request.condition_min)
    if search_request.condition_max is not None:
        count_query &= Q(condition__lte=search_request.condition_max)
    
    total_count = await Equipment.filter(count_query).count()
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        query=search_request.query,
        limit=search_request.limit,
        offset=search_request.offset
    )


@router.post("/search/advanced", response_model=SearchResponse)
async def advanced_search_equipment(
    search_request: AdvancedSearchRequest,
    user: Annotated[TokenIntrospect, Depends(require_role("user"))]
) -> SearchResponse:
    """
    Advanced search with field-specific search capabilities
    """
    results = await EquipmentCRUD.search_equipment_advanced(
        query=search_request.query,
        search_fields=search_request.search_fields,
        limit=search_request.limit,
        offset=search_request.offset
    )
    
    # Get total count for pagination
    from app.models import Equipment
    from tortoise.expressions import Q
    
    count_conditions = []
    for field in search_request.search_fields:
        if hasattr(Equipment, field):
            count_conditions.append(Q(**{f"{field}__icontains": search_request.query}))
    
    if count_conditions:
        count_query = count_conditions[0]
        for condition in count_conditions[1:]:
            count_query |= condition
        total_count = await Equipment.filter(count_query).count()
    else:
        total_count = len(results)
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        query=search_request.query,
        limit=search_request.limit,
        offset=search_request.offset
    )


@router.get("/search/quick")
async def quick_search(
    user: Annotated[TokenIntrospect, Depends(require_role("user"))],
    q: str = Query(..., min_length=1, max_length=100, description="Quick search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of results"),
) -> SearchResponse:
    """
    Quick search endpoint for simple text queries
    """
    results = await EquipmentCRUD.search_equipment(
        query=q,
        limit=limit,
        offset=0
    )
    
    # Get total count
    from app.models import Equipment
    from tortoise.expressions import Q
    
    total_count = await Equipment.filter(
        Q(name__icontains=q) |
        Q(serial_number__icontains=q) |
        Q(search_vector__icontains=q)
    ).count()
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        query=q,
        limit=limit,
        offset=0
    )


@router.get("/search/stats", response_model=EquipmentStats)
async def get_equipment_stats(
    user: Annotated[TokenIntrospect, Depends(require_role("user"))]
) -> EquipmentStats:
    """
    Get equipment statistics for search analytics
    """
    stats = await EquipmentCRUD.get_equipment_stats()
    return EquipmentStats(**stats)


@router.post("/{item_id}/update-search")
async def update_equipment_search_vector(
    user: Annotated[TokenIntrospect, Depends(require_role("admin"))],
    item_id: int = Path(),
) -> dict[str, object]:
    """
    Manually update the search vector for a specific equipment item
    """
    equipment = await EquipmentCRUD.get_by(id=item_id)
    if not equipment:
        raise HTTPException(404, detail="Equipment not found")
    
    await EquipmentCRUD.update_search_vector(item_id)
    return {"message": "Search vector updated successfully", "equipment_id": item_id}


@router.get("/search/suggestions")
async def get_search_suggestions(
    user: Annotated[TokenIntrospect, Depends(require_role("user"))],
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of suggestions"),
) -> dict[str, object]:
    """
    Get search suggestions based on partial queries
    """
    suggestions = await search_suggestions(q, limit)
    return {
        "query": q,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@router.get("/search/analytics")
async def get_search_analytics_data(
    user: Annotated[TokenIntrospect, Depends(require_role("user"))]
) -> dict[str, object]:
    """
    Get detailed search analytics and equipment distribution
    """
    analytics = await get_search_analytics()
    return analytics


@router.post("/search/optimize")
async def optimize_search(
    user: Annotated[TokenIntrospect, Depends(require_role("admin"))]
) -> dict[str, object]:
    """
    Optimize search performance by updating all search vectors
    """
    result = await optimize_search_performance()
    return result


@router.post("/search/bulk-update")
async def bulk_update_search_vectors_endpoint(
    equipment_ids: list[int],
    user: Annotated[TokenIntrospect, Depends(require_role("admin"))]
) -> dict[str, object]:
    """
    Bulk update search vectors for multiple equipment items
    """
    if not equipment_ids:
        raise HTTPException(400, detail="Equipment IDs list cannot be empty")
    
    if len(equipment_ids) > 100:
        raise HTTPException(400, detail="Cannot process more than 100 items at once")
    
    result = await bulk_update_search_vectors(equipment_ids)
    return result
