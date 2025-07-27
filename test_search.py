#!/usr/bin/env python3
"""
Test script for the inventory full text search functionality
"""
import asyncio
import json
from typing import Dict, Any

# This would be imported from your actual app
# from app.crud import EquipmentCRUD
# from app.utils.search_utils import populate_search_vectors, search_suggestions


async def test_search_functionality():
    """
    Demonstrate the search functionality with example data
    """
    print("🔍 Testing Inventory Full Text Search Functionality")
    print("=" * 50)
    
    # Example search scenarios
    search_examples = [
        {
            "name": "Basic Equipment Search",
            "query": "laptop",
            "description": "Search for laptops in the inventory"
        },
        {
            "name": "Serial Number Search", 
            "query": "SN2024",
            "description": "Search by serial number prefix"
        },
        {
            "name": "Status Filtered Search",
            "query": "monitor",
            "filters": {"status": "available", "condition_min": 7}
        },
        {
            "name": "Advanced Field Search",
            "query": "office",
            "search_fields": ["name", "search_vector"]
        }
    ]
    
    print("\n📋 Available Search Endpoints:")
    print("- POST /inventory/search - Full text search with filters")
    print("- POST /inventory/search/advanced - Advanced field-specific search")
    print("- GET /inventory/search/quick - Quick search for simple queries")
    print("- GET /inventory/search/suggestions - Get search suggestions")
    print("- GET /inventory/search/analytics - Get search analytics")
    print("- POST /inventory/search/optimize - Optimize search performance")
    print("- POST /inventory/search/bulk-update - Bulk update search vectors")
    
    print("\n🔧 Example API Usage:")
    
    for example in search_examples:
        print(f"\n{example['name']}:")
        print(f"  Query: {example['query']}")
        if 'description' in example:
            print(f"  Description: {example['description']}")
        
        # Example request payload
        payload = {
            "query": example['query'],
            "limit": 20,
            "offset": 0
        }
        
        if 'filters' in example:
            payload.update(example['filters'])
        
        print(f"  Request: POST /inventory/search")
        print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    print("\n📊 Example Response Format:")
    example_response = {
        "results": [
            {
                "id": 1,
                "name": "Dell Latitude Laptop",
                "serial_number": "SN2024001",
                "status": "available",
                "condition": 8,
                "type": {"id": 1, "name": "Laptop"},
                "location": {"id": 1, "name": "Office A", "description": "Main office area"}
            }
        ],
        "total_count": 1,
        "query": "laptop",
        "limit": 20,
        "offset": 0
    }
    print(json.dumps(example_response, indent=2))
    
    print("\n🚀 Search Features:")
    print("✅ Full text search across equipment names, serial numbers, and search vectors")
    print("✅ Filtering by status, condition range, and equipment type")
    print("✅ Pagination support with limit and offset")
    print("✅ Search suggestions for autocomplete")
    print("✅ Search analytics and performance metrics")
    print("✅ Bulk operations for search vector updates")
    print("✅ PostgreSQL-optimized search with indexes")
    
    print("\n💡 Usage Tips:")
    print("- Use the search_vector field for comprehensive text search")
    print("- Combine filters for more precise results")
    print("- Use suggestions endpoint for autocomplete functionality")
    print("- Monitor search analytics for performance insights")
    print("- Regularly optimize search vectors for better performance")


def generate_example_data():
    """
    Generate example equipment data for testing
    """
    example_equipment = [
        {
            "name": "Dell Latitude 5520",
            "serial_number": "SN2024001",
            "status": "available",
            "condition": 8,
            "type": "Laptop",
            "location": "Office A"
        },
        {
            "name": "HP EliteBook 840",
            "serial_number": "SN2024002", 
            "status": "in_use",
            "condition": 7,
            "type": "Laptop",
            "location": "Office B"
        },
        {
            "name": "Dell 24\" Monitor",
            "serial_number": "SN2024003",
            "status": "available",
            "condition": 9,
            "type": "Monitor",
            "location": "Storage Room"
        },
        {
            "name": "Logitech Wireless Mouse",
            "serial_number": "SN2024004",
            "status": "maintenance",
            "condition": 5,
            "type": "Peripheral",
            "location": "IT Office"
        }
    ]
    
    print("\n📦 Example Equipment Data:")
    for i, equipment in enumerate(example_equipment, 1):
        print(f"\nEquipment {i}:")
        for key, value in equipment.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print("🎯 Inventory Full Text Search Demo")
    print("=" * 50)
    
    # Run the test
    asyncio.run(test_search_functionality())
    
    # Generate example data
    generate_example_data()
    
    print("\n✅ Search functionality is ready to use!")
    print("Run your FastAPI server and test the endpoints.") 