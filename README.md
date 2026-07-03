# AI行业情报系统

自动化采集和推送行业情报的智能系统，利用 AI 和 Web 搜索能力定期发送每日情报到企业微信，数据存入 Excel，并提供 Web 看板展示。

## 功能特性

- 🤖 **AI 驱动分析**：专门深度集成 DeepSeek 与 Ollama (本地部署) AI大模型
- 🔍 **智能搜索**：集成 Serper、Google、Bing 等搜索 API
- 📊 **数据可视化**：实时看板展示情报趋势和分布
- 💬 **企业微信推送**：每日定时推送情报摘要
- 📁 **Excel 归档**：自动保存到 Excel 文件便于查阅
- ⚙️ **灵活配置**：可视化管理行业关键词和推送设置

## 系统架构

```
定时调度器 → AI采集引擎 → 数据处理 → 双通道输出
                 ↓              ↓          ↓
            Web Search API   AI总结    Excel + DB
                                          ↓
                                    企业微信 + 看板
```

## 技术栈

**后端**：
- Python 3.10+
- FastAPI
- APScheduler（定时任务）
- OpenPyXL（Excel 处理）

**前端**：
- Next.js 14
- React 18
- Tailwind CSS
- Recharts（图表）

## 快速开始

### 方法一：Docker 部署（推荐）

1. **克隆项目**

```bash
git clone <repository-url>
cd "AI Industry Intelligence Dashboard"
```

2. **配置环境变量**

复制后端环境变量模板并填写配置：

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，至少配置以下必填项：

```env
# AI模型配置（至少配置一个）
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx

# 搜索API配置（至少配置一个）
SERPER_API_KEY=xxx

# 企业微信Webhook（必填）
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

3. **启动服务**

```bash
docker-compose up -d
```

4. **访问系统**

- 前端看板：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 方法二：本地开发部署

#### 后端部署

1. **创建 Python 虚拟环境**

```bash
cd backend

# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

2. **安装 Python 依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件填写配置
```

4. **启动后端服务**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端部署

1. **安装 Node.js 依赖**

```bash
cd frontend
npm install
```

2. **启动开发服务器**

```bash
npm run dev
```

访问 http://localhost:3000

3. **生产环境构建**

```bash
npm run build
npm start
```

## 配置说明

### 环境变量配置

查看 `backend/.env.example` 获取完整配置说明。

**核心配置项**：

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `AI_PROVIDER` | AI 提供商（deepseek/ollama） | 是 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 二选一 |
| `SERPER_API_KEY` | Serper 搜索 API 密钥 | 二选一 |
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook 地址 | 是 |
| `SCHEDULE_TIMES` | 定时任务时间（格式：09:00,18:00） | 否 |
| `TIMEZONE` | 时区（默认：Asia/Shanghai） | 否 |

### 行业配置

编辑 `backend/config.json` 配置监控的行业和关键词：

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

也可以通过 Web 界面的配置页面管理行业配置。

## 使用说明

### 查看情报看板

访问首页可以看到：
- 情报卡片列表（按日期、行业展示）
- 筛选器（支持行业、关键词搜索）
- 统计图表（行业分布、月度趋势）

### 配置管理

访问 `/config` 页面可以：
- 添加/编辑/删除行业配置
- 查看系统状态（AI 提供商、定时任务）
- 手动触发情报采集
- 测试企业微信推送

### 定时任务

系统默认在每天 09:00 和 18:00 自动执行情报采集任务，流程如下：

1. 根据配置的行业关键词搜索最新信息
2. 使用 AI 分析和总结情报
3. 保存到 Excel 文件
4. 推送到企业微信群聊

### 数据查看

所有情报数据保存在 `backend/data/` 目录：

- Excel 文件：`intelligence_YYYY-MM.xlsx`（按月份）
- 每个文件包含：日期、行业、标题、摘要、来源、分类、重要度、关键词、URL

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整 API 文档。

**主要接口**：

- `GET /api/v1/intelligence` - 查询情报列表
- `GET /api/v1/intelligence/statistics` - 获取统计信息
- `GET /api/v1/industries` - 获取行业配置
- `POST /api/v1/tasks/trigger` - 手动触发采集任务
- `POST /api/v1/wechat/test` - 测试企业微信推送

## 成本估算

**月度成本**（以每天采集 30 条情报为例）：

- **AI API**：
  - GPT-4：约 $1.8/月
  - Claude：约 $2/月
  - 通义千问：约 ¥40/月（推荐）
  
- **搜索API**：
  - Serper：免费额度 2500 次/月（足够使用）
  
- **服务器**：
  - 2核4G 云服务器：约 ¥100/月

**总计**：约 ¥120-150/月（使用国内模型可降至 ¥50-80/月）

## 常见问题

### 1. 如何获取企业微信 Webhook？

1. 在企业微信群聊中添加"群机器人"
2. 配置机器人名称和权限
3. 复制生成的 Webhook 地址到 `.env` 文件

### 2. 支持哪些搜索 API？

- **Serper API**（推荐）：免费额度 2500 次/月
- **Google Custom Search API**：免费额度 100 次/天
- **Bing Search API**：需付费

### 3. 如何切换 AI 模型？

修改 `.env` 文件中的 `AI_PROVIDER` 配置：

```env
# 可选值：deepseek, ollama
AI_PROVIDER=qwen
QWEN_API_KEY=your-api-key
```

### 4. 定时任务不执行怎么办？

1. 检查后端日志：`docker-compose logs backend`
2. 确认 `SCHEDULE_TIMES` 配置正确
3. 验证时区设置：`TIMEZONE=Asia/Shanghai`
4. 手动触发测试：访问配置页面点击"手动触发采集"

### 5. Excel 文件在哪里？

保存在 `backend/data/` 目录，文件名格式为 `intelligence_YYYY-MM.xlsx`。

Docker 部署时会自动挂载到主机的 `./backend/data` 目录。

## 扩展功能

系统支持以下扩展方向：

1. **多维度分析**：情感分析、热度趋势预测
2. **智能提醒**：基于用户画像推送个性化情报
3. **协作功能**：情报标注、评论、分享
4. **移动端**：开发小程序或 H5 版本
5. **多渠道推送**：支持钉钉、Slack 等平台

## 开发说明

### 项目结构

```
├── backend/                 # Python 后端
│   ├── app/
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务服务
│   │   ├── scheduler/      # 定时任务
│   │   ├── api/            # API 路由
│   │   └── main.py         # 应用入口
│   ├── data/               # 数据存储
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/               # Next.js 前端
│   ├── app/               # 页面路由
│   ├── components/        # React 组件
│   ├── lib/              # 工具函数
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml     # Docker 编排
└── README.md             # 项目文档
```

### 添加新的 AI 模型

1. 在 `backend/app/core/ai_client.py` 添加客户端类
2. 在 `AIClientFactory` 注册新模型
3. 更新 `.env.example` 添加配置项

### 添加新的搜索源

1. 在 `backend/app/services/search_service.py` 添加服务类
2. 继承 `SearchServiceBase` 基类
3. 在 `IntelligenceSearchService` 中集成

## 许可证

MIT License

## 支持

如有问题或建议，请提交 Issue 或 Pull Request。