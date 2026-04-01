<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ReportViewer from "../components/ReportViewer.vue";
import ResearchForm from "../components/ResearchForm.vue";
import TaskList from "../components/TaskList.vue";
import { useResearch } from "../composables/useResearch";

const { state, startResearch, refreshHistory, loadHistoryItem } = useResearch();
const activeModule = ref<"conversation" | "tasks" | "sources" | "report">("conversation");

const activeTask = computed(() => {
  return state.tasks.find((task) => task.status === "running") ?? null;
});

const completedCount = computed(() => {
  return state.tasks.filter((task) => task.status === "completed").length;
});

const latestLogs = computed(() =>
  state.logs.slice(-12).map((log) => ({
    text: log,
    stage: resolveStage(log),
  })),
);

const allSources = computed(() => {
  return state.tasks.flatMap((task) =>
    (task.sources || []).map((source) => ({
      ...source,
      taskTitle: task.title,
    })),
  );
});

const currentStatusText = computed(() => {
  if (activeTask.value) return `当前执行：${activeTask.value.title}`;
  if (state.isRunning) return "正在准备研究流程...";
  if (state.topic) return "研究已停止，查看结果或重新发起新命题。";
  return "等待新的研究命题";
});

const liveTags = computed(() => {
  const tags = [
    { label: state.isRunning ? "运行中" : "空闲", tone: state.isRunning ? "active" : "muted" },
    { label: `${state.progress}%`, tone: "neutral" },
  ];

  if (activeTask.value) {
    tags.push({ label: "Thinking", tone: "thinking" });
  }

  if (allSources.value.length > 0) {
    tags.push({ label: `Sources ${allSources.value.length}`, tone: "neutral" });
  }

  if (state.report) {
    tags.push({ label: "Report ready", tone: "done" });
  }

  return tags;
});

function resolveStage(log: string): string {
  const value = log.toLowerCase();
  if (value.includes("规划") || value.includes("planner") || value.includes("task")) return "规划";
  if (value.includes("query") || value.includes("rewrite")) return "改写";
  if (value.includes("search") || value.includes("搜索") || value.includes("检索")) return "搜索";
  if (value.includes("note") || value.includes("笔记")) return "笔记";
  if (value.includes("report") || value.includes("报告")) return "报告";
  if (value.includes("cache")) return "缓存";
  if (value.includes("error") || value.includes("失败")) return "异常";
  return "进度";
}

const startAndFocus = async (topic: string) => {
  activeModule.value = "conversation";
  await startResearch(topic);
};

onMounted(() => {
  void refreshHistory();
  const pendingTopic = sessionStorage.getItem("researchflow.pendingTopic");
  if (pendingTopic) {
    sessionStorage.removeItem("researchflow.pendingTopic");
    void startAndFocus(pendingTopic);
  }
});
</script>

<template>
  <main class="workspace">
    <aside class="sidebar">
      <div class="brand">
        <p class="eyebrow">ResearchFlow</p>
        <h1>研究工作台</h1>
      </div>

      <nav class="module-nav">
        <button
          type="button"
          :class="{ active: activeModule === 'conversation' }"
          @click="activeModule = 'conversation'"
        >
          对话 / 过程
        </button>
        <button
          type="button"
          :class="{ active: activeModule === 'tasks' }"
          @click="activeModule = 'tasks'"
        >
          任务
        </button>
        <button
          type="button"
          :class="{ active: activeModule === 'sources' }"
          @click="activeModule = 'sources'"
        >
          来源
        </button>
        <button
          type="button"
          :class="{ active: activeModule === 'report' }"
          @click="activeModule = 'report'"
        >
          报告
        </button>
      </nav>

      <section class="sidebar-section status-section">
        <div class="section-title">
          <span>执行状态</span>
          <small>{{ activeTask ? "ACTIVE" : "WAITING" }}</small>
        </div>
        <p class="sidebar-status">{{ currentStatusText }}</p>
        <div class="metric-grid sidebar-metrics">
          <article>
            <strong>{{ state.progress }}%</strong>
            <span>总体进度</span>
          </article>
          <article>
            <strong>{{ completedCount }}</strong>
            <span>已完成</span>
          </article>
          <article>
            <strong>{{ state.tasks.length }}</strong>
            <span>任务总数</span>
          </article>
          <article>
            <strong>{{ allSources.length }}</strong>
            <span>来源数</span>
          </article>
        </div>
        <div v-if="activeTask?.trace" class="trace-stack sidebar-trace">
          <span>provider: {{ activeTask.trace.provider || "-" }}</span>
          <span>fallback: {{ activeTask.trace.used_fallback ? "是" : "否" }}</span>
          <span>results: {{ activeTask.trace.result_count }}</span>
        </div>
      </section>

      <section class="sidebar-section history-section">
        <div class="section-title">
          <span>研究历史</span>
          <button type="button" class="ghost-action" @click="refreshHistory">刷新</button>
        </div>
        <ul v-if="state.history.length" class="history-list">
          <li v-for="item in state.history" :key="item.id">
            <button
              type="button"
              class="history-item"
              :class="{ active: state.researchId === item.id }"
              @click="loadHistoryItem(item.id)"
            >
              <strong>{{ item.topic }}</strong>
              <small>{{ item.status }} · {{ new Date(item.updated_at).toLocaleDateString() }}</small>
            </button>
          </li>
        </ul>
        <p v-else class="empty-hint">暂无历史记录</p>
      </section>
    </aside>

    <section class="main-panel">
      <header class="topbar">
        <div>
          <p class="eyebrow">Workbench / {{ activeModule }}</p>
          <h2>{{ state.topic || "定义命题后开始研究" }}</h2>
        </div>
        <div class="topbar-meta">
          <span class="hero-status">{{ state.isRunning ? "Research in progress" : "Ready" }}</span>
          <span class="topbar-count">{{ completedCount }}/{{ state.tasks.length || 0 }} tasks</span>
        </div>
      </header>

      <ResearchForm
        :is-running="state.isRunning"
        :current-topic="state.topic"
        @submit="startAndFocus"
      />

      <div class="live-strip">
        <span
          v-for="item in liveTags"
          :key="`${item.label}-${item.tone}`"
          class="live-chip"
          :class="item.tone"
        >
          {{ item.label }}
        </span>
      </div>

      <section v-if="activeModule === 'conversation'" class="conversation-shell">
        <article class="message user">
          <span class="role">命题</span>
          <div class="bubble">
            {{ state.topic || "从左上输入你的研究命题，例如某个协议差异、产品变更或事件调查。" }}
          </div>
        </article>

        <article
          v-for="(log, index) in latestLogs"
          :key="`${log.text}-${index}`"
          class="message assistant"
        >
          <span class="role">
            <em class="stage-chip">{{ log.stage }}</em>
            <span>AI Thinking</span>
          </span>
          <div class="bubble">{{ log.text }}</div>
        </article>
      </section>

      <section v-else-if="activeModule === 'tasks'" class="content-shell">
        <TaskList :tasks="state.tasks" />
      </section>

      <section v-else-if="activeModule === 'sources'" class="content-shell sources-shell">
        <header class="content-header">
          <h3>来源列表</h3>
          <span>{{ allSources.length }} 条</span>
        </header>
        <ul v-if="allSources.length" class="source-list">
          <li v-for="source in allSources" :key="`${source.url}-${source.taskTitle}`">
            <a :href="source.url" target="_blank" rel="noreferrer">{{ source.title }}</a>
            <small>{{ source.taskTitle }} · {{ source.provider || "unknown" }}</small>
            <p v-if="source.snippet">{{ source.snippet }}</p>
          </li>
        </ul>
        <p v-else class="empty-hint">暂无来源，研究开始后会在这里显示检索到的内容。</p>
      </section>

      <section v-else class="content-shell">
        <ReportViewer
          :report="state.report"
          :export-path="state.exportPath"
          :reused="state.reused"
          :topic="state.topic"
        />
      </section>
    </section>
  </main>
  
  
  
  
  
</template>

<style scoped>
.workspace {
  height: 100vh;
  display: grid;
  grid-template-columns: clamp(280px, 28vw, 340px) minmax(0, 1fr);
  gap: 0;
  overflow: hidden;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--rf-subtle);
  font-family: "Fira Code", monospace;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-family: "Crimson Pro", serif;
  font-size: 38px;
  letter-spacing: -0.03em;
  line-height: 1;
}

.sidebar {
  background: #18181b;
  color: #fafafa;
  padding: 22px 18px 18px;
  display: grid;
  align-content: start;
  gap: 14px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 0;
  overflow: hidden;
}

.brand {
  display: grid;
  gap: 4px;
}

.module-nav button,
.history-item,
.ghost-action,
.quick-links button {
  cursor: pointer;
}

.module-nav {
  display: grid;
  gap: 8px;
}

.module-nav button,
.history-item {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: #e4e4e7;
  padding: 11px 12px;
  font: inherit;
  font-size: 15px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.module-nav button.active {
  background: rgba(236, 72, 153, 0.16);
  border-color: rgba(236, 72, 153, 0.4);
  color: #fff;
}

.module-nav button:hover,
.history-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.history-item.active {
  background: rgba(236, 72, 153, 0.14);
  border-color: rgba(236, 72, 153, 0.36);
}

.sidebar-section {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
}

.status-section {
  display: grid;
  gap: 10px;
}

.history-section {
  overflow: hidden;
  min-height: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title span,
.section-title small {
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.status-section .section-title span {
  color: #f4f4f5;
}

.status-section .section-title small {
  color: #f472b6;
}

.empty-hint {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.6;
}

.empty-hint {
  color: #a1a1aa;
  margin-top: 8px;
}

.ghost-action {
  border: none;
  background: transparent;
  color: #f472b6;
  font-family: inherit;
  font-weight: 600;
  font-size: 13px;
}

.history-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
  max-height: 100%;
  overflow: auto;
}

.history-item strong,
.history-item small {
  display: block;
}

.history-item strong {
  font-weight: 600;
  line-height: 1.4;
  white-space: normal;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.history-item small {
  color: #a1a1aa;
  margin-top: 6px;
  font-size: 12px;
}

.main-panel {
  padding: 22px 24px;
  display: grid;
  grid-template-rows: auto auto auto 1fr;
  gap: 16px;
  background: rgba(255, 255, 255, 0.28);
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.topbar h2 {
  margin: 0;
  font-size: 30px;
  font-family: "Crimson Pro", serif;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.01em;
}

.topbar-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-status {
  border: 1px solid var(--rf-border);
  border-radius: 999px;
  padding: 7px 12px;
  background: var(--rf-surface);
  color: var(--rf-secondary);
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.topbar-count {
  color: var(--rf-subtle);
  font-family: inherit;
  font-size: 14px;
}

.live-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: -2px;
}

.live-chip {
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  line-height: 1.2;
  border: 1px solid var(--rf-border);
  background: rgba(255, 255, 255, 0.82);
  color: var(--rf-muted);
}

.live-chip.active {
  background: #fff3f8;
  border-color: rgba(236, 72, 153, 0.28);
  color: var(--rf-accent);
}

.live-chip.thinking {
  background: #f5f3ff;
  border-color: #ddd6fe;
  color: #6d28d9;
}

.live-chip.done {
  background: #ecfdf3;
  border-color: #bbf7d0;
  color: var(--rf-success);
}

.conversation-shell,
.content-shell {
  background: var(--rf-surface);
  border: 1px solid var(--rf-border);
  border-radius: var(--rf-radius);
  box-shadow: var(--rf-shadow);
  padding: 18px;
  min-height: 0;
  overflow: auto;
}

.conversation-shell {
  display: grid;
  align-content: start;
  gap: 14px;
  overflow: auto;
}

.message {
  display: grid;
  gap: 6px;
}

.message.user {
  justify-items: end;
}

.message.user .bubble {
  background: var(--rf-primary);
  color: #fff;
}

.message.assistant .bubble {
  background: #fff;
  color: var(--rf-text);
}

.role {
  color: var(--rf-subtle);
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.bubble {
  max-width: min(760px, 100%);
  border: 1px solid var(--rf-border);
  border-radius: 14px;
  padding: 12px 14px;
  line-height: 1.8;
  box-shadow: 0 8px 24px rgba(24, 24, 27, 0.04);
  font-size: 16px;
}

.bubble p {
  margin: 8px 0 0;
}

.stage-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(24, 24, 27, 0.06);
  border: 1px solid var(--rf-border);
  color: var(--rf-secondary);
  font-style: normal;
}

.content-header,
.section-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.content-header h3 {
  margin: 0;
  font-family: "Crimson Pro", serif;
  font-size: 24px;
  font-weight: 600;
}

.sources-shell {
  display: grid;
  gap: 16px;
}

.source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 14px;
}

.source-list li {
  border: 1px solid var(--rf-border);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  padding: 16px;
}

.source-list a {
  color: var(--rf-text);
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
}

.source-list small,
.source-list p {
  display: block;
  margin-top: 6px;
  color: var(--rf-muted);
  line-height: 1.7;
  font-size: 14px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.sidebar-metrics article {
  position: relative;
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.12);
}

.sidebar-metrics article::before {
  content: "";
  position: absolute;
  left: 10px;
  right: 10px;
  top: 0;
  height: 2px;
  border-radius: 999px;
  opacity: 0.9;
}

.sidebar-metrics article:nth-child(1)::before {
  background: rgba(248, 113, 113, 0.78);
}

.sidebar-metrics article:nth-child(2)::before {
  background: rgba(244, 114, 182, 0.78);
}

.sidebar-metrics article:nth-child(3)::before {
  background: rgba(96, 165, 250, 0.78);
}

.sidebar-metrics article:nth-child(4)::before {
  background: rgba(74, 222, 128, 0.78);
}

.sidebar-metrics strong {
  color: #d4d4d8;
  font-size: 24px;
}

.sidebar-metrics span {
  color: #e4e4e7;
  font-size: 13px;
}

.metric-grid article {
  border: 1px solid var(--rf-border);
  border-radius: 12px;
  background: #fff;
  padding: 12px;
  display: grid;
  gap: 4px;
}

.metric-grid strong {
  font-family: "Crimson Pro", serif;
  font-size: 24px;
  font-weight: 600;
}

.metric-grid span {
  color: var(--rf-subtle);
  font-size: 13px;
}

.sidebar-status {
  margin: 0;
  color: #f1f5f9;
  font-size: 14px;
  line-height: 1.7;
}

.trace-stack {
  display: grid;
  gap: 6px;
  margin-top: 12px;
  color: var(--rf-muted);
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.sidebar-trace {
  margin-top: 0;
  color: #cbd5e1;
}

@media (max-width: 1240px) {
  .workspace {
    height: auto;
    grid-template-columns: 1fr;
    overflow: visible;
  }

  .sidebar {
    border: none;
    overflow: visible;
  }

  .main-panel {
    overflow: visible;
  }
}

@media (max-width: 640px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .main-panel {
    padding: 16px 14px;
  }

  .topbar,
  .section-title {
    flex-direction: column;
    align-items: flex-start;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
