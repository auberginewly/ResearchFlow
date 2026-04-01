<script setup lang="ts">
import type { ResearchHistoryItem } from "../../types/research";

defineProps<{
  history: ResearchHistoryItem[];
}>();

const emit = defineEmits<{
  open: [researchId: string];
  refresh: [];
}>();
</script>

<template>
  <section class="panel">
    <div class="header">
      <h2>研究历史</h2>
      <div class="header-actions">
        <span>{{ history.length }} 条</span>
        <button type="button" class="refresh-btn" @click="emit('refresh')">
          刷新
        </button>
      </div>
    </div>
    <ul v-if="history.length" class="history-list">
      <li v-for="item in history" :key="item.id">
        <button type="button" @click="emit('open', item.id)">
          <strong>{{ item.topic }}</strong>
          <span>{{ item.status }}</span>
          <small v-if="item.reused">可复用记录</small>
          <small v-if="item.error" class="error">{{ item.error }}</small>
          <small>{{ new Date(item.updated_at).toLocaleString() }}</small>
        </button>
      </li>
    </ul>
    <p v-else>暂无研究历史</p>
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

h2 {
  margin: 0;
  font-family: "Fira Code", monospace;
  font-size: 18px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

button {
  width: 100%;
  text-align: left;
  border: 1px solid var(--rf-border);
  background: rgba(255, 255, 255, 0.76);
  border-radius: 14px;
  padding: 12px;
  cursor: pointer;
  display: grid;
  gap: 4px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

button:hover {
  border-color: var(--rf-accent);
  background: #fff;
}

.refresh-btn {
  width: auto;
  background: var(--rf-primary);
  color: #fff;
  border-color: var(--rf-primary);
  padding: 6px 10px;
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

strong {
  color: var(--rf-text);
}

span,
small {
  color: var(--rf-subtle);
}

.error {
  color: var(--rf-danger);
}
</style>
