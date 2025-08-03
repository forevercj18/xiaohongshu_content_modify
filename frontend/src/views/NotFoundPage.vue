<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在。</p>
      <div class="actions">
        <router-link to="/" class="btn btn-primary">
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}

.not-found-content {
  text-align: center;
  
  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
    margin-bottom: 20px;
  }
  
  h1 {
    font-size: 32px;
    color: var(--text-primary);
    margin-bottom: 16px;
  }
  
  p {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 32px;
  }
}
</style>