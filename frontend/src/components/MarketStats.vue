<template>
  <div class="market-stats">
    <div class="header">
      <h2>📊 市场统计分析</h2>
      <button @click="loadData" :disabled="loading" class="refresh-btn">
        {{ loading ? '加载中...' : '刷新数据' }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <p>正在加载市场数据...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <div v-else-if="marketData" class="market-content">
      <!-- 基础统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card total">
          <h3>总股票数</h3>
          <div class="stat-value">{{ marketData.today_stats?.total?.toLocaleString() || 'N/A' }}</div>
        </div>
        <div class="stat-card rise">
          <h3>上涨股票</h3>
          <div class="stat-value">{{ marketData.today_stats?.rise?.toLocaleString() || 'N/A' }}</div>
          <div class="stat-ratio">{{ marketData.today_stats?.rise_ratio?.toFixed(1) || 'N/A' }}%</div>
        </div>
        <div class="stat-card fall">
          <h3>下跌股票</h3>
          <div class="stat-value">{{ marketData.today_stats?.fall?.toLocaleString() || 'N/A' }}</div>
        </div>
        <div class="stat-card flat">
          <h3>平盘股票</h3>
          <div class="stat-value">{{ marketData.today_stats?.flat?.toLocaleString() || 'N/A' }}</div>
        </div>
      </div>

      <!-- 涨跌分布 -->
      <div class="distribution-section" v-if="marketData.rise_distribution && marketData.fall_distribution">
        <div class="rise-distribution">
          <h3>📈 上涨股票分布</h3>
          <div class="distribution-grid">
            <div v-for="(data, label) in marketData.rise_distribution" :key="label" class="dist-item">
              <div class="dist-label">{{ label }}</div>
              <div class="dist-count">{{ data.count }}</div>
              <div class="dist-percent">{{ data.percentage?.toFixed(1) || '0.0' }}%</div>
            </div>
          </div>
        </div>

        <div class="fall-distribution">
          <h3>📉 下跌股票分布</h3>
          <div class="distribution-grid">
            <div v-for="(data, label) in marketData.fall_distribution" :key="label" class="dist-item">
              <div class="dist-label">{{ label }}</div>
              <div class="dist-count">{{ data.count }}</div>
              <div class="dist-percent">{{ data.percentage?.toFixed(1) || '0.0' }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史对比 -->
      <div v-if="marketData.avg_stats" class="history-section">
        <h3>📈 近5日平均值对比</h3>
        <div class="comparison-grid">
          <div class="comp-item">
            <div class="comp-label">平均上涨股票</div>
            <div class="comp-value">{{ marketData.avg_stats.avg_rise?.toLocaleString() || 'N/A' }}</div>
            <div class="comp-today">今日: {{ marketData.today_stats?.rise?.toLocaleString() || 'N/A' }}</div>
          </div>
          <div class="comp-item">
            <div class="comp-label">平均下跌股票</div>
            <div class="comp-value">{{ marketData.avg_stats.avg_fall?.toLocaleString() || 'N/A' }}</div>
            <div class="comp-today">今日: {{ marketData.today_stats?.fall?.toLocaleString() || 'N/A' }}</div>
          </div>
          <div class="comp-item">
            <div class="comp-label">平均上涨比例</div>
            <div class="comp-value">{{ marketData.avg_stats.avg_rise_ratio?.toFixed(1) || 'N/A' }}%</div>
            <div class="comp-today">今日: {{ marketData.today_stats?.rise_ratio?.toFixed(1) || 'N/A' }}%</div>
          </div>
        </div>
      </div>

      <!-- 最近交易日详情 -->
      <div v-if="marketData.recent_stats && marketData.recent_stats.length > 0" class="recent-section">
        <h3>📋 最近5个交易日详情</h3>
        <div class="recent-list">
          <div v-for="stat in marketData.recent_stats.slice().reverse()" :key="stat.date" class="recent-item">
            <div class="recent-date">{{ stat.date }}</div>
            <div class="recent-stats">
              上涨 {{ stat.rise?.toLocaleString() || 'N/A' }} 只 ({{ stat.rise_ratio?.toFixed(1) || 'N/A' }}%)
              <span class="trend-emoji">{{ (stat.rise_ratio || 0) > 50 ? '📈' : '📉' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 交易日期 -->
      <div class="trade-date">
        <p>数据日期: {{ marketData.trade_date || 'N/A' }}</p>
      </div>
    </div>

    <div v-else class="no-data">
      <p>暂无市场数据</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getMarketAnalysis } from '../api'

export default {
  name: 'MarketStats',
  setup() {
    const marketData = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const loadData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const data = await getMarketAnalysis()
        
        if (data && typeof data === 'object') {
          marketData.value = data
        } else {
          console.error('返回的数据格式不正确:', data)
          error.value = '数据格式不正确'
        }
      } catch (err) {
        console.error('加载市场数据失败:', err)
        error.value = err.response?.data?.detail || '加载市场数据失败'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      marketData,
      loading,
      error,
      loadData
    }
  }
}
</script>

<style scoped>
.market-stats {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.refresh-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #dc3545;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-ratio {
  font-size: 14px;
  color: #007bff;
}

.total .stat-value { color: #333; }
.rise .stat-value { color: #28a745; }
.fall .stat-value { color: #dc3545; }
.flat .stat-value { color: #6c757d; }

/* 分布区域 */
.distribution-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.rise-distribution, .fall-distribution {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.rise-distribution h3, .fall-distribution h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.distribution-grid {
  display: grid;
  gap: 15px;
}

.dist-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 15px;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

.dist-label {
  font-weight: 500;
}

.dist-count {
  font-weight: bold;
  color: #333;
}

.dist-percent {
  color: #666;
  font-size: 14px;
}

/* 历史对比 */
.history-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.history-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.comp-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.comp-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.comp-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.comp-today {
  font-size: 12px;
  color: #007bff;
}

/* 最近交易日 */
.recent-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.recent-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.recent-list {
  display: grid;
  gap: 10px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 5px;
}

.recent-date {
  font-weight: 500;
  color: #333;
}

.recent-stats {
  color: #666;
}

.trend-emoji {
  margin-left: 8px;
}

.trade-date {
  text-align: center;
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .distribution-section {
    grid-template-columns: 1fr;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  
  .recent-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style> 