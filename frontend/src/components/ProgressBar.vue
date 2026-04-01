<script setup lang="ts">
defineProps<{
  progress: number;
}>();
</script>

<template>
  <section class="panel">
    <div class="header">
      <div>
        <h2>执行进度</h2>
        <p>系统会持续流式更新任务拆分、搜索、笔记整理与报告生成状态。</p>
      </div>
      <span class="percent">{{ progress }}%</span>
    </div>
    <div class="track">
      <div class="fill" :style="{ width: `${progress}%` }" />
    </div>
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
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 16px;
}

h2 {
  margin: 0 0 4px;
  font-family: "Fira Code", monospace;
  font-size: 18px;
}

p {
  margin: 0;
  color: var(--rf-muted);
  font-size: 13px;
  line-height: 1.5;
}

.percent {
  color: var(--rf-primary);
  font-family: "Fira Code", monospace;
  font-weight: 600;
}

.track {
  height: 10px;
  background: #e4e4e7;
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background: linear-gradient(90deg, #18181b, #ec4899);
}
</style>
