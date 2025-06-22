<template>
  <div class="stock-highest-check">
    <div class="header">
      <h2>🔍 股票最高价检查</h2>
      <p>检查指定股票是否为今日最高价</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-section">
      <div class="search-box">
        <input 
          v-model="stockCode" 
          @keyup.enter="checkStock"
          placeholder="请输入股票代码，如：000001.SZ"
          class="search-input"
        />
        <button @click="checkStock" :disabled="loading" class="search-btn">
          {{ loading ? '检查中...' : '检查' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <div class="spinner"></div>
      <p>正在检查股票数据...</p>
    </div>

    <!-- 错误信息 -->
    <div class="error" v-else-if="error">
      <p>{{ error }}</p>
      <button @click="checkStock" class="retry-btn">重试</button>
    </div>

    <!-- 结果展示 -->
    <div class="result" v-else-if="stockData">
      <div class="stock-card" :class="{ 'is-highest': stockData.is_highest }">
        <div class="stock-header">
          <div class="stock-info">
            <h3>{{ stockData.name }}</h3>
            <span class="code">{{ stockData.ts_code }}</span>
          </div>
          <div class="status-badge" :class="{ 'highest': stockData.is_highest }">
            {{ stockData.is_highest ? '🏆 今日最高' : '📊 非今日最高' }}
          </div>
        </div>

        <div class="price-comparison">
          <div class="price-item">
            <span class="label">今日收盘价</span>
            <span class="value current">¥{{ stockData.today_close.toFixed(2) }}</span>
          </div>
          <div class="price-item">
            <span class="label">3年最高价</span>
            <span class="value max">¥{{ stockData.max_close.toFixed(2) }}</span>
          </div>
          <div class="price-diff">
            <span class="label">价差</span>
            <span class="value" :class="{ 'positive': priceDiff > 0, 'negative': priceDiff < 0 }">
              {{ priceDiff > 0 ? '+' : '' }}¥{{ priceDiff.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="trade-date">
          交易日期: {{ formatDate(stockData.trade_date) }}
        </div>
      </div>

      <!-- 历史价格图表 -->
      <div class="chart-section" v-if="stockData.history && stockData.history.length > 0">
        <h3>历史价格走势</h3>
        <div class="chart-container">
          <canvas ref="chartCanvas" width="800" height="400"></canvas>
        </div>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="instructions" v-if="!stockData && !loading && !error">
      <h3>使用说明</h3>
      <ul>
        <li>输入完整的股票代码，如：000001.SZ（平安银行）</li>
        <li>支持A股、港股、美股代码格式</li>
        <li>系统将检查该股票今日收盘价是否为近3年最高价</li>
        <li>同时显示历史价格走势图表</li>
      </ul>
      
      <div class="examples">
        <h4>示例代码：</h4>
        <div class="example-codes">
          <span class="example">000001.SZ</span>
          <span class="example">000002.SZ</span>
          <span class="example">600000.SH</span>
          <span class="example">01810.HK</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { checkIsHighestToday } from '../api'

export default {
  name: 'StockHighestCheck',
  setup() {
    const stockCode = ref('')
    const stockData = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const chartCanvas = ref(null)

    const priceDiff = computed(() => {
      if (!stockData.value) return 0
      return stockData.value.today_close - stockData.value.max_close
    })

    const checkStock = async () => {
      if (!stockCode.value.trim()) {
        alert('请输入股票代码')
        return
      }
      
      loading.value = true
      try {
        const result = await checkIsHighestToday(stockCode.value)
        stockData.value = result
        console.log('股票检查结果:', result)
      } catch (error) {
        console.error('检查失败:', error)
        alert('检查失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`
    }

    const drawChart = (historyData) => {
      if (!chartCanvas.value) return

      const canvas = chartCanvas.value
      const ctx = canvas.getContext('2d')
      
      // 清空画布
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (historyData.length === 0) return

      // 准备数据
      const prices = historyData.map(item => item.close)
      const dates = historyData.map(item => formatDate(item.date))
      const minPrice = Math.min(...prices)
      const maxPrice = Math.max(...prices)
      const priceRange = maxPrice - minPrice

      // 设置图表参数
      const padding = 60
      const chartWidth = canvas.width - 2 * padding
      const chartHeight = canvas.height - 2 * padding
      const pointSpacing = chartWidth / (prices.length - 1)

      // 绘制坐标轴
      ctx.strokeStyle = '#ddd'
      ctx.lineWidth = 1
      
      // Y轴
      ctx.beginPath()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, canvas.height - padding)
      ctx.stroke()
      
      // X轴
      ctx.beginPath()
      ctx.moveTo(padding, canvas.height - padding)
      ctx.lineTo(canvas.width - padding, canvas.height - padding)
      ctx.stroke()

      // 绘制价格线
      ctx.strokeStyle = '#3498db'
      ctx.lineWidth = 2
      ctx.beginPath()

      prices.forEach((price, index) => {
        const x = padding + index * pointSpacing
        const y = canvas.height - padding - ((price - minPrice) / priceRange) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.stroke()

      // 绘制数据点
      ctx.fillStyle = '#3498db'
      prices.forEach((price, index) => {
        const x = padding + index * pointSpacing
        const y = canvas.height - padding - ((price - minPrice) / priceRange) * chartHeight
        
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, 2 * Math.PI)
        ctx.fill()
      })

      // 标注今日价格点
      if (stockData.value) {
        const todayPrice = stockData.value.today_close
        const todayIndex = prices.length - 1
        const x = padding + todayIndex * pointSpacing
        const y = canvas.height - padding - ((todayPrice - minPrice) / priceRange) * chartHeight
        
        ctx.fillStyle = stockData.value.is_highest ? '#e74c3c' : '#f39c12'
        ctx.beginPath()
        ctx.arc(x, y, 6, 0, 2 * Math.PI)
        ctx.fill()
        
        // 添加标签
        ctx.fillStyle = '#2c3e50'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(`今日: ¥${todayPrice.toFixed(2)}`, x, y - 10)
      }

      // 绘制Y轴标签
      ctx.fillStyle = '#666'
      ctx.font = '12px Arial'
      ctx.textAlign = 'right'
      for (let i = 0; i <= 5; i++) {
        const price = minPrice + (priceRange * i / 5)
        const y = canvas.height - padding - (chartHeight * i / 5)
        ctx.fillText(`¥${price.toFixed(2)}`, padding - 10, y + 4)
      }

      // 绘制X轴标签（简化，只显示部分日期）
      ctx.textAlign = 'center'
      const step = Math.max(1, Math.floor(dates.length / 8))
      for (let i = 0; i < dates.length; i += step) {
        const x = padding + i * pointSpacing
        ctx.fillText(dates[i].slice(5), x, canvas.height - padding + 20)
      }
    }

    return {
      stockCode,
      stockData,
      loading,
      error,
      priceDiff,
      chartCanvas,
      checkStock,
      formatDate
    }
  }
}
</script>

<style scoped>
.stock-highest-check {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.header p {
  color: #6c757d;
  margin: 0;
}

.search-section {
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #3498db;
}

.search-btn {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover:not(:disabled) {
  background: #2980b9;
}

.search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.stock-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  border-left: 4px solid #ddd;
  transition: all 0.3s;
}

.stock-card.is-highest {
  border-left-color: #e74c3c;
  background: linear-gradient(135deg, #fff 0%, #fff5f5 100%);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stock-info h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 24px;
}

.code {
  color: #6c757d;
  font-size: 16px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  background: #f8f9fa;
  color: #6c757d;
}

.status-badge.highest {
  background: #e74c3c;
  color: white;
}

.price-comparison {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.price-item, .price-diff {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.price-item .label, .price-diff .label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
}

.price-item .value, .price-diff .value {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.price-item .value.current {
  color: #3498db;
}

.price-item .value.max {
  color: #e74c3c;
}

.price-diff .value.positive {
  color: #27ae60;
}

.price-diff .value.negative {
  color: #e74c3c;
}

.trade-date {
  text-align: center;
  color: #6c757d;
  font-size: 14px;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chart-section h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  text-align: center;
}

.chart-container {
  display: flex;
  justify-content: center;
  overflow-x: auto;
}

.chart-container canvas {
  border: 1px solid #ddd;
  border-radius: 8px;
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

.instructions {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.instructions h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.instructions ul {
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 20px;
}

.instructions li {
  margin-bottom: 8px;
}

.examples h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.example-codes {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.example {
  padding: 6px 12px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: monospace;
  font-size: 14px;
  color: #2c3e50;
  cursor: pointer;
  transition: background-color 0.3s;
}

.example:hover {
  background: #e9ecef;
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }
  
  .price-comparison {
    grid-template-columns: 1fr;
  }
  
  .stock-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .chart-container canvas {
    width: 100%;
    height: auto;
  }
}
</style> 