import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import StockList from './components/StockList.vue'
import StockDetail from './components/StockDetail.vue'
import MarketStats from './components/MarketStats.vue'
import HighRiseStocks from './components/HighRiseStocks.vue'
import StockHighestCheck from './components/StockHighestCheck.vue'

// 创建路由
const routes = [
  {
    path: '/',
    name: 'StockList',
    component: StockList
  },
  {
    path: '/stock/:tsCode',
    name: 'StockDetail',
    component: StockDetail,
    props: true
  },
  {
    path: '/market-stats',
    name: 'MarketStats',
    component: MarketStats
  },
  {
    path: '/high-rise-stocks',
    name: 'HighRiseStocks',
    component: HighRiseStocks
  },
  {
    path: '/stock-check',
    name: 'StockHighestCheck',
    component: StockHighestCheck
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 创建应用
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app') 