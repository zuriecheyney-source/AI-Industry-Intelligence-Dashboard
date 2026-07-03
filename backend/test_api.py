#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速测试 API 返回"""
import requests
import json

print("=== 测试后端 API ===")
try:
    r = requests.get("http://localhost:8000/api/intelligence", params={"page": 1, "page_size": 2}, timeout=5)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"总数: {data.get('total', 0)}")
        print(f"当前页: {data.get('page', 0)}")
        print(f"返回条数: {len(data.get('items', []))}")
        
        if data.get('items'):
            first = data['items'][0]
            print(f"\n第一条数据:")
            print(f"  标题: {first.get('title', 'N/A')[:50]}")
            print(f"  行业: {first.get('industry', 'N/A')}")
            print(f"  日期: {first.get('date', 'N/A')}")
    else:
        print(f"错误: {r.text}")
        
except Exception as e:
    print(f"请求失败: {e}")

print("\n=== 测试前端代理 ===")
try:
    r = requests.get("http://localhost:3000/api/intelligence", params={"page": 1, "page_size": 2}, timeout=5)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"总数: {data.get('total', 0)}")
        print(f"返回条数: {len(data.get('items', []))}")
    else:
        print(f"错误响应码: {r.status_code}")
        print(f"内容: {r.text[:200]}")
        
except Exception as e:
    print(f"请求失败: {e}")