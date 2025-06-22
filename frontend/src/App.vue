<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>📈 股票分析系统</h1>
        </div>
        <div class="nav-menu">
          <router-link to="/" class="nav-link" active-class="active">股票列表</router-link>
          <router-link to="/market-stats" class="nav-link" active-class="active">市场统计</router-link>
          <router-link to="/high-rise-stocks" class="nav-link" active-class="active">高涨幅股票</router-link>
          <router-link to="/stock-check" class="nav-link" active-class="active">股票检查</router-link>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>&copy; 2024 股票分析系统 - 基于 Tushare 数据</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
  color: #2c3e50;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 70px;
}

.nav-brand h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 10px 16px;
  border-radius: 8px;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.main-content {
  flex: 1;
  padding: 20px 0;
}

.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
  margin-top: auto;
}

.footer p {
  margin: 0;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    padding: 15px 20px;
    gap: 15px;
  }
  
  .nav-brand h1 {
    font-size: 20px;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .nav-link {
    padding: 8px 12px;
    font-size: 14px;
  }
}

/* 通用样式 */
.loading {
  text-align: center;
  padding: 50px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 50px;
  color: #e74c3c;
}

.retry-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background: #2980b9;
}

.empty {
  text-align: center;
  padding: 50px;
  color: #6c757d;
}
</style> 