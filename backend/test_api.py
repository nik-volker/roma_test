#!/usr/bin/env python
"""Test script for API"""
import json
import sys

sys.path.insert(0, ".")

import requests

BASE_URL = "http://localhost:5000"

# Test 1: Health check
print("=" * 60)
print("TEST 1: /api/health")
print("=" * 60)
try:
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Normal message
print("\n" + "=" * 60)
print("TEST 2: /api/chat - Normal message")
print("=" * 60)
try:
    payload = {"message": "Мы не разговариваем друг с другом 3 дня"}
    resp = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")

# Test 3: Crisis detection
print("\n" + "=" * 60)
print("TEST 3: /api/chat - Crisis message")
print("=" * 60)
try:
    payload = {"message": "Я не хочу жить"}
    resp = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Tests completed!")
print("=" * 60)
