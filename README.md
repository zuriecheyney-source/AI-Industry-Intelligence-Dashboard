# AI 行业情报系统

自动化采集和推送行业情报的智能系统，利用 AI 和 Web 搜索能力定期发送每日情报到飞书，数据存入 Excel，并提供 Web 看板展示。

## 功能特性

- 🤖 **AI 驱动分析**：支持 DeepSeek API 和 Ollama 本地部署
- 🔍 **智能搜索**：集成 Serper 搜索 API
- 📊 **数据可视化**：实时看板展示情报趋势和分布
- 💬 **飞书推送**：每日定时推送情报摘要
- 📁 **Excel 归档**：自动保存到 Excel 文件便于查阅
- ⚙️ **灵活配置**：可视化管理行业关键词和推送设置

## 系统架构

```
定时调度器 → AI采集引擎 → 数据处理 → 双通道输出
                 ↓              ↓          ↓
            Web Search API   AI总结    Excel + DB
                                          ↓
                                    飞书 + 看板
```

## 技术栈

**后端**：Python 3.10+ / FastAPI / APScheduler / OpenPyXL

**前端**：Next.js 14 / React 18 / Tailwind CSS / Recharts

## 快速开始

### 方法一：Docker 部署（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填写 API 密钥

# 2. 启动服务
docker-compose up -d

# 3. 访问系统
# 前端看板：http://localhost:3000
# 后端 API：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 方法二：本地开发

**后端**：
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端**：
```bash
cd frontend
npm install
npm run dev
```

## 配置说明

### 环境变量

编辑 `backend/.env` 文件：

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `AI_PROVIDER` | AI 提供商（deepseek / ollama） | 是 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 二选一 |
| `OLLAMA_BASE_URL` | Ollama 本地服务地址 | 二选一 |
| `SERPER_API_KEY` | Serper 搜索 API 密钥 | 是 |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook 地址 | 是 |
| `SCHEDULE_TIMES` | 定时任务时间（如 09:00,18:00） | 否 |

### 行业配置

编辑 `backend/config.json` 或通过 Web 界面管理：

```json
{
  "industries": [
    {
      "name": "AI板块",
      "keywords": ["人工智能", "大模型", "ChatGPT"],
      "enabled": true
    }
  ]
}
```

## 使用说明

### 情报看板

访问首页可以看到情报卡片列表、筛选器、统计图表。

### 配置管理

访问 `/config` 页面可以管理行业配置、查看系统状态、手动触发采集、测试飞书推送。

### 定时任务

系统默认在每天 09:00 和 18:00 自动执行情报采集：

1. 根据行业关键词搜索最新信息
2. 使用 AI 分析和总结情报
3. 保存到 Excel 文件
4. 推送到飞书群聊

### 数据存储

所有情报保存在 `backend/data/` 目录：
- Excel 文件：`intelligence_YYYY-MM.xlsx`
- SQLite 数据库：`intelligence.db`

## API 接口

- `GET /api/intelligence` - 查询情报列表
- `GET /api/intelligence/statistics` - 获取统计信息
- `GET /api/industries` - 获取行业配置
- `POST /api/tasks/trigger` - 手动触发采集
- `POST /api/notification/test` - 测试飞书推送

完整 API 文档：http://localhost:8000/docs

## 常见问题

### 如何获取飞书 Webhook？

1. 在飞书群聊中添加"群机器人"
2. 复制 Webhook 地址到 `.env` 文件的 `FEISHU_WEBHOOK_URL`

### 定时任务不执行？

1. 检查后端日志
2. 确认 `SCHEDULE_TIMES` 配置正确
3. 验证时区设置 `TIMEZONE=Asia/Shanghai`

### 支持哪些 AI 模型？

- **DeepSeek**：推荐，国内访问稳定，性价比高
- **Ollama**：本地部署，数据隐私性好，需要本地算力

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── scheduler/     # 定时任务
│   │   ├── services/      # 业务服务
│   │   └── main.py        # 应用入口
│   ├── data/              # 数据存储
│   └── config.json        # 行业配置
│
├── frontend/
│   ├── app/               # 页面路由
│   ├── components/        # React 组件
│   └── lib/               # 工具函数
│
└── docker-compose.yml
```

## 许可证

MIT License
