from tortoise.expressions import Q
from tortoise.functions import Count, Avg

from app import (
    Equipment,
    EquipmentSchema,
    EquipmentSearchSchema,
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

    @classmethod
    async def search_equipment(
        cls, 
        query: str, 
        limit: int = 50, 
        offset: int = 0,
        status: str | None = None,
        condition_min: int | None = None,
        condition_max: int | None = None
    ) -> list[EquipmentSearchSchema]:
        """
        Full text search for equipment with optional filters
        """
        # Build the base query
        search_conditions = []
        
        # Text search across multiple fields
        text_search = Q(
            Q(name__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(search_vector__icontains=query)
        )
        search_conditions.append(text_search)
        
        # Add optional filters
        if status:
            search_conditions.append(Q(status=status))
        
        if condition_min is not None:
            search_conditions.append(Q(condition__gte=condition_min))
            
        if condition_max is not None:
            search_conditions.append(Q(condition__lte=condition_max))
        
        # Combine all conditions
        final_query = search_conditions[0]
        for condition in search_conditions[1:]:
            final_query &= condition
        
        # Execute the search
        equipments = await Equipment.filter(final_query).prefetch_related(
            'type', 'location'
        ).limit(limit).offset(offset)
        
        return [EquipmentSearchSchema.from_orm(equipment) for equipment in equipments]

    @classmethod
    async def search_equipment_advanced(
        cls,
        query: str,
        search_fields: list[str] | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[EquipmentSearchSchema]:
        """
        Advanced search with PostgreSQL full text search capabilities
        """
        if not search_fields:
            search_fields = ['name', 'serial_number', 'search_vector']
        
        # Build search conditions for specified fields
        search_conditions = []
        for field in search_fields:
            if hasattr(Equipment, field):
                search_conditions.append(Q(**{f"{field}__icontains": query}))
        
        if not search_conditions:
            # Fallback to basic search
            search_conditions = [
                Q(name__icontains=query) |
                Q(serial_number__icontains=query)
            ]
        
        # Combine conditions with OR
        final_query = search_conditions[0]
        for condition in search_conditions[1:]:
            final_query |= condition
        
        equipments = await Equipment.filter(final_query).prefetch_related(
            'type', 'location'
        ).limit(limit).offset(offset)
        
        return [EquipmentSearchSchema.from_orm(equipment) for equipment in equipments]

    @classmethod
    async def update_search_vector(cls, equipment_id: int) -> None:
        """
        Update the search vector for a specific equipment item
        """
        equipment = await Equipment.get(id=equipment_id).prefetch_related('type', 'location')
        if equipment:
            # Create a search vector from relevant fields
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

    @classmethod
    async def get_equipment_stats(cls) -> dict[str, object]:
        """
        Get statistics about equipment for search analytics
        """
        total_count = await Equipment.all().count()
        
        # Get status distribution
        status_counts = await Equipment.all().annotate(
            count=Count("id")
        ).group_by("status").values("status", "count")
        
        # Get average condition using a simpler approach
        all_equipment = await Equipment.all()
        conditions = [eq.condition for eq in all_equipment]
        avg_condition = sum(conditions) / len(conditions) if conditions else 0
        
        return {
            "total_equipment": total_count,
            "status_distribution": {item["status"]: item["count"] for item in status_counts},
            "average_condition": round(avg_condition, 2)
        }


class TypeCRUD(BaseCRUD[EquipmentType, TypeSchema]):
    model = EquipmentType  # type: ignore
    schema = TypeSchema  # type: ignore


class LocationCRUD(BaseCRUD[Location, LocationSchema]):
    model = Location  # type: ignore
    schema = LocationSchema  # type: ignore
