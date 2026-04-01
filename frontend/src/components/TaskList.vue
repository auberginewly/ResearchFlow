<script setup lang="ts">
import SourceList from "./workbench/SourceList.vue";
import type { ResearchTask } from "../types/research";

defineProps<{
  tasks: ResearchTask[];
}>();
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>研究任务</h2>
      <span>{{ tasks.length }} 项</span>
    </div>
    <ul v-if="tasks.length" class="task-list">
      <li v-for="task in tasks" :key="task.id">
        <div class="task-top">
          <strong>{{ task.title }}</strong>
          <span class="status">{{ task.status }}</span>
        </div>
        <div v-if="task.trace" class="trace">
          <span>provider: {{ task.trace.provider || "-" }}</span>
          <span>fallback: {{ task.trace.used_fallback ? "是" : "否" }}</span>
          <span>results: {{ task.trace.result_count }}</span>
          <span v-if="task.trace.query_cache_hit">query cache</span>
          <span v-if="task.trace.search_cache_hit">search cache</span>
          <span v-if="task.trace.note_cache_hit">note cache</span>
        </div>
        <div v-if="task.trace?.rewritten_queries?.length" class="queries">
          <strong>Queries:</strong>
          <span>{{ task.trace.rewritten_queries.join(" | ") }}</span>
        </div>
        <div v-if="task.notes?.length" class="notes">
          <h3>研究笔记</h3>
          <ul>
            <li v-for="note in task.notes" :key="`${task.id}-${note.title}-${note.category}`">
              <strong>[{{ note.category }}]</strong> {{ note.content }}
            </li>
          </ul>
        </div>
        <p v-if="task.summary">{{ task.summary }}</p>
        <SourceList :sources="task.sources || []" />
      </li>
    </ul>
    <p v-else>等待任务规划...</p>
  </section>
</template>

<style scoped>
.panel {
  background: var(--rf-surface);
  border: 1px solid var(--rf-border);
  border-radius: var(--rf-radius);
  box-shadow: var(--rf-shadow);
  padding: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

h2 {
  margin: 0;
  font-family: "Fira Code", monospace;
  font-size: 18px;
}

.panel-header span {
  color: var(--rf-subtle);
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 14px;
}

li {
  padding: 16px;
  border: 1px solid var(--rf-border);
  background: var(--rf-surface-strong);
  border-radius: 16px;
}

.task-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.status {
  color: var(--rf-accent);
  background: var(--rf-accent-soft);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
  text-transform: uppercase;
  font-family: "Fira Code", monospace;
}

p {
  margin: 10px 0 0;
  color: var(--rf-muted);
  line-height: 1.7;
}

.trace,
.queries {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 10px;
  color: var(--rf-subtle);
  font-size: 12px;
  font-family: "Fira Code", monospace;
}

.notes {
  margin-top: 12px;
  border-top: 1px solid var(--rf-border);
  padding-top: 12px;
}

.notes h3 {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--rf-secondary);
  font-family: "Fira Code", monospace;
}

.notes ul {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
}

.notes li {
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 0;
}
</style>
