# ResearchFlow

ResearchFlow 是一个面向复杂主题调研的 Agentic Research Workbench。  
它不是单轮问答 Demo，而是一个覆盖命题输入、任务拆解、检索、结构化笔记、报告生成、历史复用与导出的完整研究流程系统。

## 项目亮点

- 多阶段研究工作流：围绕研究主题自动拆解子任务，串联检索、笔记整理、报告生成。
- SSE 实时反馈：前端可以实时看到执行状态、任务进度、日志阶段和来源数量，而不是等待单次返回。
- 多层缓存与历史复用：支持 `query / search / note / report` 多层缓存，并能复用历史研究结果。
- 搜索解耦与兜底策略：搜索 provider 支持抽象与 fallback，降低单一搜索源不可用时的失败风险。
- 模板优先报告生成：报告生成支持规则和模板优先的稳定路径，减少对单次 LLM 输出质量的强依赖。
- Markdown / PDF 导出：支持 Markdown 导出与后端生成 PDF，避免浏览器端导出空白等不稳定问题。
- 工作台式前端：采用单页研究工作台布局，支持任务、来源、过程、报告和历史记录切换查看。

## 技术栈

- Vue 3
- TypeScript
- Vite
- Vue Router
- Marked
- FastAPI
- SSE
- Pydantic / Pydantic Settings
- Httpx
- ReportLab

## 当前能力

- 输入研究命题并发起研究流程
- 自动规划多个研究子任务
- 基于搜索结果生成结构化研究笔记
- 输出研究报告并支持 Markdown 预览
- 实时展示执行状态、任务过程、日志与来源
- 保存研究历史并支持历史详情加载
- 支持 Markdown 导出与后端 PDF 导出

## 项目结构

```text
ResearchFlow/
├── backend/   FastAPI research service, SSE, history/cache/export
├── frontend/  Vue 3 workbench UI
└── README.md
```

## 快速开始

### 1. 启动后端

推荐使用 `uv`：

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

后端默认地址：`http://127.0.0.1:8000`

### 2. 配置后端环境变量

后端会从 `backend/.env` 读取配置。可以基于 `backend/.env.example` 创建本地配置文件：

```bash
cd backend
cp .env.example .env
```

常用配置项如下：

```env
LLM_API_KEY=your-llm-api-key
LLM_BASE_URL=https://api.example.com/v1
LLM_MODEL=your-model-name

SEARCH_PROVIDER=tavily
SEARCH_FALLBACK_PROVIDER=duckduckgo
SEARCH_API_KEY=your-search-api-key

LLM_ENABLE_QUERY_REWRITE=true
LLM_ENABLE_REPORT_POLISH=false
```

说明：

- 如果你没有 Tavily Key，可以把 `SEARCH_PROVIDER` 改成 `duckduckgo`
- 如果使用兼容 OpenAI 的模型服务，修改 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` 即可

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：`http://localhost:5173`

## 核心流程

1. 用户输入研究主题
2. 后端生成研究计划与子任务
3. 检索层执行搜索，并根据配置启用 fallback
4. 结果被整理为结构化研究笔记
5. Reporter 生成最终研究报告
6. 前端通过 SSE 实时展示进度、日志和中间状态
7. 研究结果写入历史存储，并支持导出

## 存储与导出

后端默认会在 `backend/workspace/` 下维护运行数据：

- `history/`：研究历史记录
- `cache/`：查询、搜索、笔记、报告缓存
- `exports/`：Markdown / PDF 导出文件

