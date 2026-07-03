"""简单触发脚本"""
import requests

url = "http://127.0.0.1:8000/api/v1/tasks/trigger"
print("触发任务...")
try:
    r = requests.post(url, timeout=5)
    print(f"状态: {r.status_code}")
    if r.status_code == 200:
        print("任务已触发，正在后台执行")
        print("预计 2-5 分钟完成，可查看后端日志了解进度")
    else:
        print(f"响应: {r.text}")
except requests.Timeout:
    print("请求超时，但任务可能已在后台启动")
    print("检查后端日志确认执行状态")
except Exception as e:
    print(f"错误: {e}")