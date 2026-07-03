#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import sys

print("=== API 状态检查 ===\n")

# 测试后端
try:
    r = requests.get("http://localhost:8000/api/industries", timeout=2)
    print(f"[后端 /api/industries]")
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  返回: {len(data)} 个行业配置")
        print(f"  ✓ 后端 API 正常\n")
    else:
        print(f"  返回内容: {r.text[:100]}\n")
except Exception as e:
    print(f"  ✗ 后端连接失败: {e}\n")
    sys.exit(1)

# 测试前端代理
try:
    r = requests.get("http://localhost:3000/api/industries", timeout=2)
    print(f"[前端代理 /api/industries]")
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  返回: {len(data)} 个行业配置")
        print(f"  ✓ 前端代理正常\n")
    else:
        print(f"  返回内容: {r.text[:100]}\n")
except Exception as e:
    print(f"  ✗ 前端代理失败: {e}\n")
    sys.exit(1)

# 测试情报数据
try:
    r = requests.get("http://localhost:3000/api/intelligence", params={"page": 1, "page_size": 1}, timeout=2)
    print(f"[情报数据 /api/intelligence]")
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  总数: {data.get('total', 0)}")
        print(f"  返回条数: {len(data.get('items', []))}")
        print(f"  ✓ 情报 API 正常\n")
    else:
        print(f"  返回内容: {r.text[:100]}\n")
except Exception as e:
    print(f"  ✗ 情报 API 失败: {e}\n")

print("=== 检查完成 ===")
print("\n下一步:")
print("1. 如果所有检查都通过,在浏览器中按 Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac) 硬刷新")
print("2. 如果仍然 404,在浏览器控制台执行: localStorage.clear(); location.reload(true)")