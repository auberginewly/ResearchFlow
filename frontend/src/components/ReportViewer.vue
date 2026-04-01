<script setup lang="ts">
import { computed, ref } from "vue";
import { marked } from "marked";

import { getResearchPdfExportUrl } from "../api/research";

const props = defineProps<{
  report: string;
  exportPath: string;
  reused?: boolean;
  topic?: string;
}>();

const previewMode = ref<"preview" | "markdown">("preview");
const isPdfPreviewOpen = ref(false);

const renderMarkdown = (content: string): string => {
  return marked.parser(marked.lexer(content));
};

const renderedReport = computed(() => {
  if (!props.report) {
    return "<p>研究完成后会在这里展示最终报告。</p>";
  }
  return renderMarkdown(props.report);
});

const openPdfPreview = () => {
  if (!props.report) return;
  isPdfPreviewOpen.value = true;
};

const confirmPdfExport = () => {
  if (!props.exportPath) return;
  const pathParts = props.exportPath.split("/");
  const researchId = pathParts[pathParts.length - 1];
  if (!researchId) return;
  window.open(getResearchPdfExportUrl(researchId), "_blank", "noopener,noreferrer");
  isPdfPreviewOpen.value = false;
};
</script>

<template>
  <section class="panel">
    <div class="header">
      <h2>研究报告</h2>
      <div class="actions">
        <span v-if="reused" class="badge">历史复用</span>
        <button type="button" class="secondary-btn" :class="{ active: previewMode === 'preview' }" @click="previewMode = 'preview'">
          预览
        </button>
        <button type="button" class="secondary-btn" :class="{ active: previewMode === 'markdown' }" @click="previewMode = 'markdown'">
          Markdown
        </button>
        <a v-if="exportPath" :href="exportPath" target="_blank" rel="noreferrer">
          导出 Markdown
        </a>
        <button type="button" class="secondary-btn" :disabled="!report" @click="openPdfPreview">
          PDF 预览
        </button>
      </div>
    </div>
    <p class="caption">最终结论区保留完整文本输出，适合直接复核、复制和导出。</p>
    <article v-if="previewMode === 'preview'" class="markdown-body" v-html="renderedReport" />
    <pre v-else>{{ report || "研究完成后会在这里展示最终报告" }}</pre>

    <div v-if="isPdfPreviewOpen" class="overlay" @click.self="isPdfPreviewOpen = false">
      <section class="modal">
        <div class="modal-header">
          <div>
            <h3>PDF 导出预览</h3>
            <p>确认预览内容无误后，再继续导出 PDF。</p>
          </div>
          <button type="button" class="secondary-btn" @click="isPdfPreviewOpen = false">关闭</button>
        </div>
        <article class="modal-preview markdown-body" v-html="renderedReport" />
        <div class="modal-actions">
          <span>确认后将由后端直接生成并下载 PDF 文件。</span>
          <button type="button" class="secondary-btn primary-btn" @click="confirmPdfExport">
            确认导出 PDF
          </button>
        </div>
      </section>
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
  align-items: center;
  margin-bottom: 12px;
}

h2 {
  margin: 0;
  font-family: "Fira Code", monospace;
  font-size: 18px;
}

.header a {
  color: var(--rf-accent);
  text-decoration: none;
  font-family: "Fira Code", monospace;
  font-size: 12px;
}

.actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.secondary-btn {
  border: 1px solid var(--rf-border);
  border-radius: 999px;
  background: #fff;
  color: var(--rf-secondary);
  padding: 7px 10px;
  font-family: "Fira Code", monospace;
  font-size: 12px;
  cursor: pointer;
}

.secondary-btn.active {
  background: var(--rf-primary);
  color: #fff;
  border-color: var(--rf-primary);
}

.secondary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.primary-btn {
  background: var(--rf-primary);
  color: #fff;
  border-color: var(--rf-primary);
}

.badge {
  background: #ecfdf3;
  color: var(--rf-success);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #bbf7d0;
  font-family: "Fira Code", monospace;
}

.caption {
  margin: 0 0 12px;
  color: var(--rf-muted);
  font-size: 13px;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  line-height: 1.75;
  color: var(--rf-text);
  border: 1px solid var(--rf-border);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 14px;
  padding: 16px;
}

.markdown-body {
  border: 1px solid var(--rf-border);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 14px;
  padding: 16px;
  line-height: 1.8;
  color: var(--rf-text);
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin-top: 1.2em;
  margin-bottom: 0.55em;
  font-family: "Crimson Pro", serif;
  line-height: 1.2;
}

.markdown-body :deep(h1:first-child),
.markdown-body :deep(h2:first-child),
.markdown-body :deep(h3:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p),
.markdown-body :deep(li) {
  line-height: 1.8;
}

.markdown-body :deep(code) {
  font-family: "Fira Code", monospace;
  background: rgba(24, 24, 27, 0.06);
  padding: 2px 6px;
  border-radius: 6px;
}

.markdown-body :deep(pre) {
  overflow: auto;
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(9, 9, 11, 0.45);
  display: grid;
  place-items: center;
  padding: 24px;
}

.modal {
  width: min(920px, 100%);
  max-height: min(88vh, 920px);
  background: #fff;
  border: 1px solid var(--rf-border);
  border-radius: 18px;
  box-shadow: 0 30px 80px rgba(24, 24, 27, 0.18);
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
}

.modal-header,
.modal-actions {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--rf-border);
}

.modal-actions {
  border-bottom: none;
  border-top: 1px solid var(--rf-border);
}

.modal-header h3 {
  margin: 0 0 4px;
  font-family: "Crimson Pro", serif;
  font-size: 24px;
}

.modal-header p,
.modal-actions span {
  margin: 0;
  color: var(--rf-muted);
  font-size: 13px;
}

.modal-preview {
  margin: 18px;
  overflow: auto;
}
</style>
