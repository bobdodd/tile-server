#!/usr/bin/env python3
"""Test script to validate Overpass API query"""

import requests

# Toronto downtown bounds
bounds = {
    'north': 43.66,
    'south': 43.63,
    'east': -79.36,
    'west': -79.41
}

# Create simple test query
bbox = f"{bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']}"
test_query = f"""[out:xml][timeout:300];
(
  way["building"]({bbox});
  way["highway"]({bbox});
);
out body;
>;
out skel qt;"""

print("Testing Overpass query:")
print(test_query)
print("\nSending request...")

try:
    response = requests.post(
        'https://overpass-api.de/api/interpreter',
        data=test_query,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    if not response.ok:
        print(f"Error response: {response.text}")
    else:
        print("✅ Query successful!")
        
except Exception as e:
    print(f"❌ Error: {e}")