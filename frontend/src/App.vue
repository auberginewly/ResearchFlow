<template>
  <RouterView />
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&family=Fira+Code:wght@400;500;600;700&display=swap");

:global(body) {
  margin: 0;
  font-family: "Atkinson Hyperlegible", "PingFang SC", "Noto Sans SC", sans-serif;
  background:
    radial-gradient(circle at top right, rgba(236, 72, 153, 0.08), transparent 25%),
    linear-gradient(180deg, #fafafa 0%, #f3f4f6 100%);
  color: #09090b;
  overflow: hidden;
}

:global(*) {
  box-sizing: border-box;
}

:global(:root) {
  --rf-bg: #fafafa;
  --rf-surface: rgba(255, 255, 255, 0.86);
  --rf-surface-strong: #ffffff;
  --rf-border: #e4e4e7;
  --rf-border-strong: #d4d4d8;
  --rf-text: #09090b;
  --rf-muted: #52525b;
  --rf-subtle: #71717a;
  --rf-primary: #18181b;
  --rf-secondary: #3f3f46;
  --rf-accent: #ec4899;
  --rf-accent-soft: rgba(236, 72, 153, 0.12);
  --rf-success: #166534;
  --rf-danger: #b91c1c;
  --rf-radius: 18px;
  --rf-shadow: 0 18px 40px rgba(24, 24, 27, 0.05);
}

</style>
