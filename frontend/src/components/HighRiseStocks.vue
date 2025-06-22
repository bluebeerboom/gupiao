<template>
  <div class="high-rise-stocks">
    <div class="header">
      <h2>📈 高涨幅创新高股票</h2>
      <div class="stats" v-if="stats">
        <span class="stat-item">
          <span class="label">总股票数:</span>
          <span class="value">{{ stats.total }}</span>
        </span>
        <span class="stat-item">
          <span class="label">3年新高:</span>
          <span class="value highlight">{{ stats.threeYearHighs }}</span>
        </span>
        <span class="stat-item">
          <span class="label">历史新高:</span>
          <span class="value highlight">{{ stats.allTimeHighs }}</span>
        </span>
      </div>
    </div>

    <div class="loading" v-if="loading">
      <div class="spinner"></div>
      <p>正在分析高涨幅股票...</p>
    </div>

    <div class="error" v-else-if="error">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <div class="content" v-else-if="stocks.length > 0">
      <!-- 筛选器 -->
      <div class="filters">
        <label>
          <input type="checkbox" v-model="showThreeYearHighs" />
          只显示3年新高
        </label>
        <label>
          <input type="checkbox" v-model="showAllTimeHighs" />
          只显示历史新高
        </label>
      </div>

      <!-- 股票列表 -->
      <div class="stock-list">
        <div 
          v-for="stock in filteredStocks" 
          :key="stock.ts_code"
          class="stock-item"
          :class="{ 
            'three-year-high': stock.is_3y_high,
            'all-time-high': stock.is_all_time_high 
          }"
        >
          <div class="stock-header">
            <div class="stock-info">
              <h3>{{ stock.name }}</h3>
              <span class="code">{{ stock.ts_code }}</span>
            </div>
            <div class="price-info">
              <span class="current-price">¥{{ stock.current_price.toFixed(2) }}</span>
              <span class="pct-change" :class="{ positive: stock.pct_chg > 0 }">
                +{{ stock.pct_chg.toFixed(2) }}%
              </span>
            </div>
          </div>
          
          <div class="stock-details">
            <div class="detail-item">
              <span class="label">3年最高:</span>
              <span class="value">¥{{ stock.max_3y.toFixed(2) }}</span>
              <span class="badge" :class="{ active: stock.is_3y_high }">
                {{ stock.is_3y_high ? '✅ 3年新高' : '❌ 非3年新高' }}
              </span>
            </div>
            <div class="detail-item" v-if="stock.max_all">
              <span class="label">历史最高:</span>
              <span class="value">¥{{ stock.max_all.toFixed(2) }}</span>
              <span class="badge" :class="{ active: stock.is_all_time_high }">
                {{ stock.is_all_time_high ? '🏆 历史新高' : '📊 非历史新高' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="empty" v-else>
      <p>暂无高涨幅股票数据</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getHighRiseStocks } from '../api'

export default {
  name: 'HighRiseStocks',
  setup() {
    const stocks = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showThreeYearHighs = ref(false)
    const showAllTimeHighs = ref(false)
    const tradeDate = ref(null)

    const stats = computed(() => {
      if (stocks.value.length === 0) return null
      
      const threeYearHighs = stocks.value.filter(s => s.is_3y_high).length
      const allTimeHighs = stocks.value.filter(s => s.is_all_time_high).length
      
      return {
        total: stocks.value.length,
        threeYearHighs,
        allTimeHighs
      }
    })

    const filteredStocks = computed(() => {
      let filtered = stocks.value
      
      if (showThreeYearHighs.value) {
        filtered = filtered.filter(s => s.is_3y_high)
      }
      
      if (showAllTimeHighs.value) {
        filtered = filtered.filter(s => s.is_all_time_high)
      }
      
      return filtered.sort((a, b) => b.pct_chg - a.pct_chg)
    })

    const loadData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const data = await getHighRiseStocks()
        console.log('高涨幅股票数据:', data)
        stocks.value = data.stocks || []
        tradeDate.value = data.trade_date
      } catch (error) {
        console.error('加载高涨幅股票失败:', error)
        alert('加载失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      stocks,
      loading,
      error,
      stats,
      showThreeYearHighs,
      showAllTimeHighs,
      filteredStocks,
      loadData,
      tradeDate
    }
  }
}
</script>

<style scoped>
.high-rise-stocks {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 30px;
  text-align: center;
}

.header h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 20px;
  background: #f8f9fa;
  border-radius: 10px;
  min-width: 120px;
}

.stat-item .label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 5px;
}

.stat-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-item .value.highlight {
  color: #e74c3c;
}

.filters {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.filters label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.filters label:hover {
  background: #e9ecef;
}

.stock-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.stock-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  border-left: 4px solid #ddd;
}

.stock-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stock-item.three-year-high {
  border-left-color: #e74c3c;
  background: linear-gradient(135deg, #fff 0%, #fff5f5 100%);
}

.stock-item.all-time-high {
  border-left-color: #f39c12;
  background: linear-gradient(135deg, #fff 0%, #fff8e1 100%);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.stock-info h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 18px;
}

.code {
  color: #6c757d;
  font-size: 14px;
}

.price-info {
  text-align: right;
}

.current-price {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.pct-change {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: #e74c3c;
}

.pct-change.positive {
  color: #27ae60;
}

.stock-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-item .label {
  font-size: 14px;
  color: #6c757d;
  min-width: 80px;
}

.detail-item .value {
  font-weight: bold;
  color: #2c3e50;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  background: #f8f9fa;
  color: #6c757d;
}

.badge.active {
  background: #e74c3c;
  color: white;
}

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
}

.retry-btn:hover {
  background: #2980b9;
}

.empty {
  text-align: center;
  padding: 50px;
  color: #6c757d;
}

@media (max-width: 768px) {
  .stock-list {
    grid-template-columns: 1fr;
  }
  
  .stats {
    gap: 15px;
  }
  
  .stat-item {
    min-width: 100px;
    padding: 10px 15px;
  }
}
</style> 