<script setup lang="ts">
import { computed, ref, watch } from "vue";

const emit = defineEmits<{
  submit: [topic: string];
}>();

const props = defineProps<{
  isRunning: boolean;
  currentTopic?: string;
}>();

const topic = ref("");
const canSubmit = computed(() => Boolean(topic.value.trim()) && !props.isRunning);
const suggestedTopics = [
  "MCP 与 AI Agent 的协议差异",
  "Claude Code 源码泄漏事件时间线",
  "OpenAI Responses API 与 Assistants API 的迁移差异",
];

watch(
  () => props.currentTopic,
  (value) => {
    if (typeof value === "string" && value.trim()) {
      topic.value = value;
    }
  },
  { immediate: true },
);

const onSubmit = () => {
  const value = topic.value.trim();
  if (!value || props.isRunning) return;
  emit("submit", value);
};

const applySuggestion = (value: string) => {
  topic.value = value;
};
</script>

<template>
  <section class="panel">
    <div class="form-row">
      <label class="visually-hidden" for="research-topic">研究命题</label>
      <input
        id="research-topic"
        v-model="topic"
        type="text"
        :placeholder="isRunning ? '研究执行中，可修改命题后再次发起' : '输入一个研究主题，例如：MCP 与 AI Agent 的协议差异'"
      />
      <button type="button" :disabled="!canSubmit" @click="onSubmit">
        {{ isRunning ? "研究中..." : "启动" }}
      </button>
    </div>
    <div class="suggestions">
      <button
        v-for="item in suggestedTopics"
        :key="item"
        type="button"
        class="chip"
        @click="applySuggestion(item)"
      >
        {{ item }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.panel {
  background: var(--rf-surface);
  border: 1px solid var(--rf-border);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(24, 24, 27, 0.04);
  padding: 12px;
  display: grid;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 12px;
}

input {
  flex: 1;
  min-height: 48px;
  padding: 12px 14px;
  border: 1px solid var(--rf-border-strong);
  border-radius: 12px;
  font-size: 15px;
  background: #fff;
  color: var(--rf-text);
  font-family: inherit;
  line-height: 1.4;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  outline: none;
  border-color: var(--rf-accent);
  box-shadow: 0 0 0 4px var(--rf-accent-soft);
}

button {
  min-width: 104px;
  border: 1px solid #111827;
  border-radius: 12px;
  padding: 0 16px;
  background: var(--rf-primary);
  color: #fff;
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

button:hover:enabled {
  background: var(--rf-accent);
  border-color: var(--rf-accent);
  transform: translateY(-1px);
}

button:disabled {
  background: #d4d4d8;
  border-color: #d4d4d8;
  color: #71717a;
  cursor: not-allowed;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border: 1px solid var(--rf-border);
  border-radius: 999px;
  background: #fff;
  color: var(--rf-muted);
  padding: 6px 12px;
  font-size: 13px;
  line-height: 1.2;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}

.chip:hover {
  border-color: var(--rf-accent);
  color: var(--rf-accent);
  background: #fff8fc;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 720px) {
  .form-row {
    flex-direction: column;
  }

  button {
    min-height: 44px;
  }
}
</style>
