#!/usr/bin/env python
"""Test script for frontend functionality"""
import json
import time
import requests

# Test 1: Check if frontend server is running
print("=" * 60)
print("TEST 1: Frontend server (port 8000)")
print("=" * 60)
try:
    resp = requests.get("http://localhost:8000", timeout=5)
    print(f"✅ Frontend server: {resp.status_code}")
    if "AI Relationship Consultant" in resp.text:
        print("✅ HTML contains expected title")
    else:
        print("❌ HTML title not found")
except Exception as e:
    print(f"❌ Frontend server error: {e}")

# Test 2: Check backend connectivity from frontend perspective
print("\n" + "=" * 60)
print("TEST 2: Backend connectivity (port 5000)")
print("=" * 60)
try:
    resp = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"✅ Backend health: {resp.status_code}")
    result = resp.json()
    print(f"✅ Response: {result}")
except Exception as e:
    print(f"❌ Backend connectivity error: {e}")

# Test 3: Test chat endpoint
print("\n" + "=" * 60)
print("TEST 3: Chat endpoint test")
print("=" * 60)
try:
    payload = {"message": "Test message", "language": "en"}
    resp = requests.post("http://localhost:5000/api/chat", json=payload, timeout=30)
    print(f"✅ Chat endpoint: {resp.status_code}")
    result = resp.json()
    print(f"✅ Detected state: {result.get('detected_state')}")
    print(f"✅ Risk level: {result.get('risk_level')}")
    print(f"✅ Message length: {len(result.get('message', ''))} chars")
except Exception as e:
    print(f"❌ Chat endpoint error: {e}")

# Test 4: Backward compatibility without language field
print("\n" + "=" * 60)
print("TEST 4: Chat endpoint backward compatibility")
print("=" * 60)
try:
    payload = {"message": "We have not talked properly for days"}
    resp = requests.post("http://localhost:5000/api/chat", json=payload, timeout=30)
    print(f"✅ Chat endpoint without language: {resp.status_code}")
    result = resp.json()
    print(f"✅ Detected state: {result.get('detected_state')}")
    print(f"✅ Risk level: {result.get('risk_level')}")
except Exception as e:
    print(f"❌ Backward compatibility test error: {e}")

print("\n" + "=" * 60)
print("Frontend tests completed!")
print("Open http://localhost:8000 in browser to test UI")
print("=" * 60)
