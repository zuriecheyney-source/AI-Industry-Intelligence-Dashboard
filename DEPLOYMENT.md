# 部署验证指南

## 环境检查

在部署前，确认以下环境准备就绪：

### 必需软件

**Docker 部署**：
- Docker 20.10+
- Docker Compose 2.0+

**本地部署**：
- Python 3.10+
- Node.js 18+
- pip
- npm

检查版本：
```bash
docker --version
docker-compose --version
python --version
node --version
```

## 配置验证

### 1. 复制环境变量文件

```bash
cp backend/.env.example backend/.env
```

### 2. 必填配置项检查清单

打开 `backend/.env`，确保至少配置以下项：

- [ ] `AI_PROVIDER` - 选择一个 AI 提供商 (建议: deepseek)
- [ ] 对应 AI 提供商的 API Key
- [ ] `SERPER_API_KEY` 或其他搜索 API
- [ ] `WECHAT_WEBHOOK_URL` - 企业微信机器人地址

**最小配置示例**：
```env
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key-here
SERPER_API_KEY=your-serper-key
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

### 3. 行业配置验证

检查 `backend/config.json` 是否存在且格式正确：

```bash
# Windows PowerShell
Test-Path backend\config.json

# 查看内容
Get-Content backend\config.json
```

## 部署步骤

### Docker 部署

```bash
# 1. 构建并启动
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 等待服务启动（约 30-60 秒）

# 4. 检查容器状态
docker-compose ps
```

预期输出：
```
NAME       SERVICE    STATUS    PORTS
backend    backend    Up        0.0.0.0:8000->8000/tcp
frontend   frontend   Up        0.0.0.0:3000->3000/tcp
```

### 本地部署

**后端**：

1. 创建并激活虚拟环境：

```bash
# Windows
cd backend
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
cd backend
python3 -m venv venv
source venv/bin/activate
```

2. 安装依赖并启动：

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**前端**（新终端）：
```bash
cd frontend
npm install
npm run dev
```

## 功能验证

### 1. 健康检查

**后端 API**：
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "ai_provider": "deepseek",
  "timezone": "Asia/Shanghai"
}
```

**前端页面**：
访问 http://localhost:3000，应该看到"AI行业情报系统"标题。

### 2. API 文档访问

访问 http://localhost:8000/docs，应该看到 Swagger API 文档界面。

### 3. 企业微信推送测试

**方法一：通过 Web 界面**
1. 访问 http://localhost:3000/config
2. 点击"测试企业微信推送"按钮
3. 检查企业微信群聊是否收到测试消息

**方法二：通过 API**
```bash
curl -X POST http://localhost:8000/api/v1/wechat/test
```

预期：企业微信群收到类似消息：
```
【测试消息】
AI行业情报系统运行正常
时间：2026-07-01 14:30:00
配置的AI提供商：deepseek
此消息用于测试企业微信推送功能。
```

### 4. 手动触发采集任务

**方法一：通过 Web 界面**
1. 访问 http://localhost:3000/config
2. 点击"手动触发采集"按钮
3. 等待 1-3 分钟
4. 检查后端日志或企业微信群聊

**方法二：通过 API**
```bash
curl -X POST http://localhost:8000/api/v1/tasks/trigger
```

### 5. 验证数据存储

检查 Excel 文件是否生成：

```bash
# Windows PowerShell
Get-ChildItem backend\data\*.xlsx

# 查看文件大小
Get-ChildItem backend\data\*.xlsx | Select-Object Name, Length, LastWriteTime
```

### 6. 查看定时任务状态

```bash
curl http://localhost:8000/api/v1/tasks/status
```

预期响应：
```json
{
  "running": true,
  "timezone": "Asia/Shanghai",
  "jobs": [
    {
      "id": "daily_collection_09:00",
      "name": "每日情报采集 09:00",
      "next_run_time": "2026-07-02T09:00:00+08:00"
    }
  ]
}
```

## 常见问题排查

### 问题 1：容器启动失败

```bash
# 查看详细日志
docker-compose logs backend

# 常见原因：
# - 端口被占用：修改 docker-compose.yml 中的端口映射
# - 环境变量未配置：检查 .env 文件
# - 镜像构建失败：docker-compose build --no-cache
```

### 问题 2：前端无法连接后端

检查 API 代理配置：
1. 确认后端在 http://localhost:8000 运行
2. 检查 `frontend/next.config.js` 的 rewrites 配置
3. 清除 Next.js 缓存：`rm -rf frontend/.next`

### 问题 3：企业微信推送失败

```bash
# 检查 Webhook 是否正确
curl -X POST "你的WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"测试"}}'

# 常见原因：
# - Webhook 地址错误或过期
# - 机器人被移除或禁用
# - 消息格式不符合企业微信要求
```

### 问题 4：搜索 API 返回空结果

```bash
# 检查后端日志
docker-compose logs backend | grep -i "search"

# 常见原因：
# - API Key 无效或额度用完
# - 搜索关键词太宽泛或太具体
# - 网络连接问题
```

### 问题 5：AI 分析失败

检查 AI 提供商配置：
```bash
# 测试 DeepSeek 连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"

# 常见原因：
# - API Key 错误
# - 账户余额不足
# - 模型不可用或名称错误
```

## 性能优化

### 1. 调整采集频率

编辑 `backend/.env`：
```env
# 减少采集频率（节省成本）
SCHEDULE_TIMES=09:00

# 增加采集频率（更及时）
SCHEDULE_TIMES=06:00,09:00,12:00,18:00,21:00
```

### 2. 限制搜索结果数量

编辑 `backend/config.json`：
```json
{
  "search_config": {
    "max_results_per_keyword": 3,
    "date_range_days": 1
  }
}
```

### 3. Docker 资源限制

编辑 `docker-compose.yml` 添加资源限制：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## 监控建议

### 1. 定期检查日志

```bash
# 查看最近 100 行日志
docker-compose logs --tail=100 backend

# 持续监控
docker-compose logs -f backend
```

### 2. 监控数据增长

```bash
# 检查 Excel 文件大小
du -sh backend/data/

# 定期备份
cp -r backend/data/ backup/data-$(date +%Y%m%d)/
```

### 3. API 健康检查

设置定时任务（cron/计划任务）定期检查：
```bash
# Linux cron
*/5 * * * * curl -f http://localhost:8000/health || echo "Backend down!"
```

## 生产环境建议

1. **使用 HTTPS**：配置 Nginx 反向代理 + Let's Encrypt
2. **环境隔离**：为生产环境创建独立的 `.env.production`
3. **日志轮转**：配置 Docker 日志轮转防止磁盘占满
4. **定期备份**：自动备份 `backend/data/` 目录
5. **监控告警**：集成 Prometheus + Grafana 或云监控服务
6. **密钥管理**：使用密钥管理服务（如 AWS Secrets Manager）

## 验证成功标准

系统正常运行时应满足：

- [ ] 后端 `/health` 端点返回 200
- [ ] 前端页面正常加载
- [ ] 企业微信测试消息发送成功
- [ ] 手动触发任务能执行完成
- [ ] Excel 文件正常生成
- [ ] 定时任务显示为 running
- [ ] 后端日志无严重错误
- [ ] 前端可以查询和展示情报数据

如果以上都满足，说明系统部署成功！