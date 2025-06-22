<template>
  <div class="stock-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="$router.go(-1)" icon="ArrowLeft">返回</el-button>
          <span v-if="stock.name">{{ stock.name }} ({{ stock.ts_code }})</span>
        </div>
      </template>
      
      <div v-if="stock.ts_code" class="detail-content">
        <!-- 基本信息 -->
        <el-row :gutter="20" class="info-section">
          <el-col :span="12">
            <el-descriptions title="基本信息" :column="1" border>
              <el-descriptions-item label="股票代码">{{ stock.ts_code }}</el-descriptions-item>
              <el-descriptions-item label="股票名称">{{ stock.name }}</el-descriptions-item>
              <el-descriptions-item label="所属地区">{{ stock.area }}</el-descriptions-item>
              <el-descriptions-item label="所属行业">{{ stock.industry }}</el-descriptions-item>
              <el-descriptions-item label="市场类型">{{ stock.market }}</el-descriptions-item>
              <el-descriptions-item label="上市日期">{{ stock.list_date }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          
          <el-col :span="12">
            <el-descriptions title="交易数据" :column="1" border>
              <el-descriptions-item label="交易日期">{{ stock.trade_date }}</el-descriptions-item>
              <el-descriptions-item label="收盘价">
                <span class="price">¥{{ stock.close?.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="开盘价">¥{{ stock.open?.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="最高价">¥{{ stock.high?.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="最低价">¥{{ stock.low?.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="涨跌幅">
                <span :class="getPctChgClass(stock.pct_chg)">
                  {{ stock.pct_chg > 0 ? '+' : '' }}{{ stock.pct_chg?.toFixed(2) }}%
                </span>
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        
        <!-- 成交信息 -->
        <el-row :gutter="20" class="info-section">
          <el-col :span="24">
            <el-descriptions title="成交信息" :column="3" border>
              <el-descriptions-item label="成交量">
                {{ (stock.vol / 10000).toFixed(0) }} 万股
              </el-descriptions-item>
              <el-descriptions-item label="成交额">
                {{ (stock.amount / 10000).toFixed(0) }} 万元
              </el-descriptions-item>
              <el-descriptions-item label="换手率">
                {{ ((stock.vol / 10000) / 100).toFixed(2) }}%
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        
        <!-- 价格走势图 -->
        <div v-if="stock.history && stock.history.length > 0" class="chart-section">
          <h3>📈 近30日价格走势</h3>
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </div>
      
      <div v-else-if="!loading" class="no-data">
        <el-empty description="未找到股票信息" />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { stockAPI } from '../api'
import * as echarts from 'echarts'

export default {
  name: 'StockDetail',
  components: {
    ArrowLeft
  },
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const stock = reactive({})
    const chartRef = ref(null)
    let chart = null
    
    // 加载股票详情
    const loadStockDetail = async () => {
      loading.value = true
      try {
        const code = route.params.code
        const data = await stockAPI.getStockDetail(code)
        Object.assign(stock, data)
        
        // 等待DOM更新后初始化图表
        await nextTick()
        if (stock.history && stock.history.length > 0) {
          initChart()
        }
      } catch (error) {
        ElMessage.error('加载股票详情失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    // 初始化图表
    const initChart = () => {
      if (!chartRef.value) return
      
      chart = echarts.init(chartRef.value)
      
      const history = stock.history.reverse() // 按时间正序
      const dates = history.map(item => item.date)
      const prices = history.map(item => item.close)
      const volumes = history.map(item => item.vol / 10000) // 转换为万股
      
      const option = {
        title: {
          text: `${stock.name} 价格走势图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['收盘价', '成交量'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '价格(元)',
            position: 'left'
          },
          {
            type: 'value',
            name: '成交量(万股)',
            position: 'right'
          }
        ],
        series: [
          {
            name: '收盘价',
            type: 'line',
            data: prices,
            yAxisIndex: 0,
            itemStyle: {
              color: '#409eff'
            },
            lineStyle: {
              width: 2
            }
          },
          {
            name: '成交量',
            type: 'bar',
            data: volumes,
            yAxisIndex: 1,
            itemStyle: {
              color: '#67c23a',
              opacity: 0.6
            }
          }
        ]
      }
      
      chart.setOption(option)
    }
    
    // 获取涨跌幅样式
    const getPctChgClass = (pctChg) => {
      if (pctChg > 0) return 'rise'
      if (pctChg < 0) return 'fall'
      return 'flat'
    }
    
    onMounted(() => {
      loadStockDetail()
    })
    
    return {
      loading,
      stock,
      chartRef,
      loadStockDetail,
      getPctChgClass
    }
  }
}
</script>

<style scoped>
.stock-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.detail-content {
  padding: 20px 0;
}

.info-section {
  margin-bottom: 30px;
}

.chart-section {
  margin-top: 30px;
}

.chart-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.no-data {
  padding: 60px 0;
  text-align: center;
}

.price {
  font-weight: bold;
  color: #409eff;
}

.rise {
  color: #f56c6c;
  font-weight: bold;
}

.fall {
  color: #67c23a;
  font-weight: bold;
}

.flat {
  color: #909399;
}
</style> 