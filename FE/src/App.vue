<template>
  <div class="app">
    <header class="app-header">
      <h1>JejuDoldam</h1>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
}

.app-main {
  flex: 1;
  padding: 24px;
}
</style>
