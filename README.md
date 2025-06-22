# 📈 股票分析系统

一个基于前后端分离架构的股票信息分析系统，提供实时市场数据、股票详情、市场统计等功能。

## 🚀 功能特性

- 📊 **市场统计分析** - 实时涨跌分布、市场情绪分析
- 📈 **高涨幅股票筛选** - 3年新高且涨幅超过7%的股票
- 🔍 **股票详情查询** - 个股基本信息、历史数据、今日最高价检查
- 📋 **股票列表浏览** - 支持分页、过滤、排序功能
- 🎨 **现代化UI** - 基于Vue3的响应式界面设计

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **Tushare** - 金融数据接口
- **Pandas** - 数据处理和分析

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 快速构建工具
- **Axios** - HTTP客户端
- **CSS Grid/Flexbox** - 响应式布局

## 📦 项目结构

```
gupiao/
├── backend/                 # 后端API服务
│   ├── main.py             # FastAPI主程序
│   ├── config.py           # 配置文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── api/           # API调用
│   │   └── App.vue        # 主应用组件
│   ├── package.json       # Node.js依赖
│   └── vite.config.js     # Vite配置
├── config.py              # 全局配置
├── requirements.txt       # 全局Python依赖
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/bluebeerboom/gupiao.git
cd gupiao
```

### 2. 配置Tushare Token
在 `config.py` 中设置你的Tushare Token：
```python
TUSHARE_TOKEN = "your_tushare_token_here"
```

### 3. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 4. 安装前端依赖
```bash
cd frontend
npm install
```

### 5. 启动服务

#### 启动后端API服务
```bash
cd backend
python main.py
```
后端服务将在 http://localhost:8000 运行

#### 启动前端开发服务器
```bash
cd frontend
npm run dev
```
前端应用将在 http://localhost:5173 运行

## 📖 API接口

### 市场分析
- `GET /api/market-analysis` - 获取市场统计分析数据

### 股票列表
- `GET /api/stocks` - 获取股票列表（支持分页、过滤、排序）

### 股票详情
- `GET /api/stock/{ts_code}` - 获取单个股票详细信息

### 高涨幅股票
- `GET /api/high-rise-stocks` - 获取3年新高且涨幅超过7%的股票

### 今日最高价检查
- `GET /api/is-highest-today/{ts_code}` - 检查股票是否为今日最高价

## 🎯 使用说明

1. **市场统计页面** - 查看整体市场涨跌分布和趋势
2. **股票列表页面** - 浏览所有股票，支持多种过滤条件
3. **股票详情页面** - 查看个股详细信息
4. **高涨幅股票页面** - 筛选符合条件的股票
5. **今日最高价检查** - 输入股票代码检查是否为今日最高价

## 🔧 开发说明

### 后端开发
- 使用FastAPI框架，支持自动API文档生成
- 访问 http://localhost:8000/docs 查看API文档
- 主要数据来源：Tushare金融数据接口

### 前端开发
- 基于Vue 3 Composition API
- 使用Vite作为构建工具
- 响应式设计，支持移动端

## 📝 更新日志

### v1.0.0
- ✅ 完成基础架构搭建
- ✅ 实现市场统计分析功能
- ✅ 实现股票列表和详情功能
- ✅ 实现高涨幅股票筛选功能
- ✅ 实现今日最高价检查功能
- ✅ 完成前后端分离架构
- ✅ 优化性能和用户体验

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。 