import requests
import json

print("触发采集任务...")
response = requests.post("http://127.0.0.1:8000/api/v1/tasks/trigger")
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

print("\n任务已在后台执行，查看后端日志了解进度")