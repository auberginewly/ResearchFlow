# ResearchFlow

ResearchFlow 是一个面向复杂主题调研的 Agentic Research Workbench。  
覆盖命题输入、任务拆解、检索、结构化笔记、报告生成、历史复用与 Markdown / PDF 导出，前后端分离、SSE 流式反馈。

## 项目亮点

- **多阶段 Agent 工作流**：Planner 拆解子任务，Executor 串联搜索与笔记，Reporter 产出最终报告，而非单轮问答。
- **SSE 实时可观测**：研究过程通过事件流推送到前端，执行状态、任务进度、日志与来源数量可同步查看。
- **多层缓存与历史复用**：`query / search / note / report` 分层缓存；相同或相近命题可复用历史研究结果，减少重复调用。
- **搜索可插拔与兜底**：Tavily、DuckDuckGo 等 provider 抽象，主源失败时可走 fallback，降低单点不可用风险。
- **报告双路径**：模板与规则优先，必要时再交给 LLM 润色，降低对单次模型输出的依赖。
- **导出与存储分离**：Markdown 与 PDF 导出目录可配置；PDF 由后端 ReportLab 生成，避免纯前端导出不稳定。
- **研究工作台 UI**：单页内模块切换（对话与过程、任务、来源、报告），侧栏历史与执行状态，适配长内容滚动。

## 解决的困难

| 问题 | 做法 |
|------|------|
| 长流程黑盒、用户不知道跑到哪一步 | 用 SSE 推送阶段化事件，前端按阶段展示日志与状态标签。 |
| 模型服务限流、偶发失败 | `llm_client` 内指数退避重试；对不兼容参数（如部分厂商不支持 temperature）做兼容处理。 |
| 仅依赖单一搜索源易失败或成本高 | 抽象 `search_providers`，配置主源 + `SEARCH_FALLBACK_PROVIDER` 兜底。 |
| 无 Key 或 Tavily 不可用时无法检索 | 支持 `SEARCH_PROVIDER=duckduckgo` 等零 Key 或低成本路径。 |
| 重复检索与重复生成浪费配额 | 多层文件缓存 + 历史命中复用，日志中可体现命中情况。 |
| 浏览器端 PDF 易空白、依赖打印对话框 | 改为后端生成 PDF，前端仅预览与触发下载。 |
| 报告里混有表格片段、长 URL、中英文混排 | PDF 侧做 Markdown 子集映射、表格识别收紧、链接与 CJK 换行优化，减少版式炸页。 |
| 工作台信息堆叠、单页溢出 | 收敛为侧栏 + 主区 + 模块切换，各区域独立滚动，减少重复状态展示。 |

## 技术栈

- Vue 3、TypeScript、Vite、Vue Router、Marked
- FastAPI、SSE、Pydantic / Pydantic Settings、Httpx、ReportLab

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
├── README.md
├── backend/
│   ├── pyproject.toml          # Python 依赖与项目元数据
│   ├── uv.lock                 # 锁定依赖版本（可选）
│   ├── .env.example            # 环境变量模板（复制为 .env）
│   └── src/
│       ├── main.py             # FastAPI 应用入口、CORS、路由挂载
│       ├── config.py           # pydantic-settings：LLM / 搜索 / 存储路径等
│       ├── models.py           # 请求体、研究状态、任务与事件模型
│       ├── prompts.py          # 各 Agent 使用的提示模板
│       ├── agent.py            # 研究主循环：编排 Planner → 执行 → Reporter
│       ├── api/
│       │   └── research.py     # POST /stream（SSE）、GET /history、导出 Markdown/PDF
│       ├── core/
│       │   ├── state.py        # 历史 JSON 存取、Markdown/PDF 导出、PDF 渲染
│       │   ├── cache.py        # 多层缓存目录与键策略
│       │   ├── events.py
│       │   └── registry.py
│       ├── services/
│       │   ├── planner.py      # 子任务规划
│       │   ├── executor.py     # 单任务执行调度
│       │   ├── llm_client.py   # 兼容多厂商的 HTTP 调用与重试
│       │   ├── search.py       # 搜索门面：provider 选择与结果汇总
│       │   ├── summarizer.py
│       │   ├── reporter.py     # 报告生成（模板优先 + 可选 LLM）
│       │   ├── search_components/
│       │   │   ├── query_rewriter.py    # 查询改写（可配置开关）
│       │   │   ├── query_templates.py   # 规则化查询模板
│       │   │   ├── result_ranker.py
│       │   │   └── source_deduplicator.py
│       │   └── search_providers/
│       │       ├── tavily.py
│       │       └── duckduckgo.py
│       └── tools/
│           ├── search_tool.py
│           ├── note_tool.py    # 结构化笔记
│           └── source_tool.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.ts             # 挂载 Vue、Router
        ├── router.ts           # 路由（工作台为主）
        ├── App.vue
        ├── api/research.ts     # SSE 解析、历史与详情 API、导出 URL
        ├── composables/useResearch.ts   # 研究状态与 SSE 订阅
        ├── types/research.ts
        ├── views/
        │   └── WorkbenchView.vue        # 侧栏 + 主面板 + 模块切换
        └── components/
            ├── ResearchForm.vue         # 命题输入
            ├── TaskList.vue
            ├── ReportViewer.vue         # Markdown 预览、导出入口
            ├── LogPanel.vue
            ├── ProgressBar.vue
            └── workbench/
                ├── HistoryPanel.vue
                └── SourceList.vue
```

运行时数据（默认在 `backend/workspace/`，已由 `.gitignore` 忽略）：

- `history/`：研究状态 JSON
- `cache/`：query / search / note / report 缓存
- `exports/`：Markdown 导出
- `exports/pdf/`：PDF 导出（可通过 `PDF_EXPORT_STORAGE_DIR` 单独配置）

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

常用配置项示例见 `backend/.env.example`（含 `LLM_*`、`SEARCH_*`、`HISTORY_STORAGE_DIR`、`EXPORT_STORAGE_DIR`、`PDF_EXPORT_STORAGE_DIR`、`CACHE_STORAGE_DIR`）。

说明：

- 若没有 Tavily Key，可将 `SEARCH_PROVIDER` 设为 `duckduckgo`
- 使用兼容 OpenAI 的接口时，修改 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`

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
3. 检索层执行搜索，必要时启用 fallback
4. 结果被整理为结构化研究笔记
5. Reporter 生成最终研究报告
6. 前端通过 SSE 实时展示进度、日志与中间状态
7. 研究结果写入历史存储，并支持 Markdown / PDF 导出

## 存储与导出

后端默认在 `backend/workspace/` 下维护数据：

- `history/`：研究历史记录
- `cache/`：查询、搜索、笔记、报告缓存
- `exports/`：Markdown 导出
- `exports/pdf/`：PDF 导出（或 `PDF_EXPORT_STORAGE_DIR` 指定路径）

