<template>
  <div id="app" class="app-container" :data-theme="themeStore.currentTheme">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// 初始化主题
onMounted(() => {
  themeStore.initTheme()
})
</script>

<style lang="scss">
#app {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>