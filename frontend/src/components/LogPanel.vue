<script setup lang="ts">
defineProps<{
  logs: string[];
}>();
</script>

<template>
  <section class="panel">
    <div class="header">
      <h2>执行日志</h2>
      <span>{{ logs.length }} 条</span>
    </div>
    <ul v-if="logs.length" class="logs">
      <li v-for="(log, index) in logs" :key="`${log}-${index}`">{{ log }}</li>
    </ul>
    <p v-else>暂无日志输出</p>
  </section>
</template>

<style scoped>
.panel {
  background: var(--rf-primary);
  color: #f4f4f5;
  border: 1px solid rgba(255, 255, 255, 0.08);
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

.header span {
  color: rgba(255, 255, 255, 0.66);
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.logs {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
  color: #e4e4e7;
  max-height: 460px;
  overflow: auto;
}

.logs li {
  line-height: 1.7;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  font-family: "Fira Code", monospace;
  font-size: 12.5px;
}
</style>
