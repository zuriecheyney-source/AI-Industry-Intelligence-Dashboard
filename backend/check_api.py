#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

def test_backend():
    try:
        r = requests.get("http://localhost:8000/api/intelligence", params={"page": 1, "page_size": 1}, timeout=3)
        if r.status_code == 200:
            data = r.json()
            print(f"[OK] Backend API: total={data['total']}, items={len(data['items'])}")
            if data['items']:
                item = data['items'][0]
                print(f"  Example: {item['title'][:40]}... | {item['industry']} | {item['date']}")
            return True
        else:
            print(f"[FAIL] Backend error: {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Backend request failed: {e}")
        return False

def test_frontend():
    try:
        r = requests.get("http://localhost:3000/api/intelligence", params={"page": 1, "page_size": 1}, timeout=3)
        if r.status_code == 200:
            data = r.json()
            print(f"[OK] Frontend proxy: total={data['total']}, items={len(data['items'])}")
            return True
        else:
            print(f"[FAIL] Frontend proxy error: {r.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Frontend proxy failed: {e}")
        return False

if __name__ == "__main__":
    print("=== API Status Check ===")
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print("\n[SUCCESS] All services OK. Refresh http://localhost:3000 to see data.")
    elif backend_ok and not frontend_ok:
        print("\n[WARNING] Backend OK but frontend proxy has issues.")
    else:
        print("\n[ERROR] Need to check backend service.")