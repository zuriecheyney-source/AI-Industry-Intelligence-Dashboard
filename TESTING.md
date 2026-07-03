# 系统测试指南

## 快速验证

### 1. 后端服务测试

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 启动服务
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**验证接口：**

- 健康检查：http://127.0.0.1:8000/health
- API文档：http://127.0.0.1:8000/docs
- 行业配置：http://127.0.0.1:8000/api/v1/industries
- AI配置：http://127.0.0.1:8000/api/v1/config/ai-provider

### 2. 前端服务测试

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

访问：http://localhost:3000

### 3. 核心功能测试

#### 手动触发情报采集

```bash
# 使用 curl 或浏览器访问
curl -X POST http://127.0.0.1:8000/api/v1/tasks/trigger
```

**观察点：**
- 后端日志显示采集流程
- 搜索关键词并调用 Serper API
- AI 分析情报并分类
- 保存到 Excel（backend/data/目录）
- 推送到飞书群聊

#### 查看情报列表

访问前端看板：http://localhost:3000

**验证功能：**
- 情报卡片展示
- 按行业/日期/重要度筛选
- 搜索功能
- 趋势图表
- 配置管理页面

### 4. 飞书推送测试

```bash
# 测试飞书 Webhook 连通性
curl -X POST http://127.0.0.1:8000/api/v1/notification/test
```

检查飞书群聊是否收到测试消息。

## 配置检查清单

- [ ] `.env` 文件已配置所有必需的 API 密钥
  - AI Provider API Key（DeepSeek等）
  - Serper API Key（搜索）
  - 飞书 Webhook URL
- [ ] `config.json` 已配置行业和关键词
- [ ] 数据目录 `backend/data/` 可写
- [ ] 前端环境变量 `NEXT_PUBLIC_API_URL` 已配置

## 定时任务验证

定时任务在后端启动时自动配置（每日 9:00 和 18:00）。

**查看任务状态：**
```bash
curl http://127.0.0.1:8000/api/v1/tasks/status
```

## 常见问题

### 后端启动失败

**问题：** pydantic 验证错误
**解决：** 检查 `.env` 文件中是否有未定义但在 `config.py` 中必需的字段

**问题：** 依赖安装失败
**解决：** 确保使用 Python 3.10+，某些包可能需要编译环境

### 前端无法连接后端

**解决：** 
1. 确认后端服务已启动（端口 8000）
2. 检查前端 `.env.local` 中的 API URL 配置
3. 检查 CORS 配置（后端默认允许所有来源）

### 情报采集失败

**可能原因：**
1. Serper API Key 无效或超额
2. AI API Key 无效或超额
3. 网络连接问题
4. 关键词配置为空

**排查：** 查看后端日志，会显示详细错误信息

### 飞书推送失败

**排查：**
1. 检查 Webhook URL 是否正确
2. 检查机器人是否已添加到群聊
3. 检查消息格式是否符合飞书要求

## 性能优化建议

1. **搜索并发：** 配置文件中可调整 `max_results_per_keyword`
2. **AI 模型选择：** 使用国内模型（通义千问）可降低成本和延迟
3. **数据库：** 如需高性能查询，启用 SQLite 数据库
4. **缓存：** 搜索结果可增加缓存层，避免重复搜索

## Docker 部署测试

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问：
- 后端：http://localhost:8000
- 前端：http://localhost:3000

## 测试数据示例

系统首次运行后会在 `backend/data/` 目录生成 Excel 文件：

```
backend/data/
└── intelligence_2026-03.xlsx  # 当月情报汇总
```

Excel 包含列：日期、行业、标题、摘要、来源、分类、重要度、关键词、URL