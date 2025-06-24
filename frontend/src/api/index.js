import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response  // 返回完整的response对象，不自动解包
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 股票相关API
export const stockAPI = {
  // 获取股票列表
  async getStocks(params) {
    const response = await api.get('/stocks', { params })
    return response.data
  },
  
  // 获取股票详情
  async getStockDetail(code) {
    const response = await api.get(`/stock/${code}`)
    return response.data
  },
  
  // 获取市场统计（查数据库）
  async getMarketStats() {
    const response = await api.get('/market_stats')
    return response.data
  },
  
  // 获取过滤选项
  async getFilters() {
    const response = await api.get('/filters')
    return response.data
  }
}

// 获取高涨幅创新高股票（查数据库）
export const getHighRiseStocks = async () => {
  try {
    const response = await api.get('/high_rise_stocks')
    return response.data
  } catch (error) {
    console.error('获取高涨幅股票失败:', error)
    throw error
  }
}

// 检查股票是否为今日最高价
export const checkIsHighestToday = async (tsCode) => {
  try {
    const response = await api.get(`/is-highest-today/${tsCode}`)
    return response.data
  } catch (error) {
    console.error('检查股票最高价失败:', error)
    throw error
  }
}

// 获取市场分析数据（查数据库）
export const getMarketAnalysis = async () => {
  try {
    const response = await api.get('/unified_market_analysis')
    return response.data
  } catch (error) {
    console.error('获取市场分析失败:', error)
    throw error
  }
}

// 获取涨跌分布分析（查数据库）
export const getRiseFallDistribution = async () => {
  try {
    const response = await api.get('/rise_fall_distribution')
    return response.data
  } catch (error) {
    console.error('获取涨跌分布失败:', error)
    throw error
  }
}

// 手动触发市场统计分析
export const refreshMarketStats = async () => {
  try {
    const response = await api.post('/refresh_market_stats')
    return response.data
  } catch (error) {
    console.error('刷新市场统计失败:', error)
    throw error
  }
}

// 手动触发高涨幅创新高分析
export const refreshHighRiseStocks = async () => {
  try {
    const response = await api.post('/refresh_high_rise_stocks')
    return response.data
  } catch (error) {
    console.error('刷新高涨幅分析失败:', error)
    throw error
  }
}

// 手动触发涨跌分布分析
export const refreshRiseFallDistribution = async () => {
  try {
    const response = await api.post('/refresh_rise_fall_distribution')
    return response.data
  } catch (error) {
    console.error('刷新涨跌分布分析失败:', error)
    throw error
  }
}

// 手动触发综合分析
export const refreshUnifiedMarketAnalysis = async () => {
  try {
    const response = await api.post('/refresh_unified_market_analysis')
    return response.data
  } catch (error) {
    console.error('刷新综合分析失败:', error)
    throw error
  }
}

export default api 