"""手动触发情报采集任务"""
import requests
import time

print("正在触发情报采集任务...")
try:
    response = requests.post("http://127.0.0.1:8000/api/v1/tasks/trigger")
    if response.status_code == 200:
        print("✓ 任务已触发")
        print(f"  响应: {response.json()}")
        print("\n任务正在后台执行，预计需要 2-5 分钟...")
        print("可以查看后端日志了解执行进度")
    else:
        print(f"✗ 触发失败: {response.status_code}")
        print(f"  {response.text}")
except Exception as e:
    print(f"✗ 请求失败: {e}")
    print("\n请确认后端服务已启动（http://127.0.0.1:8000）")