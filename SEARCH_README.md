# Inventory Full Text Search

This document describes the full text search functionality implemented for the QSInventory system using Tortoise ORM.

## Overview

The search system provides comprehensive full text search capabilities across equipment inventory, including:

- **Full text search** across equipment names, serial numbers, and search vectors
- **Advanced filtering** by status, condition, and equipment type
- **Search suggestions** for autocomplete functionality
- **Search analytics** for performance monitoring
- **Bulk operations** for search vector management

## Database Schema Changes

### Equipment Model Updates

The `Equipment` model has been enhanced with:

```python
class Equipment(ExtendedAbstractModel):
    # ... existing fields ...
    search_vector = fields.TextField(null=True)  # For full text search
    
    class Meta:
        table = "equipments"
        indexes = [
            ("name", "serial_number"),  # Composite index for better search performance
        ]
```

### Migration

A new migration has been created to add the search functionality:

```bash
# Run the migration to add search_vector field and indexes
aerich upgrade
```

## API Endpoints

### Core Search Endpoints

#### 1. Full Text Search
```http
POST /inventory/search
```

**Request Body:**
```json
{
  "query": "laptop",
  "limit": 20,
  "offset": 0,
  "status": "available",
  "condition_min": 7,
  "condition_max": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Dell Latitude 5520",
      "serial_number": "SN2024001",
      "status": "available",
      "condition": 8,
      "type": {"id": 1, "name": "Laptop"},
      "location": {"id": 1, "name": "Office A"}
    }
  ],
  "total_count": 1,
  "query": "laptop",
  "limit": 20,
  "offset": 0
}
```

#### 2. Advanced Search
```http
POST /inventory/search/advanced
```

**Request Body:**
```json
{
  "query": "office",
  "search_fields": ["name", "search_vector"],
  "limit": 20,
  "offset": 0
}
```

#### 3. Quick Search
```http
GET /inventory/search/quick?q=laptop&limit=10
```

### Utility Endpoints

#### 4. Search Suggestions
```http
GET /inventory/search/suggestions?q=lap&limit=5
```

**Response:**
```json
{
  "query": "lap",
  "suggestions": ["Dell Latitude 5520", "HP EliteBook 840"],
  "count": 2
}
```

#### 5. Search Analytics
```http
GET /inventory/search/analytics
```

**Response:**
```json
{
  "status_distribution": {
    "available": 15,
    "in_use": 8,
    "maintenance": 3
  },
  "condition_distribution": {
    "Poor": 2,
    "Fair": 5,
    "Good": 12,
    "Excellent": 7
  },
  "type_distribution": {
    "Laptop": 10,
    "Monitor": 8,
    "Peripheral": 8
  },
  "total_equipment": 26,
  "equipment_with_search_vector": 26
}
```

#### 6. Search Optimization
```http
POST /inventory/search/optimize
```

#### 7. Bulk Update Search Vectors
```http
POST /inventory/search/bulk-update
```

**Request Body:**
```json
[1, 2, 3, 4, 5]
```

#### 8. Update Single Equipment Search Vector
```http
POST /inventory/{item_id}/update-search
```

## Search Features

### 1. Full Text Search
- Searches across equipment names, serial numbers, and search vectors
- Case-insensitive matching
- Partial word matching

### 2. Filtering Options
- **Status**: Filter by equipment status (available, in_use, maintenance, etc.)
- **Condition Range**: Filter by condition rating (0-10)
- **Equipment Type**: Filter by equipment type
- **Location**: Filter by location

### 3. Pagination
- **limit**: Maximum number of results (default: 50, max: 100)
- **offset**: Number of results to skip for pagination

### 4. Search Vector Management
- Automatic search vector updates when equipment is created/modified
- Manual search vector updates for individual items
- Bulk search vector updates for multiple items
- Search vector optimization for performance

## Implementation Details

### CRUD Operations

The `EquipmentCRUD` class has been extended with search methods:

```python
class EquipmentCRUD(BaseCRUD[Equipment, EquipmentSchema]):
    @classmethod
    async def search_equipment(cls, query: str, limit: int = 50, offset: int = 0, ...):
        # Full text search implementation
    
    @classmethod
    async def search_equipment_advanced(cls, query: str, search_fields: List[str], ...):
        # Advanced search implementation
    
    @classmethod
    async def update_search_vector(cls, equipment_id: int):
        # Update search vector for equipment
```

### Search Utilities

Utility functions in `app/utils/search_utils.py`:

- `populate_search_vectors()`: Populate search vectors for all equipment
- `search_suggestions()`: Get search suggestions for autocomplete
- `get_search_analytics()`: Get search analytics and statistics
- `optimize_search_performance()`: Optimize search performance
- `bulk_update_search_vectors()`: Bulk update search vectors

### Search Vector Generation

Search vectors are automatically generated from:
- Equipment name
- Serial number
- Status
- Condition rating
- Equipment type name
- Location name and description

## Performance Considerations

### Database Indexes
- Composite index on (name, serial_number)
- Index on search_vector field
- Automatic index creation via migration

### Search Optimization
- Use search vectors for comprehensive text search
- Implement pagination to limit result sets
- Use database indexes for faster queries
- Regular search vector updates for accuracy

### Best Practices
1. **Regular Updates**: Update search vectors when equipment data changes
2. **Pagination**: Always use pagination for large result sets
3. **Filtering**: Use filters to narrow down search results
4. **Monitoring**: Monitor search analytics for performance insights

## Usage Examples

### Basic Search
```python
# Search for laptops
results = await EquipmentCRUD.search_equipment(
    query="laptop",
    limit=20,
    offset=0
)
```

### Filtered Search
```python
# Search for available equipment in good condition
results = await EquipmentCRUD.search_equipment(
    query="monitor",
    status="available",
    condition_min=7,
    condition_max=10
)
```

### Advanced Search
```python
# Search specific fields
results = await EquipmentCRUD.search_equipment_advanced(
    query="office",
    search_fields=["name", "search_vector"]
)
```

## Testing

Run the test script to see the search functionality in action:

```bash
python test_search.py
```

This will demonstrate:
- Available search endpoints
- Example API usage
- Response formats
- Search features and capabilities

## Security

All search endpoints require authentication:
- **User role**: Required for basic search operations
- **Admin role**: Required for optimization and bulk update operations

## Future Enhancements

Potential improvements for the search system:

1. **Fuzzy Search**: Implement fuzzy matching for typos
2. **Search Ranking**: Add relevance scoring for search results
3. **Search History**: Track search queries for analytics
4. **Elasticsearch Integration**: For more advanced search capabilities
5. **Real-time Search**: Implement real-time search suggestions

## Troubleshooting

### Common Issues

1. **Search vectors not updating**: Run the optimization endpoint
2. **Slow search performance**: Check database indexes and run optimization
3. **No search results**: Verify search vectors are populated

### Debugging

Use the analytics endpoint to check:
- Total equipment count
- Equipment with search vectors
- Search performance metrics

## Conclusion

The full text search functionality provides a robust and scalable solution for searching equipment inventory. The implementation leverages Tortoise ORM's capabilities while providing comprehensive search features and performance optimizations. 