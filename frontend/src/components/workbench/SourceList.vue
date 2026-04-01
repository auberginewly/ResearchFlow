<script setup lang="ts">
import type { SearchSource } from "../../types/research";

defineProps<{
  sources: SearchSource[];
}>();
</script>

<template>
  <div class="sources" v-if="sources.length">
    <h3>来源</h3>
    <ul>
      <li v-for="source in sources" :key="source.url">
        <a :href="source.url" target="_blank" rel="noreferrer">
          {{ source.title }}
        </a>
        <span v-if="source.provider"> · {{ source.provider }}</span>
        <p v-if="source.snippet">{{ source.snippet }}</p>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.sources {
  margin-top: 12px;
  border-top: 1px solid var(--rf-border);
  padding-top: 12px;
}

.sources h3 {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--rf-secondary);
  font-family: "Fira Code", monospace;
}

.sources ul {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
}

.sources a {
  color: var(--rf-accent);
  text-decoration: none;
}

.sources a:hover {
  text-decoration: underline;
}

.sources p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--rf-muted);
  line-height: 1.6;
}
</style>
