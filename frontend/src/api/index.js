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
  
  // 获取市场统计
  async getMarketStats() {
    const response = await api.get('/market-stats')
    return response.data
  },
  
  // 获取过滤选项
  async getFilters() {
    const response = await api.get('/filters')
    return response.data
  }
}

// 获取高涨幅创新高股票
export const getHighRiseStocks = async () => {
  try {
    const response = await api.get('/high-rise-stocks')
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

// 获取市场分析数据
export const getMarketAnalysis = async () => {
  try {
    const response = await api.get('/market-analysis')
    return response.data
  } catch (error) {
    console.error('获取市场分析失败:', error)
    throw error
  }
}

// 获取简化的市场统计数据（快速版本）
export const getMarketStatsSimple = async () => {
  try {
    const response = await api.get('/market-stats-simple')
    return response.data
  } catch (error) {
    console.error('获取简化市场统计失败:', error)
    throw error
  }
}

export default api 