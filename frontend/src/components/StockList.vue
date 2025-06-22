<template>
  <div class="stock-list">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>🔍 股票筛选</span>
          <el-button type="primary" @click="loadStocks" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      
      <el-form :model="filters" label-width="100px" inline>
        <el-form-item label="涨幅范围">
          <el-input-number 
            v-model="filters.min_rise" 
            placeholder="最小涨幅" 
            :precision="2"
            style="width: 120px"
          />
          <span style="margin: 0 10px">至</span>
          <el-input-number 
            v-model="filters.max_rise" 
            placeholder="最大涨幅" 
            :precision="2"
            style="width: 120px"
          />
        </el-form-item>
        
        <el-form-item label="价格范围">
          <el-input-number 
            v-model="filters.min_price" 
            placeholder="最低价格" 
            :precision="2"
            style="width: 120px"
          />
          <span style="margin: 0 10px">至</span>
          <el-input-number 
            v-model="filters.max_price" 
            placeholder="最高价格" 
            :precision="2"
            style="width: 120px"
          />
        </el-form-item>
        
        <el-form-item label="市场类型">
          <el-select v-model="filters.market" placeholder="选择市场" clearable style="width: 120px">
            <el-option label="深圳" value="SZ" />
            <el-option label="上海" value="SH" />
            <el-option label="北京" value="BJ" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序方式">
          <el-select v-model="filters.sort_by" style="width: 120px">
            <el-option label="涨幅" value="pct_chg" />
            <el-option label="价格" value="close" />
            <el-option label="成交量" value="vol" />
            <el-option label="成交额" value="amount" />
          </el-select>
          <el-select v-model="filters.sort_order" style="width: 80px; margin-left: 10px">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>📊 股票列表 ({{ tradeDate }})</span>
          <div class="header-actions">
            <el-select v-model="pageSize" @change="handlePageSizeChange" style="width: 100px">
              <el-option label="50条/页" :value="50" />
              <el-option label="100条/页" :value="100" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="stocks" 
        v-loading="loading"
        stripe
        @row-click="handleRowClick"
        style="width: 100%"
      >
        <el-table-column prop="ts_code" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="close" label="收盘价" width="100">
          <template #default="scope">
            <span class="price">¥{{ scope.row.close.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pct_chg" label="涨跌幅" width="120">
          <template #default="scope">
            <span :class="getPctChgClass(scope.row.pct_chg)">
              {{ scope.row.pct_chg > 0 ? '+' : '' }}{{ scope.row.pct_chg.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="vol" label="成交量(万)" width="120">
          <template #default="scope">
            {{ (scope.row.vol / 10000).toFixed(0) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="成交额(万)" width="120">
          <template #default="scope">
            {{ (scope.row.amount / 10000).toFixed(0) }}
          </template>
        </el-table-column>
        <el-table-column prop="area" label="地区" width="100" />
        <el-table-column prop="industry" label="行业" width="150" />
        <el-table-column prop="market" label="市场" width="80" />
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { stockAPI } from '../api'

export default {
  name: 'StockList',
  components: {
    Refresh
  },
  setup() {
    const router = useRouter()
    
    // 数据状态
    const stocks = ref([])
    const loading = ref(false)
    const tradeDate = ref('')
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(50)
    
    // 过滤条件
    const filters = reactive({
      min_rise: null,
      max_rise: null,
      min_price: null,
      max_price: null,
      market: '',
      sort_by: 'pct_chg',
      sort_order: 'desc'
    })
    
    // 加载股票数据
    const loadStocks = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          ...filters
        }
        
        console.log('发送请求参数:', params)
        const response = await stockAPI.getStocks(params)
        console.log('收到响应:', response)
        
        stocks.value = response.data
        total.value = response.pagination.total
        tradeDate.value = response.trade_date
        
        console.log('处理后的数据:', {
          stocks: stocks.value,
          total: total.value,
          tradeDate: tradeDate.value
        })
      } catch (error) {
        console.error('加载股票数据失败:', error)
        ElMessage.error('加载股票数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 应用筛选
    const applyFilters = () => {
      currentPage.value = 1
      loadStocks()
    }
    
    // 重置筛选
    const resetFilters = () => {
      Object.keys(filters).forEach(key => {
        if (key === 'sort_by' || key === 'sort_order') {
          filters[key] = key === 'sort_by' ? 'pct_chg' : 'desc'
        } else {
          filters[key] = null
        }
      })
      currentPage.value = 1
      loadStocks()
    }
    
    // 分页处理
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadStocks()
    }
    
    const handlePageSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadStocks()
    }
    
    // 行点击事件
    const handleRowClick = (row) => {
      router.push(`/stock/${row.ts_code}`)
    }
    
    // 获取涨跌幅样式
    const getPctChgClass = (pctChg) => {
      if (pctChg > 0) return 'rise'
      if (pctChg < 0) return 'fall'
      return 'flat'
    }
    
    onMounted(() => {
      loadStocks()
    })
    
    return {
      stocks,
      loading,
      tradeDate,
      total,
      currentPage,
      pageSize,
      filters,
      loadStocks,
      applyFilters,
      resetFilters,
      handleCurrentChange,
      handlePageSizeChange,
      handleRowClick,
      getPctChgClass
    }
  }
}
</script>

<style scoped>
.stock-list {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
}

.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-wrapper {
  margin-top: 20px;
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

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}
</style> 