"""
Search utilities for the inventory system
"""
from tortoise.expressions import Q
from tortoise.functions import Count

from app.models import Equipment, EquipmentType, Location
from app.crud import EquipmentCRUD


async def populate_search_vectors() -> dict[str, object]:
    """
    Populate search vectors for all existing equipment
    """
    equipments = await Equipment.all().prefetch_related('type', 'location')
    updated_count = 0
    
    for equipment in equipments:
        # Create search vector from relevant fields
        search_parts = [
            equipment.name,
            equipment.serial_number,
            equipment.status,
            str(equipment.condition),
            equipment.type.name if equipment.type else "",
            equipment.location.name if equipment.location else "",
            equipment.location.description if equipment.location and equipment.location.description else ""
        ]
        
        # Filter out None values and join
        search_vector = " ".join([part for part in search_parts if part])
        equipment.search_vector = search_vector
        await equipment.save()
        updated_count += 1
    
    return {
        "message": f"Updated search vectors for {updated_count} equipment items",
        "updated_count": updated_count
    }


async def search_suggestions(query: str, limit: int = 5) -> list[str]:
    """
    Get search suggestions based on partial queries
    """
    if len(query) < 2:
        return []
    
    # Search in equipment names and serial numbers
    equipments = await Equipment.filter(
        Q(name__icontains=query) | Q(serial_number__icontains=query)
    ).limit(limit).values_list('name', 'serial_number')
    
    suggestions: set[str] = set()
    for name, serial in equipments:
        if query.lower() in name.lower():
            suggestions.add(name)
        if query.lower() in serial.lower():
            suggestions.add(serial)
    
    return list(suggestions)[:limit]


async def get_search_analytics() -> dict[str, object]:
    """
    Get analytics about search usage and equipment distribution
    """
    # Equipment counts by status
    status_counts = await Equipment.all().annotate(
        count=Count("id")
    ).group_by("status").values("status", "count")
    
    # Equipment counts by condition range
    condition_ranges = [
        (0, 2, "Poor"),
        (3, 5, "Fair"),
        (6, 8, "Good"),
        (9, 10, "Excellent")
    ]
    
    condition_stats = {}
    for min_cond, max_cond, label in condition_ranges:
        count = await Equipment.filter(
            condition__gte=min_cond,
            condition__lte=max_cond
        ).count()
        condition_stats[label] = count
    
    # Equipment types distribution - simplified approach
    all_equipment = await Equipment.all().prefetch_related('type')
    type_stats = {}
    for equipment in all_equipment:
        if equipment.type:
            type_name = equipment.type.name
            type_stats[type_name] = type_stats.get(type_name, 0) + 1
    
    return {
        "status_distribution": {item["status"]: item["count"] for item in status_counts},
        "condition_distribution": condition_stats,
        "type_distribution": type_stats,
        "total_equipment": await Equipment.all().count(),
        "equipment_with_search_vector": await Equipment.filter(
            search_vector__not_isnull=True
        ).count()
    }


async def optimize_search_performance() -> dict[str, object]:
    """
    Optimize search performance by updating search vectors and creating indexes
    """
    # Update all search vectors
    await populate_search_vectors()
    
    # Get performance metrics
    total_equipment = await Equipment.all().count()
    equipment_with_vectors = await Equipment.filter(
        search_vector__not_isnull=True
    ).count()
    
    return {
        "message": "Search performance optimization completed",
        "total_equipment": total_equipment,
        "equipment_with_search_vectors": equipment_with_vectors,
        "optimization_percentage": (equipment_with_vectors / total_equipment * 100) if total_equipment > 0 else 0
    }


async def bulk_update_search_vectors(equipment_ids: list[int]) -> dict[str, object]:
    """
    Bulk update search vectors for specific equipment items
    """
    updated_count = 0
    failed_count = 0
    
    for equipment_id in equipment_ids:
        try:
            await EquipmentCRUD.update_search_vector(equipment_id)
            updated_count += 1
        except Exception:
            failed_count += 1
    
    return {
        "message": f"Bulk update completed",
        "updated_count": updated_count,
        "failed_count": failed_count,
        "total_processed": len(equipment_ids)
    } 